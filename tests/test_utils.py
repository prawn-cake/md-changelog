# -*- coding: utf-8 -*-
import pytest


@pytest.mark.skip('only for local tests')
def test_git_backend():
    from md_changelog.utils.git import GitBackend

    git = GitBackend()
    email = git.get_user_email()
    name = git.get_user_name()
    assert email == 'ekimovsky.maksim@gmail.com'
    assert name == 'Maksim Ekimovskii'

