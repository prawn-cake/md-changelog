# -*- coding: utf-8 -*-


class ChangelogError(Exception):
    """ Common module exception class"""
    pass


class WrongMessageTypeError(ChangelogError):
    pass


class ConfigNotFoundError(ChangelogError):
    pass
