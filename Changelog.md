Changelog
=========

0.1.3 (2016-07-10)
--------------------
* Remove py27 support, keep only py3, too hassle to maintain it and time to move to be in the new era of python
* [Feature] Added confirmation dialog for 'release' with support of rollback, added --force-yes key to disable it

0.1.2 (2016-07-08)
------------------
* [Improvement] py2/3 compatibility
* [Improvement] implemented changelog.undo()

0.1.1 (2016-07-07)
------------------
* [Improvement] Rename cli command current -> last
* [Improvement] updated append command, added --no-edit key
* [Improvement] improve add_message feature, new --split-by key to add multiple entries at once

0.1.0 (2016-07-06)
------------------
* [Feature] Implemented basic functionality: init, messages, release, append, current, edit

