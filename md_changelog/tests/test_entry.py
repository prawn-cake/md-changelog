# -*- coding: utf-8 -*-
import os.path as op
import pytest

from md_changelog.entry import LogEntry, Changelog

FIXTURES_DIR = op.abspath(op.dirname(__file__)) + '/fixtures'


def get_fixtures_path(filename):
    return '/'.join([FIXTURES_DIR, filename])


def get_fixtures(filename):
    with open(get_fixtures_path(filename)) as fd:
        content = fd.read()
    return content


@pytest.fixture
def raw_changelog():
    return get_fixtures('Changelog.md')


def test_changelog_parsing(raw_changelog):
    entries = Changelog.parse_entries(text=raw_changelog)
    assert len(entries) == 1
    print(entries)
