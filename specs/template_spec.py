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
from cookiecutter.config import get_config
from datetime import datetime

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
        
    with context('file content'):
        with it('fills the VERSION file with the version number'):
            expected = '2.0.1'
            self.settings.extra_context["version"] = expected
            self.runner.run()
            f = open(self.project_dir + '/VERSION', 'r')

            expect(f.read()).to(contain_exactly(expected))

        with it('fills the LICENSE file with the year, the full name and the email address'):
            config = get_config(SettingObject.CONFIG_FILE)
            self.runner.run()
            f = open(self.project_dir + '/LICENSE', 'r')
            actual = f.read()

            expect(actual).to(contain(config['default_context']['full_name']))
            expect(actual).to(contain(config['default_context']['email']))
            expect(actual).to(contain(datetime.now().strftime("%Y")))