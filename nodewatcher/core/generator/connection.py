import hashlib
import io
import os
import paramiko
import pipes
import socket

from . import exceptions
from .cgm import exceptions as cgm_exceptions

BUILDER_PATH = '/builder/imagebuilder'


class BuilderConnection(object):
    """
    Connection with the builder.
    """

    def __init__(self, builder):
        """
        Class constructor.

        :param builder: Builder configuration object
        """

        self.builder = builder
        self.tempdirs = []

    def __enter__(self):
        """
        Establishes a connection with the builder.
        """

        # Load private key (detect RSA or DSS)
        try:
            pkey = paramiko.RSAKey.from_private_key(io.StringIO(self.builder.private_key))
        except paramiko.SSHException:
            # Not a RSA key, try to decode the key as a DSS key
            try:
                pkey = paramiko.DSSKey.from_private_key(io.StringIO(self.builder.private_key))
            except paramiko.SSHException:
                raise exceptions.MalformedPrivateKey

        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(
                hostname=self.builder.host,
                username='builder',
                pkey=pkey,
            )
            transport = self.client.get_transport()
            transport.set_keepalive(60)
            self.sftp = transport.open_sftp_client()
        except (paramiko.SSHException, paramiko.SFTPError, socket.error):
            raise exceptions.BuilderConnectionFailed

        return self

    def __exit__(self, *args):
        """
        Cleans up any temporary resources and closes the connection.
        """

        # Cleanup temporary directories
        for tmpdir in self.tempdirs:
            self.client.exec_command('rm -rf %s' % tmpdir)

        self.client.close()

    def create_tempdir(self):
        """
        Creates a remote temporary directory.
        """

        dirname = os.path.join('/tmp', hashlib.md5(os.urandom(16)).hexdigest()[:16])
        try:
            self.sftp.mkdir(dirname)
        except IOError:
            raise cgm_exceptions.BuildError('Failed to create temporary directory.')

        self.tempdirs.append(dirname)
        return dirname

    def write_file(self, path, content, mode=None):
        """
        Creates a file with specific content on the builder.

        :param path: File path
        :param content: File content
        :param mode: File mode
        """

        # Ensure that all directories leading up to the file are created
        components = os.path.dirname(path).split('/')[1:]
        for idx, component in enumerate(components):
            try:
                self.sftp.mkdir('/%s' % os.path.join('/'.join(components[:idx]), component))
            except IOError:
                pass

        # Write the file
        try:
            with self.sftp.open(path, 'w') as fobj:
                fobj.write(content)

            if mode is not None:
                self.sftp.chmod(path, mode)
        except IOError:
            raise cgm_exceptions.BuildError('Failed to write file: %s' % path)

    def chmod(self, path, mode):
        """
        Changes the permissions of a file.

        :param path: File path
        :param mode: New permissions
        """

        try:
            self.sftp.chmod(path, mode)
        except IOError:
            raise cgm_exceptions.BuildError('Failed to chmod file: %s' % path)

    def call(self, *args, **kwargs):
        """
        Executes a builder command.

        :param quote: Should the arguments be quoted
        """

        if kwargs.get('quote', True):
            args = [pipes.quote(arg) for arg in args]

        try:
            cmd = [
                'cd %s;' % BUILDER_PATH,
                " ".join(args),
                "2>&1",
            ]

            stdin, stdout, stderr = self.client.exec_command(" ".join(cmd))
            build_log = "\n".join(stdout.readlines())

            if stdout.channel.recv_exit_status() != 0:
                raise cgm_exceptions.BuildError(build_log)

            return build_log
        except paramiko.SSHException:
            raise cgm_exceptions.BuildError('Unknown error on builder.')

    def list_dir(self, path):
        """
        Returns a directory listing.

        :param path: Path relative to the builder directory
        """

        return self.sftp.listdir(os.path.join(BUILDER_PATH, path))

    def read_result_file(self, path):
        """
        Reads a result file.

        :param path: Path relative to the builder directory
        """

        with self.sftp.open(os.path.join(BUILDER_PATH, path), 'r') as fobj:
            return fobj.read()
