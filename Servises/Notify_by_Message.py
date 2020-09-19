import inspect
import os
import tkinter
import traceback
from os import system
from tkinter import LEFT, WORD

from plyer.platforms.win.libs.balloontip import WindowsBalloonTip

from Servises.log_main import log_vis_rec

__version__ = '2'
__all__ = 'GeneralMessage'
__target_name__ = 'Parser_Yandex'
__app_name__ = 'Parser'

VIS_LOG = False  # True -  Отображение хода процесса в консоли
PRINT_LOG = True  # True -  Запись лога в файл


def walk_up_folder(path, depth=1):
    """Получение пути на заданный уровень от местонахождения текущего файла."""

    _cur_depth = 1
    while _cur_depth < depth:
        path = os.path.dirname(path)
        _cur_depth += 1
    return path


this_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
current_dir = walk_up_folder(this_dir, depth=2)
CURRENT_DIR = current_dir + '\\'


class BColors:  # colors in console
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class TkBcolors:  # colors in console
    HEADER = 'LightMagenta'  # '\033[95m'
    OKBLUE = 'LightBlue'  # '\033[94m'
    OKGREEN = 'LightGreen'  # '\033[92m'
    WARNING = 'LightYellow'  # '\033[93m'
    FAIL = 'Red'  # '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def decorate_msg(msg, color=None):
    """     Returns: colored msg, if colors are enabled in config and a color is provided for msg
             msg, otherwise     """

    msg_string = msg
    if config['colors']:
        msg_string = color + msg + BColors.ENDC
    return msg_string


config = {'get_main_interval': 6,
          'get_reConnect_interval': 5,  # Time (seconds). Recommended value: 5
          'colors': True,  # True/False. True prints colorful msgs in console
          }


class GeneralMessage:
    """ Уведомления и оповещения доступными соредствами """

    def __init__(self, message: str, *, period: int = config['get_main_interval'], app_name=None,
                 color=TkBcolors.OKBLUE):
        self.message = message
        self.period = period * 1000
        self.color = color
        self.app_name = app_name
        self.work()

    def work(self):
        """ Уведомление доступными средствами"""

        try:
            #  уведомление в центре уведомлений
            self.toast_message(self.message, duration=self.period, app_name=self.app_name)
        except Exception as err:
            print(decorate_msg(f" def 'toast_message' not available | \n"
                               f" Unexpected exception: {repr(err)}", BColors.FAIL))
            try:
                #  уведомление с помощью окна tkinter
                self.main_message(self.message, self.period, self.color)
            except Exception as err:
                print(decorate_msg(f" def 'main_message' not available | \n"
                                   f" Unexpected exception: {repr(err)}", BColors.FAIL))
                #  уведомление MSG.exe
                self.notify(self.message)

    @staticmethod
    def notify(message: str):
        """
        Функция создаёт окно оповещения средствами MSG.exe
        :param message: str - Тело сообщения
        """
        # notify(message, title=None, subtitle=None):
        # t = 'title {!r}'.format(title)
        # s = 'subtitle {!r}'.format(subtitle)
        # m = 'message {!r}'.format(message)
        # os.system('MSG.exe *  /TIME:10 message = {}'.format(' '.join([m, t, s])))
        system('MSG.exe *  /TIME:5 message = {}'.format(' '.join([message])))

    @staticmethod
    def main_message(message: str, period: int = config['get_main_interval'] * 1000, color=TkBcolors.OKBLUE):
        """Функция создаёт окно оповещения средствами tkinter
        :param color: цвет уведлмления сообщения
        :param message: str - Тело сообщения
        :param period: int - продолжительность показа в мс
        :type message: object
        """
        root = tkinter.Tk()
        w, h = 0, 0
        root.geometry('400x170+{}+{}'.format(w, h))
        root.title("info")

        root.textEditor = tkinter.Text(root, width=200, height=50, font='Arial 12', wrap=WORD, bg=color, fg='white')
        root.textEditor.pack(side=LEFT)
        root.textEditor.insert(1.0, message)

        tkinter.Label(root, text=message).pack()
        root.after(period, lambda: root.destroy())  # time in ms
        root.mainloop()

    @staticmethod
    def toast_message(message: str, duration: int = config['get_main_interval'], app_name: str = None):
        """Функция создаёт оповещение в центре оповещений Windows
        :param duration: int  время показа сообщения
        :param message: str - Тело сообщения
        :param app_name: str - имя вызывающего приложения
        :type message: object
        """

        WindowsBalloonTip(title=app_name,
                          message=message,
                          app_name=app_name,
                          app_icon=app_name + ".ico",
                          timeout=duration)


def l_message(names=None, value=None, color=None, r_log=None, r_print=None):
    """Функция логирования в файл и отображения данны в терминале"""

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


def get_function_name():
    """ Получение имени вызываемой функции"""

    return [str(traceback.extract_stack(None, 2)[0][2]),
            str(traceback.extract_stack(None, 2)[0][0]).replace('.py', '').split('/')[-1]]
