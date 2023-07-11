import nox


PYTHON_TEST_VERSIONS = ("3.7", "3.8", "3.9", "3.10", "3.11", "3.12")
PYTHON_DEVELOPMENT_VERSION = "3.11"


@nox.session(python=PYTHON_TEST_VERSIONS)
def test(session):
    session.install("-e", ".")
    session.install("requests", "pytest")
    session.run("pytest")


@nox.session(python=PYTHON_TEST_VERSIONS)
def test_include_router(session):
    session.install("-e", ".")
    session.install("requests", "pytest")
    session.run("pytest", "--include-router")


@nox.session
def lint(session):
    session.install("-e", ".")
    session.install("pylint")
    session.run("pylint", "fritzconnection")


# @nox.session(python=PYTHON_DEVELOPMENT_VERSION)
# def build(session):
#     session.install("-e", ".")
#     session.run("python", "setup.py", "sdist", "bdist_wheel")


# @nox.session(name="upload-to-pypi", python=PYTHON_DEVELOPMENT_VERSION)
# def uppload_to_pypi(session):
#     session.install("-e", ".")
#     session.install("twine")
#     session.run("twine", "upload", "dist/*")
