# Contributing

Thank you for taking time to contribute to this project.
The project is not large enough to need a lot of rules, but here are some guidelines:


## Issues

In case you think that something is not working as expected or you have a new idea, feel free to create an issue. Especially if you want to provide a pull-request, it is a good idea to create an issue first. Please also keep in mind that issues are not for support. For support try 'discussions' (please keep in mind that this is not a commercial product, so you may get support or not).


## Pull requests

In general pull requests are welcome. Please create an issue first before putting too much work into a pull request that may not get merged at the end, for whatever reason. An issue can help to clarify points of view and motivation.

For pull requests there is a golden rule: **keep them small**. Smaller pull requests are easier to review and easier to merge – especially in cases when not every part of a larger changeset should get merged and has to get modifications.

Please avoid to just change the formatting. The result is most often nothing else than git-diff pollution. This is especially true for `black` (or `blue` or the corresponding modes in `ruff`) – this project startet before `black`. It is ok to use these tools for modified code snippets, but not for a module.


## Status of core and lib

fritzconnection is mainly the code in the core-directory. This code is pretty mature and stable so far.

Most changes are in the library (the lib-directory). The library started mainly as a collection of examples how to use the core. Because it's easier to use an existing function instead of reading the AVM TR-064 documentation, the library modules have grown over time.

But every action supported by AVM can get executed without the library. So best enhancements should not be to trivial.


## Style guide

- In general the style guide is PEP 8.
- Recommended maximum line length is 80 something.
- Use proper names: i.e. an atrribute for `attributes` or `properties`, a verb for `callables`.
- Avoid `black` (see "Pull requests").


## Comments

No new function, method or class should get undocumented. Write meaningful comments: what the code does, about the arguments and return values, and - important - the corresponding types.


## Type hints

This project started long ago without type hints. Keep it that way. The project is small enough, so there is no real benefit. Also some parts of the code are really dynamic (one strength of Python), where type-hints can lead to a nightmare. The place for types in this project are in the comments. Readability counts!

Update: since version `1.13.0` type hints are introduced for the public API (and only there). Type-hints must be backward compatible for the oldest supported python-version. For type-checking `mypy` is used.


## Tests

This project comes with tests. Since version `1.13.0` `nox` is used for testautomation (`https://nox.thea.codes/en/stable/index.html`). `nox` should get installed separately. In the same environment where `nox` has been installed also `ruff` must be installed because the `noxfile` makes use of `ruff` as external module for linting.

After installation the sessions from the `noxfile.py` can be used like:

- `nox -s test`: run the tests with all supported python versions. The supported versions must be installed on the local development system and must be callable like `python3.11` or `python3.12`. Currently python `3.7` and newer are supported (no new language features are used, so backward compatibility is cheap). You can run `nox -s test-3.11` to run the tests with a single python version. This can be handy for development running the test for all versions later on.

- `nox -s test_router`: run all tests making a connection to the router. These tests are taking much more time and can fail because of connection errors. In case of a connection error run the tests again - chances are good the error was temporarly and gone and there are no real bugs. In all other cases: fix it. A test run with a defined python version (here `3.11`) can get started with `nox -s test_router-3.11`.

- `nox -s test_all`: run all tests including the time consuming router-tests.

- `nox -s check`: run `ruff` to `lint` the code.

- `nox -s mypy`: apply a mypy check.

- `nox -s sphinx`:  make a local build of the documentation.
