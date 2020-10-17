from Servises import FannyBot as Fb  # файл с приколами
from Servises import ModuleReloder
from Servises import Notify_by_Message as Nm  # файл с уведомлниями
from Servises import log_main
from Servises import timeit

print(f'Invoking __init__.py for {__name__}')

__all__ = [
    'log_main',
    'ModuleReloder',
    'Notify_by_Message',
    'timeit'
]
