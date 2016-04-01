import sys, os

modules = [
    os.path.dirname(__file__),
    os.path.dirname(__file__) + '/support'
]
for module in modules:
    if module not in sys.path:
        sys.path.append(module)

from expects import *
from testfixtures import TempDirectory
from support.runner import Runner
from support.settings import SettingObject

DEFAULT_PROJECT = 'Dummy Project'
DEFAULT_PROJECT_DIR = 'cookiecutter-dummy-project'

with description('Cookiecutter Template'):
    with after.all:
        TempDirectory.cleanup_all()

    with before.each:
        self.tempdir = TempDirectory()
        self.output_dir = self.tempdir.path
        self.project_dir = self.output_dir + '/' + DEFAULT_PROJECT_DIR
        self.settings = SettingObject({"project_name": DEFAULT_PROJECT}, self.output_dir)
        self.runner = Runner(self.settings)

    with after.each:
        self.tempdir.cleanup()

    with context('naming convention'):
        with it('names the directory using the project name rewritten in kebab-case format, prefixed with \'cookiecutter-\''):
            self.runner.run()

            expect(os.path.exists(self.project_dir)).to(be_true)
        