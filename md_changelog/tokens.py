# -*- coding: utf-8 -*-
import abc
import re
from collections import namedtuple

from datetime import datetime

from md_changelog.exceptions import WrongMessageTypeError


class Evaluable(object):
    @abc.abstractmethod
    def eval(self):
        """This method should generally evaluate the value of it's holder.
        In most cases it should return some markdown string
        """
        pass


class Token(Evaluable):
    """Token interface"""

    @abc.abstractclassmethod
    def parse(self, raw_text):
        pass

    def __str__(self):
        return str(self.eval())


class Version(Token):
    """Version token"""

    VERSION_RE = re.compile(
        r'(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?P<suffix>\+\d+)?')

    def __init__(self, version_str, matcher=None):
        self.version_str = version_str
        self._version_dict = {}
        if not matcher:
            matcher = self.VERSION_RE.search(version_str)
        self._version_dict = matcher.groupdict()
        self._version_tuple = (self._version_dict['major'],
                               self._version_dict['minor'],
                               self._version_dict['patch'])

    @classmethod
    def parse(cls, raw_text):
        matcher = cls.VERSION_RE.search(raw_text)
        if not matcher:
            return None
        return cls(matcher.group(), matcher=matcher)

    @property
    def released(self):
        return not self._version_dict.get('suffix')

    def eval(self):
        return self.version_str

    def __repr__(self):
        return '%s(version_str=%s, released=%s)' % (
            self.__class__.__name__, self.version_str, self.released)

    def __gt__(self, other):
        return self._version_tuple > other._version_tuple

    def __lt__(self, other):
        return self._version_tuple < other._version_tuple

    def __ge__(self, other):
        return self._version_tuple >= other._version_tuple

    def __le__(self, other):
        return self._version_tuple <= other._version_tuple


class Date(Token):
    """Date token"""

    UNRELEASED = 'UNRELEASED'
    DATE_RE = re.compile(r'((\d{4})\-(\d{2})\-(\d{2})|%s)' % UNRELEASED)
    DATE_FMT = '%Y-%m-%d'

    def __init__(self, dt=None):
        if dt is None:
            self.dt = datetime.now()
        elif dt in ('', self.UNRELEASED):  # UNRELEASED can come from parse
            self.dt = None
        elif isinstance(dt, str):
            self.dt = datetime.strptime(dt, self.DATE_FMT)
        elif isinstance(dt, datetime):
            self.dt = dt
        else:
            raise ValueError('Wrong datetime value %r for Date token' % dt)

    def is_set(self):
        return isinstance(self.dt, datetime)

    @classmethod
    def parse(cls, raw_text):
        matcher = cls.DATE_RE.search(raw_text)
        if not matcher:
            return None
        return cls(dt=matcher.group())

    def eval(self):
        if self.dt:
            return self.dt.strftime(self.DATE_FMT)
        return self.UNRELEASED

    def __repr__(self):
        return ''


# Declare message type namedtuple
message_t = namedtuple('MESSAGE_TYPES', ['message',
                                         'feature',
                                         'bugfix',
                                         'improvement'])
TYPES = message_t(message='',
                  feature='Feature',
                  bugfix='Bugfix',
                  improvement='Improvement')


class Message(Token):
    """Changelog entry message"""

    MD_TEMPLATE = '{type} {text}'
    MESSAGE_RE = re.compile(r'^\* (?P<type>\[\w+\])? ?(?P<message>.*$)')

    def __init__(self, text, message_type=None):
        if not message_type:
            self._type = TYPES.message
        else:
            self._type = message_type
        self._text = text

    def eval(self):
        if self._type == TYPES.message:
            return self._text
        return self.MD_TEMPLATE.format(type=self.format_type(self._type),
                                       text=self._text)

    @staticmethod
    def format_type(val):
        return '[{}]'.format(val)

    @staticmethod
    def deformat_type(val):
        if val:
            val = str(val).replace('[', '').replace(']', '').lower()
        return val

    @classmethod
    def parse(cls, raw_text):
        matcher = cls.MESSAGE_RE.search(raw_text)
        if not matcher:
            return None

        values_dict = matcher.groupdict()
        if values_dict['type'] is None:
            values_dict['type'] = 'message'
        else:
            values_dict['type'] = cls.deformat_type(values_dict['type'])

        try:
            message_type = getattr(TYPES, str(values_dict['type']))
        except AttributeError:
            raise WrongMessageTypeError(
                'Wrong message type: %s' % values_dict['type'])
        instance = cls(text=str(values_dict['message']),
                       message_type=message_type)
        return instance

    def __repr__(self):
        return '%s(type=%s, text=%s)' % (
            self.__class__.__name__, self._type, self._text)
