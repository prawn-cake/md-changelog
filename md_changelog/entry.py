# -*- coding: utf-8 -*-
import abc

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

    def eval(self):
        header = self.eval_header()
        tokens = (header,
                  '-' * len(header),
                  '\n'.join(['* {}'.format(entry.eval())
                             for entry in self._messages]))
        return '\n'.join(tokens)

    def add_message(self, message):
        if not isinstance(message, tokens.Message):
            raise ValueError('Wrong message type %r, must be %s'
                             % (message, tokens.Message))
        self._messages.append(message)

    def add_version(self, version):
        if self._version is None:
            self._version = version
        else:
            raise ChangelogError(
                "Can't add version because it's already exists")

    def add_date(self, date):
        if self._date is None:
            self._date = date
        else:
            raise ChangelogError(
                "Can't add date because it's already exists")

    def eval_header(self):
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
        return "%s(declared=%s, messages=%d)" % (self.__class__.__name__,
                                                 self.declared,
                                                 len(self._messages))


class Changelog(object):
    """Changelog representation"""

    IGNORE_LINES_RE = re.compile(r'([-=]{3,})')  # ----, ===

    def __init__(self, path=None, entries=None):
        self.path = path
        self.entries = entries or []

    @property
    def last_entry(self):
        if self.entries:
            return self.entries[-1]
        return None

    @classmethod
    def parse(cls, path):
        """Parse changelog

        :param path: str
        :param only_last: bool
        :return: Changelog
        """
        # TODO: write test for it
        with open(path) as fd:
            content = fd.read()
        entries = cls.parse_entries(text=content, only_last=False)
        instance = Changelog(path=path, entries=entries)
        return instance

    @classmethod
    def parse_entries(cls, text: str, only_last=True):
        """Parse text into log entries

        :param text: str: raw changelog text
        :param only_last: bool: parse only last entry
        """
        entries = []
        log_entry = LogEntry()
        for line in text.splitlines():
            # Skip comments or empty lines
            if line.startswith('#') or not line:
                continue
            if cls.IGNORE_LINES_RE.search(line):
                continue

            if LogEntry.is_header(line):
                if not log_entry.declared:
                    # New log entry
                    log_entry.add_version(Version.parse(line))
                    log_entry.add_date(Date.parse(line))
                else:
                    entries.append(log_entry)
                    if only_last:
                        break
                    # flush changes
                    log_entry = LogEntry()
            elif log_entry.declared and LogEntry.is_message(line):
                # parse messages only after log header is declared
                log_entry.add_message(Message.parse(line))
            else:
                continue
        return entries

    def new_entry(self):
        log_entry = LogEntry()
        self.entries.append(log_entry)
        return log_entry

    def sync(self):
        """Save and sync changes

        """
        # TODO: generate string and save
        pass

    def __repr__(self):
        return "%s(entries=%d)" % (self.__class__.__name__, len(self.entries))