import threading


def start_new_thread(func, args):
    t = threading.Thread(target=func, args=args)
    t.start()
