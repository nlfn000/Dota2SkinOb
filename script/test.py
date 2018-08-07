import threading
import time


def func1():
    with open('../data/proxies/proxies.dat', 'r') as f:
        time.sleep(5)

t = threading.Thread(target=func1)
t.start()
for i in range(15):
    with open('../data/proxies/proxies.dat', 'r') as f:
        f.close()
        print(f.closed)

