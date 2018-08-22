import inspect
import queue
import threading
import time

from prototypes.Service import Service
from utils.LogDisplay import LogDisplay


class Universe(Service):
    def __init__(self):
        super().__init__()
        self._log = LogDisplay()
        self.tasks = queue.Queue()
        self.dropped = queue.Queue()
        self.receiver = queue.Queue()

    def _service_thread(self):
        self._frozen.clear()
        t1 = threading.Thread(target=self._receive)
        t1.setDaemon(True)
        t1.start()
        t2 = threading.Thread(target=self._monitor)
        t2.setDaemon(True)
        t2.start()
        self._frozen.wait()

    def _receive(self):
        while True:
            data = self.receiver.get()
            print(f'taskdone:{data}')
            self.tasks.task_done()

    def _monitor(self):
        while True:
            _unfinished = self.tasks.unfinished_tasks
            _rest = self.tasks.qsize()
            _received = self.receiver.unfinished_tasks
            _dropped = self.dropped.qsize()
            _processing = _unfinished - _rest
            _total = _rest + _received + _dropped
            self.log(4, f'{_processing} of {_unfinished} processing.({_received} received /{_dropped} dropped)')
            if _total != 0:
                self.log_bar(_received, _processing, _rest, _dropped)
            time.sleep(4)

    def join(self):
        self.tasks.join()

    def drop(self, data):
        self.dropped.put(data)

    def activate(self):
        self._log.activate()
        super().activate()

    def freeze(self):
        self._log.freeze()
        super().freeze()

    def log_bar(self, *args):
        _total = sum(args)
        args = [x / _total for x in args]
        self._log.log_bar(*args)

    def log(self, m_type, message):
        self._log.put((m_type, message))

    @staticmethod
    def log_exception(e):
        if 'HTTPSConnectionPool' in str(e):
            print(f'\033[0;31m:HTTPSConnectionPool Error:{repr(e)}\033[0m')
            return
        func_name = inspect.stack()[1][3]
        print(f'\033[0;31m:{func_name}()\n:{repr(e)}\033[0m')


class Cell(Service):
    def __init__(self, inner=None):
        super().__init__()  # shell endued

        self.universe = inner.universe if inner else Universe()  # inner auto merged

        self._input = inner.output if inner else queue.Queue()  # local _input
        self._inners = [inner] if inner else []

        self.input = inner.input if inner else self._input  # global input
        self.output = queue.Queue()
        self.fail = queue.Queue()

    def join_input(self, inner, recur=False):
        if recur:
            inner.output = self.input
        else:
            inner.output = self._input
        self.forced_connection(inner)

    def forced_connection(self, inner):
        self._inners.append(inner)  # forced merge
        inner.universe = self.universe  # share the universe

    def log(self, m_type, message):
        self.universe.log(m_type, message)

    def log_exception(self, e):
        self.universe.log_exception(e)

    def activate(self, enable_log=True):
        for x in self._inners:
            x.activate(enable_log)
        super().activate()
        if enable_log:
            self.log(7, f':{self.__class__.__name__} activated.')

    def freeze(self, enable_log=True):
        for x in self._inners:
            x.freeze(enable_log)
        super().freeze()
        if enable_log:
            self.log(7, f':{self.__class__.__name__} frozen.')

    def state(self):
        ret = super().state()
        if ret == 'waiting' and any([x.state() == 'processing' for x in self._inners]):
            return 'processing'
        return ret
