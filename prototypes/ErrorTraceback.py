import inspect
import traceback


def ErrorTraceback(e):
    if 'HTTPSConnectionPool' in str(e):
        return
    funcName = inspect.stack()[1][3]
    print(f'\033[0;31m:{funcName}()\n:{repr(e)}\033[0m')
    detail = traceback.format_exc().replace('\n', ':')
    print(f'\033[0;31m:{detail}\033[0m')
