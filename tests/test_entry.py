# -*- coding: utf-8 -*-
import os.path as op
import tempfile

import pytest

from md_changelog import tokens
from md_changelog.entry import Changelog, LogEntry
from md_changelog.tokens import Message

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
    assert len(entries) == 2

    assert entries[0].version.released is False
    assert str(entries[0].version) == '0.1.0+1'

    assert entries[1].version.released is True
    assert str(entries[1].version) == '0.1.0'


def test_new_changelog_save():
    with tempfile.NamedTemporaryFile() as tmp_file:
        changelog = Changelog(path=tmp_file.name)

        # Create and add log entry manually
        entry = LogEntry(version=tokens.Version('0.1.0'), date=tokens.Date())
        entry.add_message(Message(text='Test message'))
        entry.add_message(Message(text='Updated tests',
                                  message_type=tokens.TYPES.improvement))
        changelog.add_entry(entry)

        # Add new entry
        new_entry = changelog.new_entry()
        new_entry.add_message(Message(text='Code refactoring message'))
        new_entry.add_message(Message(text='New super-cool feature',
                                      message_type=tokens.TYPES.feature))
        changelog.save()

        # Check idempotency
        changelog_2 = Changelog.parse(path=tmp_file.name)
        assert len(changelog.entries) == len(changelog_2.entries)
        for e1, e2 in zip(changelog.entries, changelog_2.entries):
            assert e1.eval() == e2.eval()


def test_changelog_backup():
    with tempfile.NamedTemporaryFile() as tmp_file:
        changelog = Changelog(path=tmp_file.name)
        assert len(changelog.entries) == 0

        # Test undo new entry
        changelog.new_entry()
        assert len(changelog.entries) == 1

        assert changelog.undo() is True
        assert len(changelog.entries) == 0

        # Add new entry + one entry manually, then undo the last one
        new_entry = changelog.new_entry()
        entry = LogEntry(version=tokens.Version('0.1.0'), date=tokens.Date())
        entry.add_message(Message(text='Test message'))
        changelog.add_entry(entry)
        assert len(changelog.entries) == 2

        assert changelog.undo() is True
        assert len(changelog.entries) == 1
        assert changelog.entries[0] == new_entry
