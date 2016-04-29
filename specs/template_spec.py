# -*- coding: utf-8 -*-
import sys
import os
import filecmp
import re
from expects import *
from testfixtures import TempDirectory
from cookiecutter.config import get_config
from datetime import datetime

modules = [
    os.path.dirname(__file__),
    os.path.dirname(__file__) + '/support'
]
for module in modules:
    if module not in sys.path:
        sys.path.append(module)

from support.runner import Runner
from support.settings import SettingObject


def check_template_variables(subject, vars):
    """
    check a given subject contains some template variables
    :param subject: the subject to be checked for the presence of
                    template variables
    :param vars: list of template variables to look for in subject
    """
    for var in vars:
        expect(subject).to(match(r'\{\{cookiecutter\.' + var + '\}\}'))

# defaults
MAIN_DIR = os.path.realpath(os.path.dirname(__file__) + '/..')
DEFAULT_PROJECT = 'Dummy Project'
DEFAULT_PROJECT_DIR = 'cookiecutter-dummy-project'
HOOK_TEMPLATE_VARS = [
    'project_name',
    'project_slug',
    'copy_hooks'
]

with description('Cookiecutter Template'):
    with after.all:
        TempDirectory.cleanup_all()

    with before.each:
        self.tempdir = TempDirectory()
        self.output_dir = self.tempdir.path
        self.project_dir = self.output_dir + '/' + DEFAULT_PROJECT_DIR
        self.settings = SettingObject(
            {"project_name": DEFAULT_PROJECT}, self.output_dir)
        self.runner = Runner(self.settings)

    with after.each:
        self.tempdir.cleanup()

    with context('naming convention'):
        with it('names the directory using the project name rewritten in \
        kebab-case format, prefixed with \'cookiecutter-\''):
            self.runner.run()

            expect(os.path.exists(self.project_dir)).to(be_true)

        with it('issue #1 - project directory name should not been prefixed \
            if the project name starts with "cookiecutter"'):
            self.settings.extra_context[
                "project_name"] = "Cookiecutter " + DEFAULT_PROJECT
            self.runner.run()

            expect(os.path.exists(self.project_dir)).to(be_true)

    with context('file content'):
        with it('fills the VERSION file with the version number'):
            expected = '2.0.1'
            self.settings.extra_context["version"] = expected
            self.runner.run()
            f = open(self.project_dir + '/VERSION', 'r')

            expect(f.read()).to(contain_exactly(expected))

        with it('fills the LICENSE file with the year, the full name and \
        the email address'):
            config = get_config(SettingObject.CONFIG_FILE)
            self.runner.run()
            f = open(self.project_dir + '/LICENSE', 'r')
            actual = f.read()

            expect(actual).to(contain(config['default_context']['full_name']))
            expect(actual).to(contain(config['default_context']['email']))
            expect(actual).to(contain(datetime.now().strftime("%Y")))

        with it('fills the README.md project name, project description, \
        project directory name and github username'):
            config = get_config(SettingObject.CONFIG_FILE)
            expected_description = 'My dummy project short description'
            self.settings.extra_context[
                "project_short_description"] = expected_description
            self.runner.run()
            f = open(self.project_dir + '/README.md', 'r')
            actual = f.read()

            expect(actual).to(contain(DEFAULT_PROJECT))
            expect(actual).to(contain(DEFAULT_PROJECT_DIR))
            expect(actual).to(contain(expected_description))
            expect(actual).to(
                contain(config['default_context']['github_username'])
            )

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

        with it('creates the main {{cookiecutter.project_slug}} directory \
        without rendering'):
            expected = self.project_dir + "/{{cookiecutter.project_slug}}"
            self.runner.run()

            expect(os.path.exists(expected)).to(be_true)

        with context('issue #3 - the post hook should be available in \
        the generated template'):
            with before.each:
                self.settings.extra_context['copy_hooks'] = 'yes'

            with it('copies the hook file'):
                source = (MAIN_DIR + "/hooks/post_gen_project.py")
                expected = self.project_dir + "/hooks/post_gen_project.py"
                self.runner.run()

                expect(os.path.exists(expected)).to(be_true)
                expect(
                    filecmp.cmp(source, expected, shallow=False)
                ).to(be_true)

            with it('reverts template expansion'):
                self.runner.run()
                f = open(self.project_dir + "/hooks/post_gen_project.py", 'r')
                actual = f.read()

                expect(actual).not_to(contain(DEFAULT_PROJECT))
                expect(actual).not_to(contain(DEFAULT_PROJECT_DIR))
                check_template_variables(actual, HOOK_TEMPLATE_VARS)

            with it('reverts template expansion even for one word project name \
            in lower case '):
                lc_project_name = 'dummy'
                project_dir = self.project_dir[0:self.project_dir.rfind('-')]
                self.settings.extra_context['project_name'] = lc_project_name
                self.runner.run()
                f = open(project_dir + "/hooks/post_gen_project.py", 'r')
                actual = f.read()

                expect(actual).not_to(contain(lc_project_name))
                expect(actual).not_to(contain(DEFAULT_PROJECT_DIR))
                check_template_variables(actual, HOOK_TEMPLATE_VARS)

            with it('should only be duplicated for cookiecutter meta \
            templates'):
                project_dir = self.project_dir.replace('cookiecutter-', '')
                not_expected = project_dir + "/hooks/post_gen_project.py"
                self.settings.extra_context['project_slug'] = \
                    "{{ cookiecutter.project_name.lower().replace(' ', '-') }}"
                self.runner.run()

                expect(os.path.exists(project_dir)).to(be_true)
                expect(os.path.exists(not_expected)).to(be_false)
