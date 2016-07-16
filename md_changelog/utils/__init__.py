# -*- coding: utf-8 -*-


class VcsBackend(object):
    """VCS utils backend interface"""

    def get_user_email(self):
        raise NotImplementedError()

    def get_user_name(self):
        raise NotImplementedError()
