import time
from functools import wraps
from pprint import pprint


def timeit(method):
    """Деоратор отображения времени работы функции"""

    @wraps(method)
    def timed(*args, **kw):
        ts = time.monotonic()
        result = method(*args, **kw)
        ms = (time.monotonic() - ts) * 1000
        sec: float = round(ms / 1000, 2)

        all_args = ', '.join(tuple(f'{k}={v!r}' for k, v in kw.items()))
        pprint('Время выполнения функции *** ' + f'{method.__name__}({all_args}) *** : {ms:2.2f} ms или ' + str(
            sec) + 'сек.')
        return result

    return timed
