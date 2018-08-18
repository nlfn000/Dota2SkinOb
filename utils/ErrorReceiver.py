import inspect
import traceback


def handle_error(e):  # trash func!
    if 'HTTPSConnectionPool' in str(e):
        print(f'\033[0;31m:HTTPSConnectionPool Error:{repr(e)}\033[0m')
        return
    func_name = inspect.stack()[1][3]
    print(f'\033[0;31m:{func_name}()\n:{repr(e)}\033[0m')
    detail = traceback.format_exc().replace('\n', ':')
    print(f'\033[0;31m:{detail}\033[0m')
