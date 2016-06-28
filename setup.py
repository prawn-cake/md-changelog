from setuptools import setup

setup(
    name='md-changelog',
    version='0.1.0',
    packages=['md_changelog'],
    url='',
    license='MIT',
    author='Maksim Ekimovskii',
    author_email='',
    description='Changelog command-line tool manager',
    entry_points={
        'console_scripts': [
            'md-changelog = md_changelog.main:main'
        ]
    }
)
