import inspect
import os
import tkinter
import traceback
from os import system
from tkinter import LEFT, WORD
from typing import List

from plyer.platforms.win.libs.balloontip import WindowsBalloonTip

from Servises.log_main import log_vis_rec

__version__ = '27.09'
__all__ = 'GeneralMessage'

print(f'Invoking __init__.py for {__name__}')

VIS_LOG = True  # True -  Отображение хода процесса в консоли
PRINT_LOG = True  # True -  Запись лога в файл

config = {'get_main_interval': 6,
          'get_reConnect_interval': 5,  # Time (seconds). Recommended value: 5
          'colors': True,  # True/False. True prints colorful msgs in console
          }


def walk_up_folder(path, depth=1):
    """ Получение пути на заданный уровень от местонахождения текущего файла.
    """

    _cur_depth = 1
    while _cur_depth < depth:
        path = os.path.dirname(path)
        _cur_depth += 1
    return path


this_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
current_dir = walk_up_folder(this_dir, depth=2)
CURRENT_DIR = current_dir + '\\'


class BColors:  # colors in console
    """ Список кодов основных цветов для системных сообщений.
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class TkBcolors:  # colors in console
    """Список кодов основных цветов для всплывающих сообщений в центре уведомлений.
    """
    HEADER = 'LightMagenta'  # '\033[95m'
    OKBLUE = 'LightBlue'  # '\033[94m'
    OKGREEN = 'LightGreen'  # '\033[92m'
    WARNING = 'LightYellow'  # '\033[93m'
    FAIL = 'Red'  # '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def decorate_msg(msg, color=None) -> str:
    """ Returns: colored msg, if colors are enabled in config and a color is provided for msg
        msg, otherwise
    """

    msg_string = msg
    if config['colors']:
        msg_string = color + msg + BColors.ENDC
    return msg_string


class GeneralMessage:
    """ Уведомления и оповещения доступными средствами.
        toast_message - уведомления в центре уведомлений Windows (Windows API)
        main_message - уведомления c помощью всплывающего окта Tkinter
        notify - уведомления c встроенными средствами Windows (system('MSG.exe')
    """

    def __init__(self, message: str, *, period: int = config['get_main_interval'], app_name=None,
                 color=TkBcolors.OKBLUE):
        self.message = message
        self.period = period
        self.color = color
        self.app_name = app_name
        self.work()

    def work(self) -> None:
        """ Уведомление доступными средствами.
        """

        try:
            #  уведомление в центре уведомлений
            self.toast_message()
        except Exception as err:
            l_message(get_function_name(), f" def 'toast_message' not available | \n"
                                           f" Unexpected exception: {repr(err)}", BColors.FAIL)

            try:
                #  уведомление с помощью окна tkinter
                self.main_message()
            except Exception as err:
                l_message(get_function_name(), f"Except Exception: {repr(err)}", color=BColors.FAIL)
                print(decorate_msg(f" def 'main_message' not available | \n"
                                   f" Unexpected exception: {repr(err)}", BColors.FAIL))
                #  уведомление MSG.exe
                self.notify()

    def notify(self):
        """ Функция создаёт окно оповещения средствами MSG.exe.
        """
        system('MSG.exe *  /TIME:5 message = {}'.format(' '.join([self.message])))
        l_message(get_function_name(), self.message, color=BColors.OKGREEN)

    def main_message(self) -> None:
        """ Функция создаёт окно оповещения средствами tkinter.
        """
        root = tkinter.Tk()
        width, height = 0, 0
        root.geometry('400x170+{}+{}'.format(width, height))
        root.title("info")

        root.textEditor = tkinter.Text(root, width=200, height=50, font='Arial 12', wrap=WORD, bg=self.color,
                                       fg='white')
        root.textEditor.pack(side=LEFT)
        root.textEditor.insert(1.0, self.message)

        tkinter.Label(root, text=self.message).pack()
        root.after(self.period, lambda: root.destroy())  # time in ms
        root.mainloop()

    def toast_message(self) -> None:
        """ Функция создаёт оповещение в центре оповещений Windows.
        """
        try:
            WindowsBalloonTip(title=self.app_name,
                              message=self.message,
                              app_name=self.app_name,
                              app_icon=self.app_name + ".ico",
                              timeout=self.period)
        except Exception as err:
            l_message(get_function_name(), f"Exception Could not load icon: {repr(err)}", color=BColors.FAIL)
            WindowsBalloonTip(title=self.app_name,
                              message=self.message,
                              app_name=self.app_name,
                              app_icon='',
                              timeout=self.period)


def l_message(names=None, value=None, color=None, r_log=None, r_print=None) -> None:
    """ Функция логирования в файл и отображения данны в терминале.
    """

    if isinstance(r_log, type(None)):
        r_log = VIS_LOG
    if isinstance(r_print, type(None)):
        r_print = PRINT_LOG

    name = names[0]
    dir_function = names[1]

    log_vis_rec(param_name=name, p_value=value, d_path=dir_function, r_log=r_log, r_print=r_print)

    if not color:
        return

    try:
        if isinstance(name, str):
            print(decorate_msg(str(name) + ' ' + str(value), color))
        else:
            print(decorate_msg(str(name), color))
    except TypeError as err:
        print(decorate_msg("lm " + name + f" TypeError: {repr(err)}", BColors.FAIL))


def get_function_name() -> List[str]:
    """ Получение имени вызывающей функции.
    :rtype: object
    """

    return [str(traceback.extract_stack(None, 2)[0][2]),
            str(traceback.extract_stack(None, 2)[0][0]).replace('.py', '').split('/')[-1]]
