import inspect
import queue
from prototypes.Service import Service
from utils.LogDisplay import LogDisplay


class Universe:
    def __init__(self):
        self._log = LogDisplay()

    def log(self, m_type, message):
        self._log.put((m_type, message))

    @staticmethod
    def log_exception(e):
        if 'HTTPSConnectionPool' in str(e):
            print(f'\033[0;31m:HTTPSConnectionPool Error:{repr(e)}\033[0m')
            return
        func_name = inspect.stack()[1][3]
        print(f'\033[0;31m:{func_name}()\n:{repr(e)}\033[0m')

    def activate(self):
        self._log.activate()

    def freeze(self):
        self._log.freeze()


class ToyBrick(Service):
    def __init__(self, inner=None, *forced_inners):
        super().__init__()  # shell endued

        self.input = inner.output if inner else queue.Queue()
        self.universe = inner.universe if inner else Universe()  # inner auto merged
        self._inners = [inner] if inner else []
        self._inners.extend(forced_inners)  # forced merge
        for x in forced_inners:
            x.universe = self.universe  # share the universe

        self.output = queue.Queue()
        self.fail = queue.Queue()

    def log(self, m_type, message):
        self.universe.log(m_type, message)

    def log_exception(self, e):
        self.universe.log_exception(e)

    def activate(self):
        for x in self._inners:
            x.activate()
        super().activate()
        self.log(7, f':{self.__class__.__name__} activated.')

    def freeze(self):
        for x in self._inners:
            x.freeze()
        super().freeze()
        self.log(7, f':{self.__class__.__name__} frozen.')

    def state(self):
        ret = super().state()
        if ret == 'waiting' and any([x.state() == 'processing' for x in self._inners]):
            return 'processing'
        return ret
