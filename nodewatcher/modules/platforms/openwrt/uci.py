import collections
import re

# Allowed characters for UCI identifiers.
UCI_IDENTIFIER = re.compile(r'^[a-zA-Z0-9_]+$')
UCI_IDENTIFIER_REPLACE = re.compile(r'[^a-zA-Z0-9_]')
UCI_PACKAGE_IDENTIFIER = re.compile(r'^[a-zA-Z0-9_-]+$')


class UCIFormat:
    """
    Available UCI export formats.
    """

    # UCI dump
    DUMP = 1
    # UCI in multiple files
    FILES = 2


class UCISection(object):
    """
    Represents a configuration section in UCI.
    """

    def __init__(self, key=None, typ=None, managed_by=None):
        """
        Class constructor.
        """

        if not isinstance(managed_by, list):
            managed_by = [managed_by]

        self.__dict__['_key'] = key
        self.__dict__['_typ'] = typ
        self.__dict__['_managed_by'] = managed_by
        self.__dict__['_values'] = collections.OrderedDict()

    def __setattr__(self, name, value):
        """
        Sets a configuration attribute.
        """

        if not name.startswith('_') and not UCI_IDENTIFIER.match(name):
            raise ValueError("Invalid UCI identifier '%s'." % name)

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

        if name.startswith('__') and name.endswith('__'):
            raise AttributeError(name)

        return self._values.get(name, None)

    __setitem__ = __setattr__
    __delitem__ = __delattr__
    __getitem__ = __getattr__

    def get_key(self):
        """
        Returns the section key.
        """

        return self._key

    def get_type(self):
        """
        Returns the section type name.
        """

        return self._typ

    def get_manager(self, klass=None):
        """
        Returns a manager object in case one has been set when adding this
        piece of configuration.
        """

        if not self._managed_by:
            return None

        for manager in self._managed_by:
            if klass is None or isinstance(manager, klass):
                return manager

        return None

    def add_manager(self, manager):
        """
        Adds a new manager.
        """

        self._managed_by.append(manager)

    def matches(self, attribute, value):
        """
        Returns true if this section's attribute matches a specific value.
        """

        if attribute == '_managed_by':
            return value in self._managed_by

        return getattr(self, attribute, None) == value

    def format_value(self, key, value, package, section, idx=None, fmt=UCIFormat.DUMP):
        """
        Formats a value so it is suitable for insertion into UCI.
        """

        if fmt == UCIFormat.DUMP:
            if isinstance(value, (list, tuple)):
                value = ' '.join(str(x) for x in value)
            elif isinstance(value, bool):
                value = int(value)
            else:
                value = str(value).strip().replace('\n', ' ')

            if self._typ is not None:
                return ['{0}.{1}.{2}={3}'.format(package, section, key, value)]
            else:
                return ['{0}.@{1}[{2}].{3}={4}'.format(package, section, idx, key, value)]
        elif fmt == UCIFormat.FILES:
            if isinstance(value, (list, tuple)):
                return ['\tlist %s \'%s\'' % (key, item) for item in value]
            elif isinstance(value, bool):
                return ['\toption %s \'%s\'' % (key, int(value))]
            else:
                return ['\toption %s \'%s\'' % (key, str(value).strip().replace('\n', ' '))]

        return str(value)

    def format(self, package, section, idx=None, fmt=UCIFormat.DUMP):
        """
        Formats the configuration tree so it is suitable for loading into UCI.
        """

        output = []

        # Output section header
        if self._typ is not None:
            # Named sections
            if fmt == UCIFormat.DUMP:
                output.append('{0}.{1}={2}'.format(package, section, self._typ))
            elif fmt == UCIFormat.FILES:
                output.append('config %s \'%s\'' % (self._typ, section))
        else:
            # Ordered sections
            if fmt == UCIFormat.DUMP:
                output.append('{0}.@{1}[{2}]={1}'.format(package, section, idx))
            elif fmt == UCIFormat.FILES:
                output.append('config %s' % section)

        # Output section values
        for key, value in self._values.iteritems():
            if key.startswith('_'):
                continue
            output += self.format_value(key, value, package, section, idx, fmt)

        # Output section footer
        if fmt == UCIFormat.FILES:
            output.append('')

        return output


