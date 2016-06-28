# -*- coding: utf-8 -*-

import os.path as op
import sys

from md_changelog.exceptions import ConfigNotFoundError

sys.path.append(
    op.abspath(op.dirname(__file__)) + '/../'
)

import argparse
import logging
import configparser
from md_changelog import tokens


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
        if op.exists(cfg_path):
            logger.info('Config %s already exist. Skip', path)
            return False
        # Write config
        config = configparser.ConfigParser()
        config['md-changelog'] = {
            'changelog': cfg_path
        }

        logger.debug('Writing config %s', cfg_path)
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
    config.read(path)
    return config


def release(args):
    """Make a new release

    :param args:
    """
    pass


def add_message(args):
    """Add message to unreleased

    :param args:
    """
    m_type = getattr(tokens.TYPES, args.message_type)
    message = tokens.Message(message=args.message, message_type=m_type)
    # TODO: implement last release parser
    print(message)


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

    for m_type in list(tokens.TYPES._asdict().keys()):
        msg_p = subparsers.add_parser(
            m_type, help='Add new %s entry to the current release' % m_type)
        msg_p.add_argument('message', help='Enter text message here')
        msg_p.set_defaults(func=add_message, message_type=m_type)

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
