md-changelog
------------

**This is a design outline. Real README will be written a bit later**

Command-line tool to create and manage changelog for a python project.
Main format: markdown

## TODO

* Release feature


## Features

* Manual control of changelog
* Git post-commit hook integration
* Git tag integration
* bash auto-complete with https://github.com/kislyuk/argcomplete
* support multiple modes: list (just list of entries) and group (entries grouped by entry types: Features, Bugfixes, Improvements, etc)

## Config

    .md-changelog.rc


## Create new changelog

    md-changelog init [<path>]

## New release

Create new release or increment previous version

    md-changelog release [<version>]
    md-changelog release 1.0.3
    
## Open with editor

    md-changelog edit
    
    
## Add entry for the last version

Interface:

    md-changelog <entry type> [<msg>]
    
    # For example
    
    md-changelog message "My message"
    md-changelog improvement "Code cleanup"
    md-changelog bugfix "Fixed main loop"
    md-changelog feature "Implemented new feature"
    
The following changelog will be generated

    Changelog
    =========
    
    0.1.0+1 (UNRELEASED)
    --------------------
    * My message
    * [Improvement] Code cleanup
    * [Bugfix] Fixed main loop
    * [Feature] Implemented new feature


### Auto-message

    md-changelog auto-message "${some_var_from_git_commit_post_hook}"
    

## Get current (last) changelog entries

    md-changelog current