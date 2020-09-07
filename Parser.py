import os
import random
import sys
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from requests.adapters import ConnectTimeout, HTTPAdapter, ProxyError
from requests.models import Response

from Servises import Notify_by_Message as Nm
from Servises.Notify_by_Message import get_function_name as gfn, l_message

__version__ = sys.version[:sys.version.index(' ')]
print("Python__version__ :" + __version__)


class Parser:

    def __init__(self, urls, queries_path: str, query=None):
        self.urls = urls
        self.queries_path = queries_path
        self.query = query
        self.divs_requests: list = []  # список c ответами

        self.HEADERS = None
        self.divs = None
        self.ques = None
        self.url = None
        self.request = None

        self.proxyes: list = []  # создаем список c прокси
        self.full_path_to_file = None
        self.proxy_path = None
        self.request_timeout = None

    def url_constructor(self):
        pass

    def write_to_excel(self):
        pass

    def divs_text_shelves(self):
        pass

    def get_response(self):
        """ функция посылает запрос и получает ответ. Если ответ есть - передаёт на обработку"""

        adapter_yd = HTTPAdapter(max_retries=3)  # максимальное количество повторов запроса в сессии
        session = requests.Session()  # устанавливаем сессию
        session.mount(str(self.url), adapter_yd)

        for header in self.HEADERS:
            try:
                self.request: Response = session.get(self.url, headers=header, stream=True,
                                                     timeout=self.request_timeout)
                if self.check_request_status_code(self.request):
                    l_message(gfn(), 'Успешный запрос!', color=Nm.bcolors.OKBLUE)
                    return self.request
                else:
                    l_message(gfn(), f'Ошибка при установке соединения! проверьте HEADERS!', color=Nm.bcolors.FAIL)
                    continue

            except Exception as err:
                l_message(gfn(), f"Exception: {repr(err)}", color=Nm.bcolors.FAIL)

    def get_response_with_proxy(self):
        """ функция посылает запрос и получает ответ. Если ответ есть - передаёт на обработку"""
        time_start = None

        self.proxyes = self.generate_proxi_pool()
        assert self.proxyes is not None, "proxyes not set"

        adapter_yd = HTTPAdapter(max_retries=3)  # максимальное количество повторов запроса в сессии
        session = requests.Session()  # устанавливаем сессию
        session.mount(str(self.url), adapter_yd)

        data_request = self._create_data_request()

        for request_number, datas in enumerate(list(data_request)):
            if request_number >= 100 and datas is not None:
                continue
            try:
                for data in list(datas):
                    l_message(gfn(), f"proxy {data['proxy']}", color=Nm.bcolors.OKGREEN)
                    # self.check_ip()
                    try:
                        time_start = time.monotonic()
                        self.request: Response = session.get(self.url, headers=data['headers'], stream=data['stream'],
                                                             timeout=data['timeout'], proxies=data['proxy'])
                        self._measure_time_request(gfn(), time_start)

                        if self.check_request_status_code(self.request):
                            l_message(gfn(), 'Успешный запрос!', color=Nm.bcolors.OKBLUE)
                            return self.request
                        else:
                            l_message(gfn(), f'Ошибка при установке соединения! проверьте HEADERS!',
                                      color=Nm.bcolors.FAIL)
                            continue

                    except ConnectTimeout as err:
                        l_message(gfn(), f"ConnectTimeout: {repr(err)}", color=Nm.bcolors.FAIL)
                        l_message(gfn(), f"Connection to proxi timed out", color=Nm.bcolors.FAIL)
                        self._measure_time_request(gfn(), time_start)
                        continue

                    except ProxyError as err:
                        l_message(gfn(), f"ProxyError: {repr(err)}", color=Nm.bcolors.FAIL)
                        l_message(gfn(), f"Удалите прокси из списка: {repr(err)}", color=Nm.bcolors.FAIL)

                    except Exception as err:
                        l_message(gfn(), f"Exception: {repr(err)}", color=Nm.bcolors.FAIL)
                        l_message(gfn(), f'Bed Proxy', color=Nm.bcolors.FAIL)

            except Exception as err:
                l_message(gfn(), f"Exception: {repr(err)}", color=Nm.bcolors.FAIL)
                l_message(gfn(), f'Ошибка при установке соединения! проверьте подключение!', color=Nm.bcolors.FAIL)

    @staticmethod
    def _measure_time_request(function: str, t_start):
        """ Исмерение времени выполнения запроса"""

        ms = (time.monotonic() - t_start) * 1000
        l_message(function, f'Время request: {ms:2.2f} ms или {str(float(round(ms / 1000, 2)))} сек.',
                  color=Nm.bcolors.OKGREEN)

    def _create_data_request(self) -> list:
        """ Создание списка данных для запроса через session.get"""

        data_request: list = []
        for header in self.HEADERS:
            for proxy in self.proxyes:
                if proxy == "":
                    continue
                data_request.append({"headers": header,
                                     "proxy": {'http': proxy, 'https': proxy},
                                     "timeout": self.request_timeout * 2,
                                     "stream": True
                                     })
        yield data_request

    def check_request_status_code(self, request) -> bool:
        """ Проверка кода ответа запроса."""
        if request.status_code == 200:  # если запрос был выполнен успешно то
            l_message(gfn(), 'Успешный запрос!', color=Nm.bcolors.OKBLUE)
            return True

        elif request.status_code == 400:
            l_message(gfn(), f'BAD request {self.url} : {str(request.status_code)}', color=Nm.bcolors.FAIL)

        elif request.status_code == 406:
            l_message(gfn(), f'Client Error {self.url} : {str(request.status_code)}', color=Nm.bcolors.FAIL)

        elif 400 < request.status_code < 500:
            l_message(gfn(), f'Client Error {self.url} : {str(request.status_code)}', color=Nm.bcolors.FAIL)

        elif 500 <= request.status_code < 600:
            l_message(gfn(), f'Server Error {self.url} : {str(request.status_code)}', color=Nm.bcolors.FAIL)

        else:
            l_message(gfn(), f'Неудачный запрос! Ответ {str(request.status_code)} : {str(request.status_code)}',
                      color=Nm.bcolors.FAIL)

    def soup_request_yandex(self, ):
        """ обработка ответа с помощью BeautifulSoup. Если есть нужные данные - передаёт на поиск нужных данных в
            divs_text_shelves """

        if hasattr(self.request, 'text') and self.request.text != '':
            soup = BeautifulSoup(self.request.text, 'lxml')  # ответ
            self.divs = soup.find_all('li', class_='serp-item')  # данные ответа

        if self.divs is None:
            l_message(gfn(), 'Ответ не содержит нужных данных :(', color=Nm.bcolors.FAIL)
            return

        l_message(gfn(), f'Всего найдено блоков ' + str(len(self.divs)), color=Nm.bcolors.OKBLUE)

    def soup_request_google(self, ):
        """ обработка ответа с помощью BeautifulSoup. Если есть нужные данные - передаёт на поиск нужных данных в
            divs_text_shelves """

        if hasattr(self.request, 'text') and self.request.text != '':
            soup = BeautifulSoup(self.request.text, 'lxml')  # ответ
            self.divs = soup.find_all('li', class_='ads-fr')  # данные ответа

        if self.divs is None or len(self.divs) == 0:
            l_message(gfn(), 'Ответ не содержит нужных данных :(', color=Nm.bcolors.FAIL)
            return

        l_message(gfn(), f'Всего найдено блоков ' + str(len(self.divs)), color=Nm.bcolors.OKBLUE)

    @staticmethod
    def _time_rand(t_start: int = 1, t_stop: int = 30):
        """функция задержки выполнения кода на рандомный промежуток """

        time_random = random.randint(t_start, t_stop)
        l_message(gfn(), f'Время ожидания нового запроса time_rand  {str(time_random)} sec', color=Nm.bcolors.OKBLUE)

        for _ in range(time_random):
            time.sleep(random.uniform(0.8, 1.2))

    @staticmethod
    def create_patch(*, path=None):
        """ Создание папки по пути"""

        os.mkdir(path)
        l_message(gfn(), f'Файл создан в {path}', color=Nm.bcolors.OKBLUE)

    @staticmethod
    def check_folder(*, path: str) -> bool:
        """  Проверка файл или каталог """

        if not os.path.exists(path):
            l_message(gfn(), f'Файл не найден', color=Nm.bcolors.OKBLUE)
            return False

    def check_and_remove_file(self):
        """ Проверка существования файла. Если файла существует - удаляем."""
        if os.path.exists(self.full_path_to_file):  # файл excel существует то удаляем
            os.remove(self.full_path_to_file)

    @staticmethod
    def date_tudselfay():
        """ Возвращаем текущую дату"""

        return datetime.today().strftime("%d.%m.%Y")

    @staticmethod
    def check_ip():
        """Check my public IP via tor."""
        l_message(gfn(), f'My public IP {requests.get("http://www.icanha4zip.com").text[:-2]}', color=Nm.bcolors.OKBLUE)
        return

    def generate_proxi_pool(self):
        """Создаём пул прокси"""

        # открываем файл с ключами по пути queries_path и считываем ключи
        with open(self.proxy_path, 'r', encoding='utf-8') as file:
            return [x.strip() for x in file if x != ""]

# def main():
#     pass
#
#
# if __name__ == '__main__':
#     main()
