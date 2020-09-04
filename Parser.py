import os
import random
import time

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.models import Response

import general_setting as gs
from Servises import Notify_by_Message as Nm
from Servises.Notify_by_Message import get_function_name as gfn, l_message


class Parser:

    def __init__(self, urls, queries_path: str, query=None):
        self.urls = urls
        self.queries_path = queries_path
        self.query = query
        self.divs_requests: list = []  # создаем список c ответами
        self.HEADERS_MASTER = gs.HEADERS
        self.HEADERS_SLAVE = gs.HEADERS_TEST
        self.divs = None
        self.ques = None
        self.url = None
        self.request = None
        self.proxies = None

    def url_constructor(self):
        pass

    def write_to_excel(self):
        pass

    def divs_text_shelves(self):
        pass

    def get_it(self):
        """ функция посылает запрос и получает ответ. Если ответ есть - передаёт на обработку"""

        adapter_yd = HTTPAdapter(max_retries=3)  # максимальное количество повторов запроса в сессии
        session = requests.Session()  # устанавливаем сессию
        session.mount(str(self.url), adapter_yd)

        try:
            self.request: Response = session.get(self.url, headers=self.HEADERS_MASTER, stream=True, timeout=10.24)

            if self.check_request_status_code(self.request):
                l_message(gfn(), 'Успешный запрос!', color=Nm.bcolors.OKBLUE)
            else:
                self.request: Response = session.get(self.url, headers=self.HEADERS_SLAVE, stream=True,
                                                     timeout=10.24)  # запрос

        except Exception as err:
            l_message(gfn(), f"Exception: {repr(err)}", color=Nm.bcolors.FAIL)
            l_message(gfn(), f'Ошибка при установке соединения! проверьте подключение!', color=Nm.bcolors.FAIL)

    def check_request_status_code(self, request) -> bool:
        if request.status_code == 200:  # если запрос был выполнен успешно то
            l_message(gfn(), 'Успешный запрос!', color=Nm.bcolors.OKBLUE)
            return True

        elif request.status_code == 400:
            l_message(gfn(), f'BAD request {self.url} : {request.text}', color=Nm.bcolors.FAIL)

        elif request.status_code == 406:
            l_message(gfn(), f'Client Error {self.url} : {request.text}', color=Nm.bcolors.FAIL)

        elif 400 < request.status_code < 500:
            l_message(gfn(), f'Client Error {self.url} : {request.text}', color=Nm.bcolors.FAIL)

        elif 500 <= request.status_code < 600:
            l_message(gfn(), f'Server Error {self.url} : {request.text}', color=Nm.bcolors.FAIL)

        else:
            l_message(gfn(), f'Неудачный запрос! Ответ {request.status_code} : {str(request.text)}',
                      color=Nm.bcolors.FAIL)

    def get_it_with_proxi(self):
        """ функция посылает запрос и получает ответ. Если ответ есть - передаёт на обработку"""

        adapter_yd = HTTPAdapter(max_retries=3)  # максимальное количество повторов запроса в сессии
        session = requests.Session()  # устанавливаем сессию
        session.mount(str(self.url), adapter_yd)

        # proxies = []
        # for proxy in proxies:
        #     response = requests.get(proxies=proxy)
        #     if response.status_code == requests.codes['ok']:
        #         break
        #
        # response.text

        try:
            self.request: Response = session.get(self.url, headers=self.HEADERS_MASTER, stream=True, timeout=10.24,
                                                 proxies=self.proxies)  # запрос

            if self.request.status_code != 200:  # если запрос был выполнен успешно то
                l_message(gfn(), f'Неудачный запрос! Ответ {self.request.status_code} : {str(self.request.text)}',
                          color=Nm.bcolors.FAIL)

            l_message(gfn(), 'Успешный запрос!', color=Nm.bcolors.OKBLUE)

        except Exception as err:
            l_message(gfn(), f"Exception: {repr(err)}", color=Nm.bcolors.FAIL)
            l_message(gfn(), f'Ошибка при установке соединения! проверьте подключение!', color=Nm.bcolors.FAIL)

    def soup_request(self, ):
        """ обработка ответа с помощью BeautifulSoup. Если есть нужные данные - передаёт на поиск нужных данных в
            divs_text_shelves """

        if hasattr(self.request, 'text') and self.request.text != '':
            soup = BeautifulSoup(self.request.text, 'lxml')  # ответ
            self.divs = soup.find_all('li', class_='serp-item')  # данные ответа

        if self.divs is None:
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
