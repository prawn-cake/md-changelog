# -*- coding: utf-8 -*-
import tempfile
import pytest
import os.path as op
from md_changelog import main
from md_changelog.exceptions import ConfigNotFoundError


@pytest.fixture
def parser():
    return main.create_parser()


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
        op.isfile(cfg_path)
        config = main.get_config(cfg_path)
        assert config['md-changelog']['changelog'] == cfg_path

        # Check changelog and default content
        changelog_path = op.join(tmp_dir, main.CHANGELOG_NAME)
        op.isfile(changelog_path)
        with open(changelog_path) as fd:
            content = fd.read()
        assert content == main.INIT_TEMPLATE


def test_add_message(parser):
    args = parser.parse_args(['message', 'test message'])
    args.func(args)

    args = parser.parse_args(['improvement', 'test improvement'])
    args.func(args)

    args = parser.parse_args(['feature', 'test feature'])
    args.func(args)

    args = parser.parse_args(['bugfix', 'test bugfix'])
    args.func(args)
