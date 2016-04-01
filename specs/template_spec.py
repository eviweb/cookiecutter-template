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

with description('Cookiecutter Template'):
    with after.all:
        TempDirectory.cleanup_all()

    with before.each:
        self.tempdir = TempDirectory()
        self.output_dir = self.tempdir.path
        self.settings = SettingObject(None, self.output_dir)
        self.runner = Runner(self.settings)

    with after.each:
        self.tempdir.cleanup()

    with context('naming convention'):
        with it('names the directory using the project name rewritten in kebab-case format, prefixed with \'cookiecutter-\''):
            project_name = 'Dummy Project'
            expected = 'cookiecutter-dummy-project'
            self.settings.extra_context = {"project_name": project_name}
            self.runner.run()

            expect(os.path.exists(self.output_dir + '/' + expected)).to(be_true)
        