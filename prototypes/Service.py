import threading


class Service:
    def __init__(self):
        self._freeze = threading.Event()
        self._freeze.set()

    def is_frozen(self):
        return self._freeze.is_set()

    def freeze(self):
        self._freeze.set()

    def activate(self, **supply_options):
        t = threading.Thread(target=self._service, kwargs=supply_options)
        t.start()

    def _service(self, target=None, **supply_options):
        self._freeze.clear()
        t = threading.Thread(target=target, kwargs=supply_options)
        t.setDaemon(True)
        t.start()
        self._freeze.wait()


if __name__ == '__main__':
    s = Service()
    print(s.is_frozen())
