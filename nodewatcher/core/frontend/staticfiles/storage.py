import fnmatch
import os
import types
import tempfile
import shutil

from django.contrib.staticfiles import storage
from django.core.files import base
from django.utils import encoding
from django.conf import settings

import scss
from nodewatcher.extra import fonticons


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


class StaticFilesProcessor(object):

    def __init__(self):
        pass

    def initialize(self, storage):
        pass

    def deinitialize(self, storage):
        pass

    def match(self, filepath):
        return False

    def process(self, filepath, storage):
        return filename, None, False


class SCSSFilesProcessor(StaticFilesProcessor):

    """
        Processor finds all SCSS files (*.scss, not starting with ``_``) and
        compiles them into CSS files and afterwards deletes them.
    """

    def __init__(self):
        # ASSETS_ROOT is where the pyScss outputs the generated files such
        # as spritemaps and compile cache
        # TODO: This should be improved if some non-local-filesystem storage is
        # used for static files
        scss.config.ASSETS_ROOT = os.path.join(
            settings.STATIC_ROOT, 'nodewatcher', 'assets')
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

    def initialize(self, storage):
        pass

    def deinitialize(self, storage):
        pass

    def match(self, filename):
        return fnmatch.fnmatchcase(filename, '*.scss')

    def process(self, filename, container, storage):
        if os.path.basename(filename).startswith('_'):
            return None, False, True

        output_filename = os.path.splitext(filename)[0] + '.css'

        with container.open(filename) as original_file:
            if hasattr(original_file, 'seek'):
                original_file.seek(0)

            output = self._scss_process(filename, original_file)

            if storage.exists(output_filename):
                storage.delete(output_filename)

            output_file = base.ContentFile(encoding.smart_str(output))
            saved_name = storage._save(output_filename, output_file)
            saved_name = encoding.force_unicode(saved_name.replace('\\', '/'))

            return saved_name, True, True

    def _scss_process(self, filename, file):
        root, name = os.path.split(
            os.path.join(settings.STATIC_ROOT, filename))
        scss.config.LOAD_PATHS = []
        scss.config.LOAD_PATHS.extend(self._scss_paths)
        scss.config.LOAD_PATHS.append(root)

        return self._scss.compile(file.read())


class FontFilesProcessor(StaticFilesProcessor):

    def __init__(self):
        self.fontname = 'nodewatcher'
        self.cssprefix = 'nw'
        self.cssname = 'icons.css'

        self.fontpath = 'frontend/fonts'
        self.csspath = 'frontend/css'
        self.fonturl = settings.STATIC_URL + 'frontend/fonts/'

    def initialize(self, storage):
        self._font = fonticons.FontIcons(self.fontname)
        self._links = {}

    def deinitialize(self, storage):
        for link, glyph in self._links.items():
            self._font.addName(glyph, [link])

        tmpdir = tempfile.mkdtemp()
        files = self._font.exportFont(tmpdir)
        for f in files:
            output_filename = os.path.join(self.fontpath, os.path.split(f)[1])
            if storage.exists(output_filename):
                storage.delete(output_filename)
            output_file = base.File(open(f, 'r'))
            saved_name = storage._save(output_filename, output_file)
            yield saved_name

        files = self._font.exportCSS(
            tmpdir, name='icons.css', prefix='nw', fonturl=self.fonturl)
        for f in files:
            output_filename = os.path.join(self.csspath, os.path.split(f)[1])
            if storage.exists(output_filename):
                storage.delete(output_filename)
            output_file = base.File(open(f, 'r'))
            saved_name = storage._save(output_filename, output_file)
            yield saved_name

        shutil.rmtree(tmpdir)

    def match(self, filename):
        if not (os.path.basename(os.path.dirname(filename)) == 'icons'):
            return False
        return (fnmatch.fnmatchcase(filename, '*.svg') or
                fnmatch.fnmatchcase(filename, '*.icon'))

    def process(self, filename, container, storage):
        (iconname, filetype) = os.path.splitext(os.path.basename(filename))

        with container.open(filename) as original_file:
            if hasattr(original_file, 'seek'):
                original_file.seek(0)

            data = original_file.read()

            if filetype == '.svg':
                self._font.addGlyph(iconname, fonticons.SVGDocumentGlyph(data))
                self._font.addName(iconname, [iconname])
            elif filetype == '.icon':
                # TODO: validate name
                self._links[iconname] = data.strip()

            return filename, True, True

    def _scss_process(self, filename, file):
        root, name = os.path.split(
            os.path.join(settings.STATIC_ROOT, filename))
        scss.config.LOAD_PATHS = []
        scss.config.LOAD_PATHS.extend(self._scss_paths)
        scss.config.LOAD_PATHS.append(root)

        return self._scss.compile(file.read())


class FilesProcessorMixin(object):

    def __init__(self, *args, **kwargs):
        super(FilesProcessorMixin, self).__init__(*args, **kwargs)

        self._processors = {
            SCSSFilesProcessor(),
            FontFilesProcessor()
        }

    def _filter(self, filename):
        for processor in self._processors:
            if processor.match(filename):
                return processor
        return None

    def post_process(self, paths, dry_run=False, **options):
        """
        Post process the given list of files (called from collectstatic).
        """

        # Don't even dare to process the files if we're in dry run mode
        if dry_run:
            return

        for processor in self._processors:
            files = processor.initialize(self)
            if isinstance(files, types.GeneratorType):
                for f in files:
                    yield '<prepend>', f, True

        # Build a list of SCSS files
        all_files = [(path, self._filter(path)) for path in paths]
        all_process_files = [e for e in all_files if e[1]]
        all_deleted_files = []

        # Then sort the files by the directory level
        path_level = lambda name: len(name[0].split(os.sep))
        for e in sorted(all_process_files, key=path_level, reverse=True):
            storage, path = paths[e[0]]
            saved_name, processed, delete = e[1].process(path, storage, self)
            yield e[0], saved_name, processed
            if delete:
                all_deleted_files.append(e)

        for processor in self._processors:
            files = processor.deinitialize(self)
            if isinstance(files, types.GeneratorType):
                for f in files:
                    yield '<append>', f, True

        for e in sorted(all_deleted_files, key=path_level, reverse=True):
            if self.exists(e[0]):
                self.delete(e[0])
                yield e[0], '<deleted>', True


class FilesProcessorStorage(FilesProcessorMixin, storage.StaticFilesStorage):

    """
    A static file system storage backend which post-processes SCSS files.
    """

    pass
