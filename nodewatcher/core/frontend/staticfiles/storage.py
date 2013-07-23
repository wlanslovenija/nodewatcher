import fnmatch
import os

from django.contrib.staticfiles import storage
from django.core.files import base
from django.utils import encoding
from django.conf import settings

import scss


def relative_path(root, path):
    """Returns the path of a file relative to the root."""
    root = os.path.abspath(root)
    path = os.path.abspath(path)
    assert path.startswith(root)
    relative = path[len(root):]
    if relative.startswith(os.sep):
        return relative[1:]
    else:
        return relative


class SCSSFilesMixin(object):
    def __init__(self, *args, **kwargs):
        super(SCSSFilesMixin, self).__init__(*args, **kwargs)

        # ASSETS_ROOT is where the pyScss outputs the generated files such
        # as spritemaps and compile cache
        # TODO: This should be improved if some non-local-filesystem storage is used for static files
        scss.config.ASSETS_ROOT = os.path.join(settings.STATIC_ROOT, 'nodewatcher', 'assets')
        scss.config.ASSETS_URL = settings.STATIC_URL + 'nodewatcher/assets/'

        scss.config.STATIC_ROOT = settings.STATIC_ROOT
        scss.config.STATIC_URL = settings.STATIC_URL

        self._scss_paths = []
        self._scss_paths.extend(getattr(settings, 'SCSS_PATHS', []))

        # _scss_vars hold the context variables
        self._scss_vars = {}
        # This creates the Scss object used to compile SCSS code
        self._scss = scss.Scss(
            scss_vars=self._scss_vars,
            scss_opts={
                'compress': not settings.DEBUG,
                'debug_info': settings.DEBUG,
            }
        )

    def _scss_process(self, filename, file):
        root, name = os.path.split(os.path.join(settings.STATIC_ROOT, filename))
        scss.config.LOAD_PATHS = []
        scss.config.LOAD_PATHS.extend(self._scss_paths)
        scss.config.LOAD_PATHS.append(root)

        return self._scss.compile(file.read())

    def post_process(self, paths, dry_run=False, **options):
        """
        Post process the given list of files (called from collectstatic).

        Processing finds all SCSS files (*.scss, not starting with ``_``) and
        compiles them into CSS files and afterwards deletes them.
        """

        # Don't even dare to process the files if we're in dry run mode
        if dry_run:
            return

        # Build a list of SCSS files
        all_scss_files = [path for path in paths if fnmatch.fnmatchcase(path, '*.scss')]

        # Then sort the files by the directory level
        path_level = lambda name: len(name.split(os.sep))
        for name in sorted(all_scss_files, key=path_level, reverse=True):
            if os.path.basename(name).startswith('_'):
                yield name, None, False
                continue

            output_filename = os.path.splitext(name)[0] + '.css'

            # Use the original, local file, not the copied-but-unprocessed
            # file, which might be somewhere far away, like S3
            storage, path = paths[name]
            with storage.open(path) as original_file:
                if hasattr(original_file, 'seek'):
                    original_file.seek(0)

                output = self._scss_process(name, original_file)

                if self.exists(output_filename):
                    self.delete(output_filename)

                output_file = base.ContentFile(encoding.smart_str(output))
                saved_name = self._save(output_filename, output_file)
                saved_name = encoding.force_unicode(saved_name.replace('\\', '/'))

                yield name, saved_name, True

        # Deletes all SCSS files
        for name in sorted(all_scss_files, key=path_level, reverse=True):
            if self.exists(name):
                self.delete(name)
                yield name, '<deleted>', True


class SCSSStaticFilesStorage(SCSSFilesMixin, storage.StaticFilesStorage):
    """
    A static file system storage backend which post-processes SCSS files.
    """

    pass
