class OptionsEnabled:
    def __init__(self):
        self.options = {}

    def settings(self, **kwargs):
        self.options.update(kwargs)
