import fnmatch, os

from django.contrib.staticfiles import storage
from django.core.files import base
from django.utils import encoding

class SCSSFilesMixin(object):
    def __init__(self, *args, **kwargs):
        super(SCSSFilesMixin, self).__init__(*args, **kwargs)

        # TODO: Implement

    def _scss_process(self, filename, file):
        # TODO: Implement
        return ''

    def post_process(self, paths, dry_run=False, **options):
        """
        Post process the given list of files (called from collectstatic).

        Processing finds all SCSS files (*.scss, not starting with ``_``) and
        compiles them into CSS files and afterwards deletes them. Furthermore, it
        deletes all files which have in their path any directory starting with ``_``.
        """

        # Don't even dare to process the files if we're in dry run mode
        if dry_run:
            return

        # Build a list of SCSS files
        all_scss_files = [path for path in paths if fnmatch.fnmatchcase(path, '*.scss')]

        #Tthen sort the files by the directory level
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

        # Deletes all files which have in their path any directory starting with ``_``
        for name in sorted(paths.keys(), key=path_level, reverse=True):
            for part in name.split(os.sep):
                if part.startswith('_'):
                    if self.exists(name):
                        self.delete(name)
                        yield name, '<deleted>', True

class SCSSStaticFilesStorage(SCSSFilesMixin, storage.StaticFilesStorage):
    """
    A static file system storage backend which post-processes SCSS files.
    """

    pass
