# -*- coding: utf-8 -*-
import abc
import copy
import re

from md_changelog import tokens
from md_changelog.exceptions import ChangelogError
from md_changelog.tokens import Version, Date, Message


class Evaluable(object):
    """Evaluable interface class. Just indicate that class has .eval() method
    """

    MD_TEMPLATE = ''

    @abc.abstractmethod
    def eval(self):
        """This method should generally evaluate the value of it's holder.
        In most cases it should return some markdown string
        """
        pass


class LogEntry(Evaluable):
    """Changelog log entry representation"""

    def __init__(self, version=None, date=None):
        self._version = version
        self._date = date
        self._messages = []

    @property
    def declared(self):
        """Log entry is declared only in case of version and date is defined

        :return:
        """
        if all([self._version, self._date]):
            return True
        else:
            if self._version and not self._version.released:
                return True
        return False

    @property
    def version(self):
        return self._version

    def eval(self):
        header = self.header
        text_tokens = (header,
                       '-' * len(header),
                       '\n'.join(['* {}'.format(entry.eval())
                                  for entry in self._messages]))
        return '\n'.join(text_tokens)

    def add_message(self, message):
        if not isinstance(message, tokens.Message):
            raise ValueError('Wrong message type %r, must be %s'
                             % (message, tokens.Message))
        self._messages.append(message)

    def set_version(self, version):
        cond = (self._version is None,
                self.version and not self.version.released)
        if any(cond):
            self._version = version
        else:
            raise ChangelogError(
                "Can't add version because it's already exists")

    def set_date(self, date):
        cond = (self._date is None,
                self._date and not self._date.is_set(),
                not self.version.released)
        if any(cond):
            self._date = date
        else:
            raise ChangelogError(
                "Can't add date because it's already exists")

    @property
    def header(self):
        return '{version} ({date})'.format(version=self._version.eval(),
                                           date=self._date.eval())

    @staticmethod
    def is_header(line):
        v = Version.parse(line)
        dt = Date.parse(line)
        if all([v, dt]):
            return True
        elif any([v, dt]):
            # Accept unreleased header
            if v and not v.released:
                return True
            raise ChangelogError(
                'Broken header %s. Version and date must be presented' % line)
        return False

    @staticmethod
    def is_message(line):
        return bool(Message.parse(line))

    def __repr__(self):
        return "%s(version=%s, date=%s, declared=%s, messages=%d)" % \
               (self.__class__.__name__, str(self.version), str(self._date),
                self.declared, len(self._messages))

    def __eq__(self, other):
        return all([self.version == other.version,
                    self._date == other._date,
                    self._messages == other._messages])


class Changelog(object):
    """Changelog representation"""

    IGNORE_LINES_RE = re.compile(r'([-=]{3,})')  # ----, ===
    INIT_VERSION = '0.1.0'

    def __init__(self, path, entries=None):
        self.header = 'Changelog'
        self.path = path
        self.entries = entries or []
        self._backup = None

    @property
    def last_entry(self):
        if not self.entries:
            return None
        return self.entries[-1]

    @property
    def versions(self):
        if not self.entries:
            return None
        return [entry.version for entry in self.entries]

    @classmethod
    def parse(cls, path):
        """Parse changelog

        :param path: str
        :return: Changelog instance
        """
        with open(path) as fd:
            content = fd.read()
        entries = cls.parse_entries(text=content)
        instance = Changelog(path=path, entries=entries[::-1])
        return instance

    @classmethod
    def parse_entries(cls, text):
        """Parse text into log entries

        :param text: str: raw changelog text
        :rtype: list
        """
        entries = []
        stack = []
        log_entry = None
        for line in text.splitlines():
            # Skip comments or empty lines
            if line.startswith('#') or not line:
                continue
            if cls.IGNORE_LINES_RE.search(line):
                continue

            if LogEntry.is_header(line):
                log_entry = LogEntry()
                stack.append(log_entry)
                if not log_entry.declared:
                    # New log entry
                    log_entry.set_version(Version.parse(line))
                    log_entry.set_date(Date.parse(line))
                else:
                    entries.append(log_entry)
                    stack.pop()

                    log_entry = LogEntry()
                    stack.append(log_entry)
            elif log_entry and log_entry.declared and LogEntry.is_message(line):
                # parse messages only after log header is declared
                log_entry.add_message(Message.parse(line))
            else:
                continue
        if stack:
            entries.extend(stack)
        return entries

    def new_entry(self):
        """Create and add new unreleased log entry

        :return: LogEntry instance
        """
        self._make_backup()
        log_entry = LogEntry()
        if len(self.entries) == 0:
            last_version = self.INIT_VERSION
        else:
            last_version = str(self.last_entry.version)

        v = Version(version_str='%s+1' % last_version)
        log_entry.set_version(version=v)
        log_entry.set_date(date=Date(dt=''))  # set Date as unreleased
        self.entries.append(log_entry)
        return log_entry

    def add_entry(self, entry):
        if not isinstance(entry, LogEntry):
            raise ValueError('Wrong entry type %r, must be %s'
                             % (entry, LogEntry))
        self._make_backup()
        self.entries.append(entry)

    def save(self):
        """Save and sync changes
        """
        with open(self.path, 'w') as fd:
            fd.write('Changelog\n=========\n\n')
            fd.write('\n\n'.join(
                [entry.eval() for entry in reversed(self.entries)])
            )
            fd.write('\n\n')

    def reload(self):
        """Reload changelog within the same instance

        """
        reloaded = self.parse(self.path)
        self.__dict__ = copy.deepcopy(reloaded.__dict__)

    def undo(self):
        if self._backup:
            self.__dict__ = copy.deepcopy(self._backup.__dict__)
            return True
        return False

    def _make_backup(self):
        """Make deep copy of itself
        """
        self._backup = copy.deepcopy(self)

    def __repr__(self):
        return "%s(entries=%d)" % (self.__class__.__name__, len(self.entries))
