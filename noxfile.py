import nox


PYTHON_TEST_VERSIONS = ("3.7", "3.8", "3.9", "3.10", "3.11", "3.12", "3.13", "3.14")
PYTHON_DEVELOPMENT_VERSION = "3.11"


@nox.session(python=PYTHON_TEST_VERSIONS)
def test(session):
    session.install("-e", ".")
    session.install("requests", "pytest")
    session.run("pytest", "-m", "not routertest")


@nox.session(python=PYTHON_TEST_VERSIONS)
def test_router(session):
    session.install("-e", ".")
    session.install("requests", "pytest")
    session.run("pytest", "-m", "routertest")


@nox.session(python=PYTHON_TEST_VERSIONS)
def test_all(session):
    session.install("-e", ".")
    session.install("requests", "pytest")
    session.run("pytest")


@nox.session(name="check")
def ruff_check(session):
    session.run("ruff", "check", "fritzconnection", external=True)


@nox.session
def mypy(session):
    session.install("-e", ".")
    session.install("mypy==1.11.1", "types-requests", "segno")
    session.run("mypy", "fritzconnection/core/fritzconnection.py")
    session.run("mypy", "fritzconnection/core/fritzmonitor.py")
    session.run("mypy", "fritzconnection/lib")


@nox.session
def sphinx(session):
    session.install("-e", ".")
    session.install("pip-tools==7.3.0")
    session.run(
        "pip-compile",
        "--strip-extras",
        "-q",
        "--output-file=docs/requirements.out",
        "docs/requirements.txt"
        #"docs/requirements.local.in"
    )
    session.install("-r", "docs/requirements.out")
    session.run("sphinx-build", "docs", "docs_out")


@nox.session(python=PYTHON_DEVELOPMENT_VERSION)
def build(session):
    session.install("-e", ".")
    session.run("python", "setup.py", "sdist", "bdist_wheel")


@nox.session(name="check-twine", python=PYTHON_DEVELOPMENT_VERSION)
def check_twine(session):
    session.install("-e", ".")
    session.install("twine")
    session.run("twine", "check", "dist/*")


@nox.session(name="upload-to-pypi", python=PYTHON_DEVELOPMENT_VERSION)
def upload_to_pypi(session):
    session.install("-e", ".")
    session.install("twine")
    session.run("twine", "upload", "dist/*")
