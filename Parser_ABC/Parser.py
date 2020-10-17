"""
МОдуль с основным базовым классом Parser от которого наследуются в се парсеры
"""

import os
import random
import sys
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from requests.adapters import ConnectTimeout, HTTPAdapter, ProxyError
from requests.models import Response

from Servises.Notify_by_Message import BColors
from Servises.Notify_by_Message import get_function_name as gfn
from Servises.Notify_by_Message import l_message

__version__ = sys.version[:sys.version.index(' ')]
print("Python__version__ :" + __version__)
print(f'Invoking __init__.py for {__name__}')


class Parser:
    """ Базовый класс парсера.
    """

    def __init__(self, urls, queries_path: str, query=None):

        self.urls = urls
        self.queries_path = queries_path
        self.query = query
        self.divs_requests: list = []  # список c ответами
        self.result: list = []

        self.headers = None
        self.divs = None
        self.ques = None
        self.url = None
        self.request = None
        self.session = None

        self.proxyes: list = []  # создаем список c прокси
        self.full_path_to_file = None
        self.proxy_path = None
        self.request_timeout = None

        self.soup_name = None
        self.soup_class = None
        self.soup_attribute = None

    def start_work(self):
        """ Определение начало работы в базовом классе.
        """
        assert self.urls is not None, f"{gfn()} urls not passed"

        for number, item_url in enumerate(self.urls):
            l_message(gfn(), f"\nЗапрос номер: {number + 1} \n", color=BColors.OKBLUE)

            try:
                self.url = item_url['url']
                self.ques = item_url['ques']

                if number <= 100:
                    self.get_response()
                else:
                    self.proxyes = self.get_proxy_pool_from_file()
                    self.get_response_with_proxy()

                self.soup_request()  # обработка ответа сервера

                if self.divs is not None:
                    self.divs_text_shelves()
                    self.result.extend(list(self.divs_requests))
                self._time_rand(2, 4)

            except ConnectionError as err:
                l_message(gfn(), f" ConnectionError: {repr(err)}", color=BColors.FAIL)
                continue

        self.write_data_to_file()

    def write_data_to_file(self):
        """ Запись в файл excel.
        """
        raise NotImplementedError(f'Определите {gfn()} в {self.__class__.__name__}')

    def divs_text_shelves(self):
        """ Поиск данных в ответе сервера.
        """
        raise NotImplementedError(f'Определите {gfn()} в {self.__class__.__name__}')

    def get_session(self):
        """ Создание сессии.
        """
        adapter_yd = HTTPAdapter(max_retries=3)  # максимальное количество повторов запроса в сессии
        self.session = requests.Session()  # устанавливаем сессию
        self.session.mount(str(self.url), adapter_yd)

        return self.session

    def close_session(self):
        """ Закрываем сессию.
        """
        return self.session.close()

    def get_response(self):
        """ Функция посылает запрос и получает ответ. Если ответ есть - передаёт на обработку.
        """
        for header in self.headers:
            try:
                self.session = self.get_session()
                self.request: Response = self.session.get(self.url, headers=header, stream=True,
                                                          timeout=self.request_timeout)
                if self.check_request_status_code(self.request):
                    l_message(gfn(), 'Успешный запрос!', color=BColors.OKBLUE)
                    self.close_session()
                    return self.request
                else:
                    l_message(gfn(), 'Ошибка при установке соединения! проверьте HEADERS!', color=BColors.FAIL)
                    continue

            except Exception as err:
                l_message(gfn(), f"Exception: {repr(err)}", color=BColors.FAIL)

    def get_response_with_proxy(self):
        """ Функция посылает запрос и получает ответ. Если ответ есть - передаёт на обработку.
        """
        time_start = None

        self.proxyes = self.get_proxy_pool_from_file()
        assert self.proxyes is not None, "proxyes not set"

        data_requests = self._create_data_request()

        for request_number, item_request in enumerate(list(data_requests)):

            if request_number >= 100:
                return

            for item_data in list(item_request):
                l_message(gfn(), f"proxy {item_data['proxy']}", color=BColors.OKGREEN)
                try:
                    time_start = time.monotonic()
                    session = self.get_session()
                    self.request: Response = session.get(self.url,
                                                         headers=item_data['headers'],
                                                         stream=item_data['stream'],
                                                         timeout=item_data['TIMEOUT'],
                                                         proxies=item_data['proxy'])
                    self._measure_time_request(str(gfn()), time_start)

                    if self.check_request_status_code(self.request):
                        return self.request
                    else:
                        l_message(gfn(), 'Ошибка при установке соединения! проверьте HEADERS!',
                                  color=BColors.FAIL)
                        continue

                except ConnectTimeout as err:
                    l_message(gfn(), f"ConnectTimeout: {repr(err)}", color=BColors.FAIL)
                    l_message(gfn(), "Connection to proxy timed out", color=BColors.FAIL)
                    self._measure_time_request(str(gfn()), time_start)
                    continue

                except ProxyError as err:
                    l_message(gfn(), f"ProxyError: {repr(err)}", color=BColors.FAIL)
                    l_message(gfn(), f"Удалите прокси из списка: {repr(err)}", color=BColors.FAIL)

    @staticmethod
    def _measure_time_request(function: str, t_start):
        """ Исмерение времени выполнения запросаю
        """
        micro_seconds = (time.monotonic() - t_start) * 1000
        l_message(function,
                  f'Время request: {micro_seconds:2.2f} ms или {str(float(round(micro_seconds / 1000, 2)))} сек.',
                  color=BColors.OKGREEN)

    def _create_data_request(self):
        """ Создание списка данных для запроса через session.get.
        """
        data_request: list = []
        for header in self.headers:
            for proxy in self.proxyes:
                if proxy == "":
                    continue
                data_request.append({"headers": header,
                                     "proxy": {'http': proxy, 'https': proxy},
                                     "TIMEOUT": self.request_timeout * 2,
                                     "stream": True
                                     })
        yield data_request

    def check_request_status_code(self, request) -> bool:
        """ Проверка кода ответа запроса.
        """
        if request.status_code == 200:  # если запрос был выполнен успешно то
            l_message(gfn(), 'Успешный запрос!', color=BColors.OKBLUE)
            return True

        elif request.status_code == 400:
            l_message(gfn(), f'BAD request {self.url} : {str(request.status_code)}', color=BColors.FAIL)
            return False

        elif request.status_code == 406:
            l_message(gfn(), f'Client Error {self.url} : {str(request.status_code)}', color=BColors.FAIL)
            return False

        elif 406 < request.status_code < 500:
            l_message(gfn(), f'Client Error {self.url} : {str(request.status_code)}', color=BColors.FAIL)
            return False

        elif 500 <= request.status_code < 600:
            l_message(gfn(), f'Server Error {self.url} : {str(request.status_code)}', color=BColors.FAIL)
            return False

        else:
            l_message(gfn(), f'Неудачный запрос! Ответ {str(request.status_code)} : {str(request.status_code)}',
                      color=BColors.FAIL)
            return False

    def soup_request(self):
        """ Обработка ответа с помощью BeautifulSoup. Если есть нужные данные - передаёт на поиск нужных данных в
            divs_text_shelves.
        """
        if not hasattr(self.request, self.soup_attribute):
            l_message(gfn(), 'Ответ не содержит текст :(', color=BColors.FAIL)
            return

        if self.request.text == '':
            l_message(gfn(), 'Ответ не содержит текстовых данных :(', color=BColors.FAIL)
            return

        soup = BeautifulSoup(self.request.text, 'lxml')  # ответ
        self.divs = soup.find_all(self.soup_name, class_=self.soup_class)  # данные ответа

        if self.divs is None or len(self.divs) == 0:
            l_message(gfn(), 'Ответ не содержит нужных данных :(', color=BColors.FAIL)
            return

        l_message(gfn(), f'Всего найдено блоков {str(len(self.divs))}', color=BColors.OKBLUE)

    @staticmethod
    def _time_rand(t_start: int = 1, t_stop: int = 30):
        """ Функция задержки выполнения кода на рандомный промежутокю
        """
        time_random = random.randint(t_start, t_stop)
        l_message(gfn(), f'Время ожидания нового запроса time_rand  {str(time_random)} sec', color=BColors.OKBLUE)

        for _ in range(time_random):
            time.sleep(random.uniform(0.8, 1.2))

    @staticmethod
    def create_patch(*, path=None):
        """ Создание папки по пути.
        """
        os.makedirs(path)
        l_message(gfn(), f'Файл создан в {path}', color=BColors.OKBLUE)

    @staticmethod
    def check_folder(*, path: str) -> bool:
        """ Проверка файл или каталог.
        """
        if not os.path.exists(path):
            l_message(gfn(), 'Файл не найден', color=BColors.OKBLUE)
            return False
        return True

    def check_and_remove_file(self):
        """ Проверка существования файла. Если файла существует - удаляем.
        """
        if os.path.exists(self.full_path_to_file):  # файл excel существует то удаляем
            os.remove(self.full_path_to_file)

    @staticmethod
    def date_today():
        """ Возвращаем текущую дату.
        """
        return datetime.today().strftime("%d.%m.%Y")

    @staticmethod
    def check_ip():
        """Check my public IP via tor.
        """
        l_message(gfn(), f'My public IP {requests.get("http://www.icanha4zip.com").text[:-2]}', color=BColors.OKBLUE)

    def get_proxy_pool_from_file(self):
        """Создаём пул прокси.
        """
        # открываем файл с ключами по пути queries_path и считываем ключи
        with open(self.proxy_path, 'r', encoding='utf-8') as file:
            return [x.strip() for x in file if x != ""]
