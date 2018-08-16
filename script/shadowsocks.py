import os
import time


def change_server():
    path = 'C:/Tools/Shadowsocks/gui-config.json'
    final_lines = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            if 'index' in line:
                l, r = line.split(':')
                num, r = r.split(',')
                num = int(num.strip())
                index = num + 1 if num < 5 else 0
                if index == 2:
                    index = 3
                line = l + ': ' + str(index) + ',' + r
            final_lines.append(line)
    with open(path, 'w', encoding='utf-8') as f:
        for line in final_lines:
            f.write(line)
    os.system('@ taskkill /F /IM shadowsocks.exe')
    time.sleep(2)
    os.system('start /b C:/Tools/Shadowsocks/Shadowsocks.exe')
    print(':shadowsocks:server changed.')
