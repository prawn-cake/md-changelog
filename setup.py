from setuptools import setup


setup(
    name='md-changelog',
    version='0.1.3',
    packages=['md_changelog'],
    url='',
    license='MIT',
    author='Maksim Ekimovskii',
    author_email='ekimovsky.maksim@gmail.com',
    description='Changelog command-line tool manager',
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'md-changelog = md_changelog.main:main'
        ]
    }
)
