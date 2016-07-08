md-changelog
============
[![Build Status](https://travis-ci.org/prawn-cake/md-changelog.svg?branch=master)](https://travis-ci.org/prawn-cake/md-changelog)

Handy command-line tool for managing changelog for your open source projects.


### TODO:

* bash auto-complete with https://github.com/kislyuk/argcomplete
* support multiple modes: list (just list of entries) and group (entries grouped by entry types: Features, Bugfixes, Improvements, etc)
* Git post-commit hook integration
* Git tag integration


## Config

    .md-changelog.rc


## Quickstart

    md-changelog init

   
### Open with editor

    md-changelog edit
    
    
### Add message entry

    md-changelog <entry type> <msg> [--split-by='<delimiter>']
    
    # Examples
    md-changelog message "My message"
    md-changelog improvement "Code cleanup"
    md-changelog bugfix "Fixed main loop"
    md-changelog feature "Implemented new feature"
    
    # Add multiple entries the same type at once
    md-changelog improvement --split-by "Code cleanup; New command-line --split-by key; Improved feature X"
    
    
Changelog may look like

    Changelog
    =========
    
    0.1.0+1 (UNRELEASED)
    --------------------
    * My message
    * [Improvement] Code cleanup
    * [Bugfix] Fixed main loop
    * [Feature] Implemented new feature


### Auto-message (not implemented)

    md-changelog auto-message "${some_var_from_git_commit_post_hook}"
    

### Show last changelog entry

    md-changelog last
    

### New release

Release currently unreleased version
    
    # Open in editor to update version manually
    md-changelog release
    
    # Set the version explicitly
    md-changelog release -v 1.0.0


### Append new unreleased entry

    md-changelog append
    md-changelog append --no-edit  # just add a new entry without calling editor 
    
