# Contributing

Thank you for taking your time to contribute to this project.
The project is not large enough to need a lot of rules, but here are some guidelines:


## Issues

In case you think that something is not working as expected or you have a new idea, feel free to create an issue. Especially if you want to provide a pull-request, it is a good idea to create an issue first. Please also keep in mind that issues are not for support. For support try 'discussions' (but please keep in mind that this is not a commercial product, so you may get support or not).


## Pull requests

In general pull requests are welcome. But please create an issue first before putting too much work into a pull request that may not get merged at the end, for whatever reason. An issue can help to clarify points of view and motivation.

For pull requests there is a golden rule: **keep them small**. Smaller pull requests are easier to review and easier to merge – especially in cases when not every part of a larger changeset should get merged and has to get modifications.

Please avoid to just change the formatting. The result is most often nothing else than git-diff pollution. This is especially true for `black` – this project startet before `black` (or `blue`). It is ok to use `black` for modified code snippets, but not for a module.


## Status of core and lib

fritzconnection is mainly the code in the core-directory. This code is pretty mature and stable so far.

Most changes are in the library (the lib-directory). The library started mainly as a collection of examples how to use the core. Because it's easier to use an existing function instead of reading the AVM TR-064 documentation, the library modules have grown over time.

But every action supported by AVM can get executed without the library. So best enhancements should not be to trivial.


## Style guide

- In general the style guide is PEP 8.
- Recommended maximum line length is 80 something.
- Use proper names: i.e. an atrribute for `attributes` or `properties`, a verb for `callables`.
- Try to avoid `black` (see "Pull requests").


## Comments

No new function, method or class should get undocumented. Write meaningful comments: what the code does, about the arguments and return values, and - important - the corresponding types.


## Type hints

This project started long ago without type hints. Keep it that way. The project is small enough, so there is no real benefit. Also some parts of the code are really dynamic (one strength of Python), where type-hints can lead to a nightmare. The place for types in this project are in the comments. Readability counts!

Update: since version 1.13.0 type hints are introduced for the public API (and only there). Type-hints must be backward compatible for the oldest supported python-version. For type-checking `mypy` is used.


## Tests

This project comes with tests. The test framework is tox/pytest. For development run `pip install -r requirements_test.txt` to install both libraries. As far as possible, the code should get tests. Before committing run the tests with tox.

Update: since version 1.13.0 `nox` has been introduced for testing. For `nox` there is no need for the `requirements_test.txt` file.
