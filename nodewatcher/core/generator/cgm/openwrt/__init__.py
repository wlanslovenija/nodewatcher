from django.utils.translation import ugettext as _

from nodewatcher.core.registry.cgm import base as cgm_base

class UCISection(object):
    """
    Represents a configuration section in UCI.
    """
    def __init__(self, typ = None):
        """
        Class constructor.
        """
        self.__dict__['_typ'] = typ
        self.__dict__['_values'] = {}

    def __setattr__(self, name, value):
        """
        Sets a configuration attribute.
        """
        self._values[name] = value

    def __delattr__(self, name):
        """
        Deletes a configuration attribute.
        """
        del self._values[name]

    def __getattr__(self, name):
        """
        Returns a configuration attribute's value.
        """
        return self._values.get(name, None)

    def get_type(self):
        """
        Returns the section type name.
        """
        return self._typ

    def format_value(self, value):
        """
        Formats a value so it is suitable for insertion into UCI.
        """
        if isinstance(value, (list, tuple)):
            return " ".join(self.format_value(x) for x in value)
        elif isinstance(value, bool):
            return int(value)

        return str(value)

    def format(self, root, section, idx = None):
        """
        Formats the configuration tree so it is suitable for loading into UCI.
        """
        output = []

        if self._typ is not None:
            # Named sections
            output.append("{0}.{1}={2}".format(root, section, self._typ))
            for key, value in self._values.iteritems():
                if key.startswith('_'):
                    continue
                output.append("{0}.{1}.{2}={3}".format(root, section, key, self.format_value(value)))
        else:
            # Ordered sections
            output.append("{0}.@{1}[{2}]={1}".format(root, section, idx))
            for key, value in self._values.iteritems():
                if key.startswith('_'):
                    continue
                output.append("{0}.@{1}[{2}].{3}={4}".format(root, section, idx, key, self.format_value(value)))

        return output

class UCIRoot(object):
    """
    Represents an UCI configuration file with multiple named and ordered
    sections.
    """
    def __init__(self, root):
        """
        Class constructor.

        @param root: Root name
        """
        self._root = root
        self._named_sections = {}
        self._ordered_sections = {}

    def add(self, *args, **kwargs):
        """
        Creates a new UCI section. An ordered section should be specified by using
        a single argument and a named section by using a single keyword argument.

        @return: The newly created UCISection
        """
        if len(args) > 1 or len(kwargs) > 1 or len(args) == len(kwargs):
            raise ValueError

        if kwargs:
            # Adding a named section
            section_key = kwargs.values()[0]
            section = UCISection(typ = kwargs.keys()[0])

            # Check for duplicates to avoid screwing up existing lists and sections
            if section_key in self._named_sections:
                raise ValueError, "UCI section '{0}' is already defined!".format(section_key)

            self._named_sections[section_key] = section
        else:
            # Adding an ordered section
            section = UCISection()
            self._ordered_sections.setdefault(args[0], []).append(section)

        return section

    def __iter__(self):
        return iter(self._named_sections.iteritems())

    def __contains__(self, section):
        return section in self._named_sections or  section in self._ordered_sections

    def __getattr__(self, section):
        """
        Retrieves the wanted UCI section.
        """
        try:
            return self._named_sections[section]
        except KeyError:
            return self._ordered_sections[section]

    def format(self):
        """
        Formats the configuration tree so it is suitable for loading into UCI.
        """
        output = []
        for name, section in self._named_sections.iteritems():
            output += section.format(self._root, name)

        for name, sections in self._ordered_sections.iteritems():
            for idx, section in enumerate(sections):
                output += section.format(self._root, name, idx)

        return output

class UCIConfiguration(cgm_base.PlatformConfiguration):
    """
    An in-memory implementation of UCI configuration.
    """
    def __init__(self):
        """
        Class constructor.
        """
        super(UCIConfiguration, self).__init__()
        self._roots = {}

    def __getattr__(self, root):
        """
        Returns the desired UCI root (config file).
        """
        return self._roots.setdefault(root, UCIRoot(root))

    def format(self):
        """
        Formats the configuration tree so it is suitable for loading into UCI.
        """
        output = []
        for name, root in self._roots.iteritems():
            output += root.format()

        return output

class PlatformOpenWRT(cgm_base.PlatformBase):
    """
    OpenWRT platform descriptor.
    """
    config_class = UCIConfiguration

    def format(self, cfg):
        """
        Formats the concrete configuration so that it is suitable for
        inclusion directly into the firmware image.

        :param cfg: Generated configuration (platform-dependent)
        :return: Platform-dependent object
        """
        # TODO Split UCI configuration into files, return a dictionary
        #      containing a mapping from file names to their contents
        raise NotImplementedError

    def build(self, formatted_cfg):
        """
        Builds the firmware using a previously generated and properly
        formatted configuration.

        :param formatted_cfg: Formatted configuration (platform-dependent)
        :return: Build process result
        """
        # TODO Setup the image builder fraemwork, write the formatted
        #      configuration to the filesystem, use the proper builder
        #      profile and build the firmware

        # TODO How to define build profile? Modules should probably specify
        #      that somehow (a special UCI configuration package called "build"?)
        raise NotImplementedError

cgm_base.register_platform("openwrt", _("OpenWRT"), PlatformOpenWRT())

# Load all model-specific modules
import nodewatcher.core.generator.cgm.openwrt.fon
import nodewatcher.core.generator.cgm.openwrt.linksys
import nodewatcher.core.generator.cgm.openwrt.buffalo
import nodewatcher.core.generator.cgm.openwrt.mikrotik
import nodewatcher.core.generator.cgm.openwrt.asus
import nodewatcher.core.generator.cgm.openwrt.tplink
