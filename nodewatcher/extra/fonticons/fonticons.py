
import os
import time
from sets import Set
import subprocess

# apt-get install ttfautohint eot-utils python-scour

import fontforge
import tempfile

TTF_SUFFIX = '.ttf'
WOFF_SUFFIX = '.woff'
SVG_SUFFIX = '.svg'
EOT_SUFFIX = '.eot'

CHARACTER_ALLOCATION_START = 0xF0000
CHARACTER_ALLOCATION_END = 0xFFFFD

def maybe_gziped_file(filename, mode="r"):
    if os.path.splitext(filename)[1].lower() in (".svgz", ".gz"):
        import gzip
        return gzip.GzipFile(filename, mode)
    return file(filename, mode)

class IconGlyph(object):
    def __init__(self):
        pass

    def export(self, glyph):
        pass

class SVGPathGlyph(IconGlyph):
    def __init__(self, paths, width=1024, height=1024):
        self._paths = paths
        self._width = width
        self._height = height

    def export(self, glyph):

        fp, svgtmp = tempfile.mkstemp(suffix=SVG_SUFFIX)

        svg = '<?xml version="1.0" encoding="utf-8"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">'
        svg = svg + '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="%d" height="%d" viewBox="0 0 %d %d">' % (self._width, self._height, self._width, self._height)
        for p in self._paths:
            svg = svg + '<path d="%s"></path>' % p
        svg = svg + "</svg>"

        os.write(fp, svg)
        os.close(fp)

        glyph.importOutlines(svgtmp)
        os.unlink(svgtmp)

        # make the glyph rest on the baseline
        ymin = glyph.boundingBox()[1]
        glyph.transform([1, 0, 0, 1, 0, -ymin])
        # set glyph side bearings, can be any value or even 0
        glyph.left_side_bearing = glyph.right_side_bearing = 10

class SVGFileGlyph(IconGlyph):
    def __init__(self, svgfile):
        self._file = svgfile

    def export(self, glyph):

        glyph.importOutlines(self._svgfile)
        os.unlink(svgtmp)

        # make the glyph rest on the baseline
        ymin = glyph.boundingBox()[1]
        glyph.transform([1, 0, 0, 1, 0, -ymin])
        # set glyph side bearings, can be any value or even 0
        glyph.left_side_bearing = glyph.right_side_bearing = 10

class SVGDocumentGlyph(IconGlyph):
    def __init__(self, data):
        self._data = data

    def export(self, glyph):
        fp, svgtmp = tempfile.mkstemp(suffix=SVG_SUFFIX)
        os.write(fp, self._data)
        os.close(fp)
        glyph.importOutlines(svgtmp)
        os.unlink(svgtmp)
        ymin = glyph.boundingBox()[1]
        glyph.transform([1, 0, 0, 1, 0, -ymin])
        glyph.left_side_bearing = glyph.right_side_bearing = 10

