""" Декоратор измерения времени работы функции.
"""
import time
from functools import wraps
from pprint import pprint

print(f'Invoking __init__.py for {__name__}')


def timeit(method):
    """ Деоратор измерения времени работы функции.
    """

    @wraps(method)
    def timed(*args, **kw):
        time_seconds = time.monotonic()
        result = method(*args, **kw)
        milli_seconds = (time.monotonic() - time_seconds) * 1000
        sec: float = round(milli_seconds / 1000, 2)

        all_args = ', '.join(tuple(f'{k}={v!r}' for k, v in kw.items()))
        pprint(
            'Время выполнения функции *** ' + f'{method.__name__}({all_args}) *** : {milli_seconds:2.2f} ms или ' + str(
                sec) + 'сек.')
        return result

    return timed
