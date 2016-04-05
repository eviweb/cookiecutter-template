from cookiecutter.main import cookiecutter

class Runner:
    def __init__(self, settings):
        self.settings = settings

    def run(self):
        cookiecutter(
            self.settings.template,
            self.settings.checkout,
            self.settings.no_input,
            self.settings.extra_context,
            self.settings.replay,
            self.settings.overwrite_if_exists,
            self.settings.output_dir,
            self.settings.config_file
        )