class FontIcons(object):
    def __init__(self, identifier, name=None):
        self._name = name if name else identifier
        self._identifier = identifier
        self._icons = {}
        self._characters = {}

    def addGlyph(self, identifier, glyph, character = None):
        if identifier in self._icons:
            raise KeyError("Identifier already used")

        if not character:
            for c in xrange(CHARACTER_ALLOCATION_START, CHARACTER_ALLOCATION_END):
                if not c in self._characters:
                    character = c
                    break

        if character in self._characters:
            raise KeyError("Character already used")

        self._icons[identifier] = {'glyph': glyph, 'character': character, 'names': Set([])}
        self._characters[character] = identifier

    def addName(self, identifier, name):
        if not identifier in self._icons:
            return
        self._icons[identifier]['names'].update(Set(name))


    def delName(self, identifier, name):
        if not identifier in self._icons:
            return
        self._icons[identifier]['names'].difference_update(Set(name))

    def export(self, directory='.'):
        fontfiles = self.exportFont(directory)
        cssfiles = self.exportCSS(directory)
        return fontfiles + cssfiles

    def exportFont(self, directory='.', ttfonly=False):

        files = []

        font = fontforge.font()

        font.fontname = self._identifier
        font.fullname = self._name
        font.familyname = self._name

        for identifier, icon in self._icons.items():
            print "Exporting glyph '%s' for character '%s'" % (identifier, hex(icon['character']))
            icon['glyph'].export(font.createChar(icon['character']))

        #fp, ttftmp = tempfile.mkstemp(suffix=TTF_SUFFIX)
        #os.close(fp)
        print "Exporting TTF font ..."
        font.generate(os.path.join(directory, self._identifier + TTF_SUFFIX))
        files.append(os.path.join(directory, self._identifier + TTF_SUFFIX))
        #print "Optimizing TTF font ..."
        #subprocess.call(['ttfautohint', '-s', '-v', ttftmp, os.path.join(directory, self._identifier + TTF_SUFFIX)])

        if not ttfonly:

            print "Exporting EOT font ..."
            fd = os.open(os.path.join(directory, self._identifier + EOT_SUFFIX), os.O_WRONLY|os.O_CREAT)
            subprocess.call(['mkeot', os.path.join(directory, self._identifier + TTF_SUFFIX)], stdout=fd)
            os.close(fd)
            files.append(os.path.join(directory, self._identifier + EOT_SUFFIX))

            print "Exporting WOFF font ..."
            font.generate(os.path.join(directory, self._identifier + WOFF_SUFFIX))
            files.append(os.path.join(directory, self._identifier + WOFF_SUFFIX))
            print "Exporting SVG font ..."
            font.generate(os.path.join(directory, self._identifier + SVG_SUFFIX))
            files.append(os.path.join(directory, self._identifier + SVG_SUFFIX))
         
            try:
                import scour

                print "Optimizing SVG font ..."
                options, rargs = scour_options_parser.parse_args([])
                svgin = maybe_gziped_file(os.path.join(directory, self._identifier + SVG_SUFFIX))
                in_string = svgin.read()
                svgin.close()
                out_string = scour.scourString(in_string, options).encode("UTF-8")
                svgout = maybe_gziped_file(os.path.join(directory, self._identifier + SVG_SUFFIX), mode='w')
                svgout.write(out_string)
                svgout.close()

            except:
                print "Unable to clean up SVG, install scour library"

        return files

    def exportCSS(self, directory='.', name=None, prefix=None, fonturl=''):

        if not name:
            name = self._identifier + '.css'

        if not prefix:
            prefix = self._identifier

        font = self._identifier
        cachebreaker = str(time.time())
        cssfile = os.path.join(directory, name)
        fp = open(cssfile, 'w')

        fp.write("@font-face {")
        fp.write("font-family: '%s';" % font)
        fp.write("src:url('%s%s.eot?-88h4nb');" % (fonturl, font))
        fp.write("src:url('%s%s.eot?#%s') format('embedded-opentype')," % (fonturl, font, cachebreaker))
        fp.write("url('%s%s.ttf?-%s') format('truetype')," % (fonturl, font, cachebreaker))
        fp.write("url('%s%s.woff?-%s') format('woff')," % (fonturl, font, cachebreaker))
        fp.write("url('%s%s.svg?-%s#%s') format('svg');" % (fonturl, font, cachebreaker, font))
        fp.write("font-weight: normal;")
        fp.write("font-style: normal;")
        fp.write("} \n\n")

        fp.write(".%s {" % prefix)
        fp.write("font-family: '%s';" % font)
        fp.write("speak: none;")
        fp.write("font-style: normal;")
        fp.write("font-weight: normal;")
        fp.write("font-variant: normal;")
        fp.write("text-transform: none;")
        fp.write("line-height: 1;")
        fp.write("-webkit-font-smoothing: antialiased;")
        fp.write("-moz-osx-font-smoothing: grayscale;")
        fp.write("}\n")

        for identifier, icon in self._icons.items():
            for name in icon["names"]:
                fp.write(".%s-%s:before {" % (prefix, name))
                fp.write("content: '\%s';" % hex(icon['character'])[2:])
                fp.write("}\n")

        fp.close()

        return [cssfile]
