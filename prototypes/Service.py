import threading

from prototypes.Indiv import Individualized


class Service(Individualized):
    """
        basic Service prototype.
    """

    def __init__(self):
        super().__init__()
        self._frozen = threading.Event()
        self._processing = threading.Event()
        self._frozen.set()

    def state(self):
        if self._frozen.is_set():
            return 'frozen'
        if self._processing.is_set():
            return 'processing'
        return 'waiting'

    def freeze(self):
        self._frozen.set()  # forced shutdown

    def activate(self):
        if self.state() == 'frozen':
            t = threading.Thread(target=self._service_thread)
            t.start()

    def _service_thread(self):
        self._frozen.clear()
        t = threading.Thread(target=self._service)
        t.setDaemon(True)
        t.start()
        self._frozen.wait()

    def _service(self):
        # do nothing
        return
