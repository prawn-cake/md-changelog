# -*- coding: utf-8 -*-

import argparse
import configparser
import logging
import os
import os.path as op
import subprocess

from md_changelog import tokens
from md_changelog.entry import Changelog
from md_changelog.exceptions import ConfigNotFoundError

logging.basicConfig(
    level=logging.DEBUG,
    # format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
    format='--> %(message)s',
)

logger = logging.getLogger('md-changelog')
CHANGELOG_NAME = 'Changelog.md'
INIT_TEMPLATE = 'Changelog\n' \
                '=========\n\n' \
                '0.1.0+1 (UNRELEASED)\n' \
                '--------------------'
CONFIG_NAME = '.md-changelog.cfg'
DEFAULT_VCS = 'git'


def init(args):
    """Init new changelog and config

    """

    def init_changelog(path):
        file_path = op.join(op.abspath(path), CHANGELOG_NAME)
        if op.exists(file_path):
            logger.info('Changelog %s already exist. Skip', file_path)
            return False
        logger.debug('Init changelog: %s', file_path)
        with open(file_path, 'w') as fd:
            fd.write(INIT_TEMPLATE)
        return True

    def init_config(path):
        cfg_path = op.join(op.abspath(path), CONFIG_NAME)
        changelog_path = op.join(op.abspath(path), CHANGELOG_NAME)
        if op.exists(cfg_path):
            logger.info('Config %s already exist. Skip', path)
            return False
        # Write config
        config = configparser.ConfigParser()
        config['md-changelog'] = {
            'changelog': changelog_path,
            'vcs': DEFAULT_VCS
        }

        logger.info('Writing config %s', cfg_path)
        with open(cfg_path, 'w') as fd:
            config.write(fd)
        return True

    if args.path:
        if op.isdir(args.path):
            path = args.path
            init_changelog(path=path)
        else:
            raise ValueError('Wrong project path %s' % args.path)
    else:
        path = './'
        init_changelog(path=path)

    init_config(path)


def get_config(path=None):
    if path is not None:
        cfg_path = path
    else:
        cfg_path = op.join(op.abspath('.'), CONFIG_NAME)
    if not op.exists(cfg_path):
        raise ConfigNotFoundError('Config is not found: %s' % path)

    config = configparser.ConfigParser()
    config.read(cfg_path)
    return config


def release(args):
    """Make a new release

    :param args: command-line args
    """
    pass


def edit(args):
    """Open changelog in the editor"""
    config = get_config(path=args.config)
    editor = os.getenv('EDITOR', 'vi')
    changelog_path = config['md-changelog']['changelog']
    logger.info('Call: %s %s', editor, changelog_path)
    subprocess.call([editor, changelog_path])


def add_message(args):
    """Add message to unreleased

    :param args: command-line args
    """
    config = get_config(path=args.config)
    path = config['md-changelog']['changelog']
    changelog = Changelog.parse(path=path)
    m_type = getattr(tokens.TYPES, args.message_type)
    msg = tokens.Message(text=args.message, message_type=m_type)
    if not changelog.last_entry:
        new_entry = changelog.new_entry()
        new_entry.add_message(msg)
    else:
        changelog.last_entry.add_message(msg)
    changelog.save()

    logger.info('Added new %s entry to the %s (%s)',
                args.message_type, path, str(changelog.last_entry.version))


def create_parser():
    parser = argparse.ArgumentParser(
        description='md-changelog command-line tool')
    parser.add_argument('-c', '--config', help='Path to config file')

    subparsers = parser.add_subparsers(help='Sub-commands')

    # Add clone command parser and parameters
    init_p = subparsers.add_parser('init', help='Init new changelog')
    init_p.add_argument('--path', help='Path to project directory')
    init_p.set_defaults(func=init)

    release_p = subparsers.add_parser(
        'release', help='Add new release entry')
    release_p.add_argument('-v', '--version', help='New release version')
    release_p.set_defaults(func=release)

    # Message parsers
    for m_type in list(tokens.TYPES._asdict().keys()):
        msg_p = subparsers.add_parser(
            m_type, help='Add new %s entry to the current release' % m_type)
        msg_p.add_argument('message', help='Enter text message here')
        msg_p.set_defaults(func=add_message, message_type=m_type)

    edit_p = subparsers.add_parser('edit', help='Open changelog in the editor')
    edit_p.set_defaults(func=edit)

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
