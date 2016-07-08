import sys
from setuptools import setup


req = ['six']
if sys.version_info >= (3, 2):
    pass
else:
    req.extend(["configparser"])

setup(
    name='md-changelog',
    version='0.1.2',
    packages=['md_changelog'],
    url='',
    license='MIT',
    author='Maksim Ekimovskii',
    author_email='ekimovsky.maksim@gmail.com',
    description='Changelog command-line tool manager',
    install_requires=req,
    entry_points={
        'console_scripts': [
            'md-changelog = md_changelog.main:main'
        ]
    }
)
