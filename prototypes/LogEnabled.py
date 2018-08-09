class LogEnabled(object):
    def __init__(self, display_module=None):
        self.log = display_module

    def _log(self, status, text):
        if self.log:
            self.log.put((status, text))
