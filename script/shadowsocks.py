import os
import time


def change_server():
    path = 'C:/Tools/Shadowsocks/gui-config.json'
    final_lines = []
    with open('../data/tmp/shadowsocks.lock', 'r') as f:
        text = f.readline()
        if int(text) == 1:
            return
    with open(path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            if 'index' in line:
                l, r = line.split(':')
                num, r = r.split(',')
                num = int(num.strip())
                index = num + 1 if num < 5 else 0
                line = l + ': ' + str(index) + ',' + r
            final_lines.append(line)
    with open(path, 'w', encoding='utf-8') as f:
        for line in final_lines:
            f.write(line)
    os.system('@ taskkill /F /IM shadowsocks.exe')
    with open('../data/tmp/shadowsocks.lock', 'w') as f:
        f.write('1')
    time.sleep(3)
    with open('../data/tmp/shadowsocks.lock', 'w') as f:
        f.write('0')
    os.system('start /b C:/Tools/Shadowsocks/Shadowsocks.exe')
    print(':shadowsocks:server changed.')

# change_server()
