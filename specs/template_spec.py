import sys, os, filecmp, re

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

MAIN_DIR = os.path.realpath(os.path.dirname(__file__) + '/..')
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

        with it('fills the README.md project name, project descritpion, project directory name and github username'):
            config = get_config(SettingObject.CONFIG_FILE)
            expected_description = 'My dummy project short descritpion'
            self.settings.extra_context["project_short_description"] = expected_description
            self.runner.run()
            f = open(self.project_dir + '/README.md', 'r')
            actual = f.read()

            expect(actual).to(contain(DEFAULT_PROJECT))
            expect(actual).to(contain(DEFAULT_PROJECT_DIR))
            expect(actual).to(contain(expected_description))
            expect(actual).to(contain(config['default_context']['github_username']))

        with it('formats correctly the project title in the README.md file'):
            expected = ''.center(len(DEFAULT_PROJECT), '=')
            self.runner.run()
            f = open(self.project_dir + '/README.md', 'r')

            expect(f.read()).to(match(r"^" + re.escape(expected) + r"$", re.M))

    with context('existing files and directories'):
        with it('creates a CHANGELOG.md file'):
            expected = self.project_dir + "/CHANGELOG.md"
            self.runner.run()

            expect(os.path.exists(expected)).to(be_true)

        with it('creates the main cookiecutter.json file without rendering'):
            expected = "\"project_slug\": \"{{ cookiecutter.project_name.lower().replace(' ', '-') }}\","
            self.runner.run()
            f = open(self.project_dir + '/cookiecutter.json', 'r')

            expect(f.read()).to(contain(expected))

        with it('creates the main {{cookiecutter.project_slug}} directory without rendering'):
            expected = self.project_dir + "/{{cookiecutter.project_slug}}"
            self.runner.run()

            expect(os.path.exists(expected)).to(be_true)