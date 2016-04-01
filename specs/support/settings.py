from os import path

class SettingObject:
    TEMPLATE = path.realpath(path.dirname(__file__) + '/../..')
    CONFIG_FILE = path.realpath(path.dirname(__file__) + '/../fixtures/cookiecutterrc')

    def __init__(self, extra_context=None, output_dir=u'.', config_file=CONFIG_FILE):
        self.template = SettingObject.TEMPLATE
        self.checkout = None
        self.no_input = True
        self.extra_context = extra_context
        self.replay = False
        self.overwrite_if_exists = False
        self.output_dir = output_dir
        self.config_file = config_file
