import threading

from prototypes.Indiv import Individualized


class Service(Individualized):
    """
        basic Service prototype.
    """

    def __init__(self):
        super().__init__()
        self._off = threading.Event()
        self._processing = threading.Event()
        self._off.set()

    # def warm_set(self):

    def is_frozen(self):
        return self._off.is_set()

    def freeze(self):
        self._off.set()  # forced shutdown

    def activate(self):
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
