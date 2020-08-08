# flake8: noqa

import dinoxhelper

lib_name = 'dicountries'

dilibraries = tuple()


@nox.session(python=test_pythons)
@nox.parametrize('extras', [None])
def test(session, extras, dilibraries=dilibraries):
    """Run the test suite."""
    session.log(f'Run test in {lib_name}')
    standard_di_test(session, extras=extras, dilibraries=dilibraries)


@nox.session(python=main_python)
def docs(session, dilibraries=dilibraries):
    """Generate documentation."""
    session.log(f'Run docs in {lib_name}')
    standard_di_docs(session, dilibraries=dilibraries)


@nox.session(python=main_python)
def install_dev(session):
    """Create development virtual environment."""
    session.log(f'Run install_dev in {lib_name}')
    common_setup(session, dilibraries=dilibraries)


@nox.session(python=main_python)
def build_library(session):
    """Build library package. (Add version file manually.)"""
    session.log(f'Run build_library in {lib_name}')
    standard_build_di_library(session, dilibraries=dilibraries)


@nox.session(python=main_python, reuse_venv=True)
@nox.parametrize('extras', [None])
def flake8(session, extras):
    """Check code with flake8"""
    session.log(f'Run flake8 for {lib_name}')
    standard_di_flake8(session, extras=extras, dilibraries=dilibraries)


@nox.session(python=main_python, reuse_venv=True)
@nox.parametrize('extras', [None])
def pylint(session, extras):
    """Check code with pylint"""
    session.log(f'Run pylint for {lib_name}')
    standard_di_pylint(session, extras=extras, dilibraries=dilibraries)


@nox.session(python=main_python, reuse_venv=True)
@nox.parametrize('extras', [None])
def bandit(session, extras):
    """Check code with bandit"""
    session.log(f'Run bandit for {lib_name}')
    standard_di_bandit(session, extras=extras, dilibraries=dilibraries)


@nox.session(python=main_python, reuse_venv=True)
def isort_check(session):
    """Check code with isort"""
    session.log(f'Run isort_check for {lib_name}')
    standard_di_isort_check(session)


@nox.session(python=main_python, reuse_venv=True)
def isort(session):
    """Sort imports with isort"""
    session.log(f'Run isort for {lib_name}')
    standard_di_isort(session)


@nox.session(python=main_python, reuse_venv=True)
@nox.parametrize('extras', [None])
def mypy(session, extras):
    """Check code with mypy"""
    session.log(f'Run mypy for {lib_name}')
    standard_di_mypy(session, extras=extras, dilibraries=dilibraries)


@nox.session(python=main_python, reuse_venv=True)
@nox.parametrize('extras', [None])
def check_outdated(session, extras):
    """Check for outdated packages"""
    session.log(f'Run check_outdated for {lib_name}')
    standard_di_check_outdated(session, extras=extras, dilibraries=dilibraries)


@nox.session(python=main_python, reuse_venv=True)
def black(session):
    """Format code with black (brunette)."""
    session.log(f'Run isort for {lib_name}')
    standard_di_black(session)


@nox.session(python=main_python, reuse_venv=True)
def black_check(session):
    """Print code diffs for black (brunette) formatting."""
    session.log(f'Run isort for {lib_name}')
    standard_di_black_check(session)


@nox.session(python=main_python, reuse_venv=True)
def proselint(session):
    """Check code with proselint"""
    session.log(f'Run proselint for {lib_name}')
    standard_di_proselint(session)
