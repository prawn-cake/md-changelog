# -*- coding: utf-8 -*-

import argparse
import configparser
import functools
import logging
import os
import os.path as op
import subprocess

import sys

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
                '%s+1 (UNRELEASED)\n' \
                '--------------------' % Changelog.INIT_VERSION
CONFIG_NAME = '.md-changelog.cfg'
DEFAULT_VCS = 'git'


def handler(fn):
    """Helper decorator for command-line handler functions

    :param fn: decorated function
    :return:
    """

    @functools.wraps
    def wrapper(args):
        config = get_config(path=args.config)
        res = fn(args, config)
        return res
    return wrapper


def default_editor():
    return os.getenv('EDITOR', 'vi')


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


def get_changelog(config_path):
    """Changelog getter

    :param config_path: str: path to config 
    :return: md_changelog.entry.Changelog instance
    """
    config = get_config(path=config_path)
    changelog_path = config['md-changelog']['changelog']
    return Changelog.parse(path=changelog_path)


def get_input(text):
    """Get input wrapper. It basically needs for unittests

    :param text: str
    :return: input result
    """
    return input(text)


def release(args):
    """Make a new release

    :param args: command-line args
    """

    changelog = get_changelog(args.config)
    last_entry = changelog.last_entry
    if not last_entry:
        logger.info('Empty changelog. Nothing to release')
        sys.exit(99)

    if last_entry.version.released:
        logger.info("No UNRELEASED entries. Run 'md-changelog append'")
        sys.exit(99)

    if args.version:
        # Set up specific version
        v = tokens.Version(args.version)
        last_v = last_entry.version
        if v <= last_v:
            logger.info('Version must be greater than the last one: '
                        '%s <= %s (last one)', v, last_v)
            sys.exit(99)
        else:
            last_entry.set_version(v)

    # Backup before release
    changelog.make_backup()

    last_entry.set_date(tokens.Date())
    changelog.save()

    # Skip this step if --force-yes is passed
    if not args.force_yes:
        subprocess.call([default_editor(), changelog.path])
        confirm = get_input('Confirm changes? [Y/n]')
        if confirm == 'n':
            res = changelog.undo()
            logger.info('Undo changes: %s', 'OK' if res else 'Fail')
            changelog.save()
            sys.exit(0)

    changelog.reload()
    if not changelog.last_entry.version.released:
        logger.warning(
            "WARNING: version still contains dev suffix: %s. "
            "Run 'md-changelog edit' to fix it",
            changelog.last_entry.version)

    if len(changelog.entries) > 1:
        v_cur = changelog.last_entry.version
        v_prev = changelog.entries[-2].version
        if v_cur <= v_prev:
            logger.warning(
                "WARNING: wrong release version, less or equal "
                "the previous one: %s (current) <= %s (previous). "
                "Run 'md-changelog edit' to fix it",
                v_cur, v_prev)


def append_entry(args):
    """Append new changelog entry

    :param args: command-line args
    """
    changelog = get_changelog(args.config)
    last_entry = changelog.last_entry
    if last_entry and not last_entry.version.released:
        logger.info('Changelog has contained UNRELEASED entry. '
                    'Make a release before appending a new one')
        sys.exit(99)
    changelog.new_entry()
    changelog.save()
    if not args.no_edit:
        subprocess.call([default_editor(), changelog.path])
    logger.info("Added new '%s' entry", changelog.last_entry.header)


def edit(args):
    """Open changelog in the editor"""
    config = get_config(path=args.config)
    changelog_path = config['md-changelog']['changelog']
    editor = default_editor()
    logger.info('Call: %s %s', editor, changelog_path)
    subprocess.call([editor, changelog_path])


def add_message(args):
    """Add message to unreleased

    :param args: command-line args
    """
    changelog = get_changelog(args.config)
    m_type = getattr(tokens.TYPES, args.message_type)
    messages = []
    if args.split_by:
        messages = [tokens.Message(text=msg.strip(), message_type=m_type)
                    for msg in args.message.split(args.split_by)]
    else:
        messages.append(tokens.Message(text=args.message, message_type=m_type))

    if not changelog.last_entry or changelog.last_entry.version.released:
        new_entry = changelog.new_entry()
        for msg in messages:
            new_entry.add_message(msg)
    else:
        for msg in messages:
            changelog.last_entry.add_message(msg)
    changelog.save()

    logger.info('Added new %d %s entry to the %s (%s)',
                len(messages),
                args.message_type,
                op.relpath(changelog.path),
                str(changelog.last_entry.version))


def show_last(args):
    """Show the last changelog log entry

    :param args: command-line args
    """
    changelog = get_changelog(args.config)
    print('\n%s\n' % changelog.last_entry.eval())


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
        'release', help='Release current version')
    release_p.add_argument('-v', '--version', help='New release version')
    release_p.add_argument('-y', '--force-yes', action='store_true',
                           help="Don't ask changes confirmation")
    release_p.set_defaults(func=release)

    append_p = subparsers.add_parser(
        'append', help='Append a new changelog entry')
    append_p.add_argument('--no-edit', help="Don't call text editor after run",
                          action='store_true')
    append_p.set_defaults(func=append_entry)

    # Message parsers
    for m_type in list(tokens.TYPES._asdict().keys()):
        msg_p = subparsers.add_parser(
            m_type, help='Add new %s entry to the current release' % m_type)
        msg_p.add_argument('message', help='Enter text message here')
        msg_p.add_argument('--split-by', type=str,
                           help='Split message into several and add it as '
                                'multiple entries')
        msg_p.set_defaults(func=add_message, message_type=m_type)

    # Open in an editor command
    edit_p = subparsers.add_parser('edit', help='Open changelog in the editor')
    edit_p.set_defaults(func=edit)

    last_p = subparsers.add_parser('last', help='Show last log entry')
    last_p.set_defaults(func=show_last)

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
