import os
import tempfile
import shutil
import pytest

from textwrap import dedent

from ...api import Gradebook


@pytest.fixture
def db(request):
    path = tempfile.mkdtemp()
    dbpath = os.path.join(path, "nbgrader_test.db")

    def fin():
        shutil.rmtree(path)
    request.addfinalizer(fin)

    return "sqlite:///" + dbpath


@pytest.fixture
def gradebook(db):
    gb = Gradebook(db)
    gb.add_assignment("ps1", duedate="2015-02-02 14:58:23.948203 PST")
    gb.add_student("foo")
    gb.add_student("bar")
    return db


@pytest.fixture
def course_dir(request):
    path = tempfile.mkdtemp()

    def fin():
        shutil.rmtree(path)
    request.addfinalizer(fin)

    return path


@pytest.fixture
def temp_cwd(request, course_dir):
    orig_dir = os.getcwd()
    path = tempfile.mkdtemp()
    os.chdir(path)

    with open("nbgrader_config.py", "w") as fh:
        fh.write(dedent(
            """
            c = get_config()
            c.NbGrader.course_directory = "{}"
            """.format(course_dir)
        ))

    def fin():
        os.chdir(orig_dir)
        shutil.rmtree(path)
    request.addfinalizer(fin)

    return path


@pytest.fixture
def jupyter_config_dir(request):
    path = tempfile.mkdtemp()

    def fin():
        shutil.rmtree(path)
    request.addfinalizer(fin)

    return path


@pytest.fixture
def jupyter_data_dir(request):
    path = tempfile.mkdtemp()

    def fin():
        shutil.rmtree(path)
    request.addfinalizer(fin)

    return path


@pytest.fixture
def env(request, jupyter_config_dir, jupyter_data_dir):
    env = os.environ.copy()
    env['JUPYTER_DATA_DIR'] = jupyter_data_dir
    env['JUPYTER_CONFIG_DIR'] = jupyter_config_dir
    return env


@pytest.fixture
def exchange(request):
    path = tempfile.mkdtemp()

    def fin():
        shutil.rmtree(path)
    request.addfinalizer(fin)

    return path

@pytest.fixture
def cache(request):
    path = tempfile.mkdtemp()

    def fin():
        shutil.rmtree(path)
    request.addfinalizer(fin)

    return path
