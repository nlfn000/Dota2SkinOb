import threading


class Service:
    def __init__(self):
        self._off = threading.Event()
        self._off.set()

    def _is_frozen(self):
        return self._off.is_set()

    def freeze(self):
        self._off.set()

    def activate(self):
        if not self._is_frozen():  # for security
            return
        t = threading.Thread(target=self.__service_thread)
        t.start()

    def __service_thread(self):
        self._off.clear()
        t = threading.Thread(target=self._service)
        t.setDaemon(True)
        t.start()
        self._off.wait()

    def _service(self):
        # replace it with target service
        pass
