# -*- coding: utf-8 -*-
import os.path as op
import tempfile
from contextlib import contextmanager

import mock
import pytest

from md_changelog import main
from md_changelog.entry import Changelog
from md_changelog.exceptions import ConfigNotFoundError


@pytest.fixture
def parser():
    return main.create_parser()


@contextmanager
def get_test_config():
    parser = main.create_parser()
    with tempfile.TemporaryDirectory() as tmp_dir:
        args = parser.parse_args(['init', '--path', tmp_dir])
        args.func(args)
        cfg_path = op.join(tmp_dir, main.CONFIG_NAME)
        yield cfg_path


def test_get_config():
    with pytest.raises(ConfigNotFoundError) as err:
        main.get_config('/tmp/not_exists.cfg')
        assert 'Config is not found' in str(err)


def test_init(parser):
    with tempfile.TemporaryDirectory() as tmp_dir:
        args = parser.parse_args(['init', '--path', tmp_dir])
        args.func(args)

        # Check config and default parameters
        cfg_path = op.join(tmp_dir, main.CONFIG_NAME)
        changelog_path = op.join(tmp_dir, main.CHANGELOG_NAME)
        op.isfile(cfg_path)
        config = main.get_config(cfg_path)
        assert len(config.keys()) == 2
        assert config['md-changelog']['changelog'] == changelog_path
        assert config['md-changelog']['vcs'] == 'git'

        # Check changelog and default content
        assert op.isfile(changelog_path)
        with open(changelog_path) as fd:
            content = fd.read()
        assert content == main.INIT_TEMPLATE


def test_add_message(parser):
    with get_test_config() as cfg_path:
        config = main.get_config(cfg_path)
        args = parser.parse_args(['-c', cfg_path, 'message', 'test message'])
        args.func(args)

        args = parser.parse_args(
            ['-c', cfg_path, 'improvement', 'test improvement'])
        args.func(args)

        args = parser.parse_args(['-c', cfg_path, 'feature', 'test feature'])
        args.func(args)

        # check unicode message
        args = parser.parse_args(['-c', cfg_path, 'bugfix', 'багфикс'])
        args.func(args)

        changelog = Changelog.parse(path=config['md-changelog']['changelog'])
        assert len(changelog.entries) == 1
        assert len(changelog.entries[0]._messages) == 4


def test_release(parser):
    with mock.patch('subprocess.call') as call_mock:
        # Without version specification
        with get_test_config() as cfg_path:
            args = parser.parse_args(
                ['-c', cfg_path, 'release'])
            with mock.patch('md_changelog.main.get_input', return_value='Y') \
                    as input_mock:
                args.func(args)
                assert input_mock.called
                assert call_mock.called is True
                args = call_mock.call_args_list[0][0][0]
                assert main.default_editor() in args
                assert main.CHANGELOG_NAME in args[1]

        # With version '-v'
        with get_test_config() as cfg_path:
            args = parser.parse_args(
                ['-c', cfg_path, 'release', '-v', '1.0.0'])
            with mock.patch('md_changelog.main.get_input', return_value='Y') \
                    as input_mock:
                args.func(args)
            assert input_mock.called
            assert call_mock.called is True
            args = call_mock.call_args_list[0][0][0]
            assert main.default_editor() in args
            assert main.CHANGELOG_NAME in args[1]


def test_show_last(parser):
    # Just expect no errors
    with get_test_config() as cfg_path:
        args = parser.parse_args(['-c', cfg_path, 'last'])
        args.func(args)
