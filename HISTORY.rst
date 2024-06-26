#####
2.0.4
#####

* Add Mozilla code of conduct
* Improve formatting with black
* Update taskcluster.yml
* Improve testing with tox
* Update MANIFEST file
* Add .dirschema.yml file
* Fix rst headings
* Add LICENSE file
* Fix linting failures

#####
2.0.3
#####

* Fix formatting of logs of retry attempts. Contributed by @nolanlum
* Fix deprecation warning in tests.
* Reformat code with black.

#####
2.0.2
#####

* Fix support in `redo.cmd` for commands with arguments.

#####
2.0.1
#####

* Lazily format log messages, so we don't incur costly str() calculations in some cases. Contributed by @samueldg

###
2.0
###

Changed
=======

* Allow jitter to be a float
