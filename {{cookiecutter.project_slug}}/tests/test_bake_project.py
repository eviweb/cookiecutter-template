from contextlib import contextmanager

import os
import subprocess


@contextmanager
def inside_dir(dirpath):
    """
    Execute code from inside the given directory
    :param dirpath: String, path of the directory the command is being run.
    """
    old_path = os.getcwd()
    try:
        os.chdir(dirpath)
        yield
    finally:
        os.chdir(old_path)


def test_project_tree(cookies):
    result = cookies.bake(extra_context={'project_slug': 'test_project'})
    assert result.exit_code == 0
    assert result.exception is None
    assert result.project.basename == 'test_project'


def test_run_flake8(cookies):
    result = cookies.bake(extra_context={'project_slug': 'flake8_compat'})
    with inside_dir(str(result.project)):
        subprocess.check_call(['flake8'])
