import os
import threading

import time

from prototypes.Indiv import OptionsEnabled


class SsServer(OptionsEnabled):
    def __init__(self):
        super().__init__()
        self.server_index = [0, 1, 4, 5]
        self._freeze = threading.Lock()
        self.settings(freeze_interval=4)

    def shuffle_server(self):
        if self._freeze.locked():
            return
        self._freeze.acquire()
        _index = self.server_index.pop(0)
        self.change_server(_index)
        self.server_index.append(_index)
        time.sleep(self.options['freeze_interval'])
        self._freeze.release()

    @staticmethod
    def change_server(_index):
        path = 'C:/Tools/Shadowsocks/gui-config.json'
        final_lines = []
        with open(path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                if 'index' in line:
                    l, r = line.split(':')
                    _, r = r.split(',')
                    line = l + ': ' + str(_index) + ',' + r
                final_lines.append(line)
        with open(path, 'w', encoding='utf-8') as f:
            for line in final_lines:
                f.write(line)
        os.system('@ taskkill /F /IM shadowsocks.exe')
        time.sleep(1)
        os.system('start /b C:/Tools/Shadowsocks/Shadowsocks.exe')
        print(':shadowsocks:server changed.')


if __name__ == '__main__':
    pass
