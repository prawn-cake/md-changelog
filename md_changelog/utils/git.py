# -*- coding: utf-8 -*-
import subprocess

from md_changelog.utils import VcsBackend


class GitBackend(VcsBackend):
    """Git utils backend"""

    def get_user_email(self):
        return self.call_cmd('git', 'config', 'user.email')

    def get_user_name(self):
        return self.call_cmd('git', 'config', 'user.name')

    @classmethod
    def call_cmd(cls, *args):
        output = subprocess.check_output(args)
        return output.strip().decode('utf-8')