class UCIPackage(object):
    """
    Represents an UCI configuration file with multiple named and ordered
    sections.
    """

    def __init__(self, package):
        """
        Class constructor.

        :param package: Package name
        """

        if not UCI_PACKAGE_IDENTIFIER.match(package):
            raise ValueError("Invalid UCI package name '%s'." % package)

        self._package = package
        self._named_sections = collections.OrderedDict()
        self._ordered_sections = collections.OrderedDict()

    def add(self, *args, **kwargs):
        """
        Creates a new UCI section. An ordered section should be specified by using
        a single argument and a named section by using a single keyword argument.

        :return: The newly created UCISection
        """

        managed_by = kwargs.pop('managed_by', None)

        if len(args) > 1 or len(kwargs) > 1 or len(args) == len(kwargs):
            raise ValueError

        if kwargs:
            # Adding a named section.
            section_key = kwargs.values()[0]
            section_type = kwargs.keys()[0]
            if not UCI_IDENTIFIER.match(section_key):
                raise ValueError("Invalid named UCI section name '%s'." % section_key)

            section = UCISection(key=section_key, typ=section_type, managed_by=managed_by)

            # Check for duplicates to avoid screwing up existing lists and sections
            if section_key in self._named_sections:
                raise ValueError("UCI section '%s' is already defined!" % section_key)

            self._named_sections[section_key] = section
        else:
            # Adding an ordered section.
            section = UCISection(managed_by=managed_by)
            self._ordered_sections.setdefault(args[0], []).append(section)

        return section

    def named_sections(self):
        """
        Returns an iterator over the named sections.
        """

        return self._named_sections.iteritems()

    def ordered_sections(self):
        """
        Returns an iterator over the ordered sections.
        """

        return self._ordered_sections.iteritems()

    def find_named_section(self, section_type, **query):
        """
        Searches for the first named section having specific values of
        attributes.

        :param section_type: Section type
        :param **query: Attribute query
        :return: Named section or None if not found
        """

        sections = self.find_all_named_sections(section_type, **query)
        if not sections:
            return None

        return sections[0]

    def find_all_named_sections(self, section_type, **query):
        """
        Searches for all named sections having specific values of
        attributes.

        :param section_type: Section type
        :param **query: Attribute query
        :return: A list of named sections matching the criteria
        """

        sections = []
        for name, section in self.named_sections():
            if section.get_type() != section_type:
                continue

            if all((section.matches(a, v) for a, v in query.items())):
                sections.append(section)

        return sections

    def find_ordered_section(self, section_type, **query):
        """
        Searches for the first ordered section having specific values of
        attributes.

        :param section_type: Section type
        :param **query: Attribute query
        :return: Ordered section or None if not found
        """

        sections = self.find_all_ordered_sections(section_type, **query)
        if not sections:
            return None

        return sections[0]

    def find_all_ordered_sections(self, section_type, **query):
        """
        Searches for all ordered section having specific values of
        attributes.

        :param section_type: Section type
        :param **query: Attribute query
        :return: List of ordered sections matching the criteria
        """

        sections = []
        for section in self._ordered_sections.get(section_type, []):
            if all((section.matches(a, v) for a, v in query.items())):
                sections.append(section)

        return sections

    def __iter__(self):
        return self.named_sections()

    def __contains__(self, section):
        return section in self._named_sections or section in self._ordered_sections

    def __getattr__(self, section):
        """
        Retrieves the wanted UCI section.
        """

        if section.startswith('__') and section.endswith('__'):
            raise AttributeError(section)

        try:
            return self._named_sections[section]
        except KeyError:
            try:
                return self._ordered_sections[section]
            except KeyError:
                raise AttributeError(section)

    def __getitem__(self, section):
        try:
            return self.__getattr__(section)
        except AttributeError:
            raise KeyError(section)

    def format(self, fmt=UCIFormat.DUMP):
        """
        Formats the configuration tree so it is suitable for loading into UCI.

        :param fmt: Wanted export format
        """

        output = []
        for name, section in self._named_sections.iteritems():
            output += section.format(self._package, name, fmt=fmt)

        for name, sections in self._ordered_sections.iteritems():
            for idx, section in enumerate(sections):
                output += section.format(self._package, name, idx, fmt=fmt)

        return output
