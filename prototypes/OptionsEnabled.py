class OptionsEnabled:
    def __init__(self):
        self.options = {}

    def settings(self, **kwargs):
        print(kwargs)
        self.options.update(kwargs)
