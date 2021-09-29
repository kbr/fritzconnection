# Contributing

Thank you for taking your time to contribute to this project.
The project is not large enough to need a lot of rules, but here are some guidelines:


## Pull requests

In general pull requests are welcome. The smaller the better. Smaller pull requests are easier to review and easier to merge – especially in cases when not every part of a larger changeset should get merged.

In case of doubt please start a discussion first about the idea – before putting too much work into a pull request that may not get merged at the end, for whatever reason. A discussion can help to clarify points of view and motivation, not obvious at first by just providing a pull request.


## Status of core and lib

fritzconnection is mainly the code in the core-directory. This code is pretty stable so far.

Most changes are in the library (the lib-directory). The library started mainly as a collection of examples how to use the core. Because it's easier to use an existing function instead of reading the AVM TR-064 documentation, the library modules have grown over time.

But every action supported by AVM can get executed without the library. So best enhancements are not too trivial tasks.


## Style guide

- In general the style guide is PEP 8.
- Recommended maximum line length is 80 something.


## Comments

No new function, method or class should get undocumented. Write meaningful comments: what the code does, about the arguments and return values, and -important- the corresponding types.


## Type hints

This project started long ago without type hints. Keep it this way. The project is small enough, so there is no real benefit. The place for types are in the comments. Readability counts!


## Tests

This project comes with tests. The test framework is tox/pytest. For development run `pip install -r requirements_test.txt` to install both libraries. As far as possible, the code should get tests. Before committing run the tests with tox.

