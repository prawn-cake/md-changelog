# -*- coding: utf-8 -*-
import pytest
from datetime import datetime

from md_changelog import tokens


@pytest.fixture
def header_line():
    return '0.1.0 [2016-03-11]'


def test_version_token(header_line):
    """Test header tokens. It includes Version, Date tokens

    """
    v = tokens.Version.parse(raw_text=header_line)

    assert isinstance(v, tokens.Version)
    assert v.eval() == '0.1.0'


def test_date_token(header_line):
    d = tokens.Date.parse(raw_text=header_line)

    assert isinstance(d, tokens.Date)
    assert isinstance(d.dt, datetime)
    assert d.eval() == '2016-03-11'

    # Test init options

    # Expect that datetime.now()
    d = tokens.Date()
    assert isinstance(d.dt, datetime)

    # '' value indicates 'unreleased'
    d = tokens.Date(dt='')
    assert d.dt is None
    assert str(d) == tokens.Date.UNRELEASED


def test_message():
    message = tokens.Message(text='Test commit')
    assert message.eval() == 'Test commit'

    message = tokens.Message(text='Test commit',
                             message_type=tokens.TYPES.bugfix)
    assert message.eval() == '[Bugfix] Test commit'

    message = '* Test commit'
    message = tokens.Message.parse(message)
    assert isinstance(message, tokens.Message)
    assert message._type == tokens.TYPES.message
    assert message._text == 'Test commit'

    message = '* [Bugfix] Test commit'
    message = tokens.Message.parse(message)
    assert isinstance(message, tokens.Message)
    assert message._type == tokens.TYPES.bugfix
    assert message._text == 'Test commit'