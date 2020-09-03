import random
import time

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.models import Response
from tqdm import tqdm

import general_setting as gs
from Servises import Notify_by_Message as Nm
from Servises.Notify_by_Message import get_function_name as gfn, l_message


class Parser:

    def __init__(self, urls, queries_path: str, query=None):
        self.urls = urls
        self.queries_path = queries_path
        self.query = query
        self.divs_requests: list = []  # создаем список c ответами
        self.HEADERS = gs.HEADERS
        self.result = None
        self.divs = None
        self.ques = None
        self.url = None

    def start_parser(self) -> list:
        """основная функция парсера"""

        for item_url in self.urls:
            try:

                self.ques = item_url['ques']
                self.result = self.get_it()
                self.divs_requests.extend(list(self.result))
                self._time_rand(2, 4)

            except ConnectionError as err:
                l_message(gfn(), f" ConnectionError: {repr(err)}", color=Nm.bcolors.FAIL)
                continue

        return self.divs_requests

    def get_it(self):
        """ функция посылает запрос и получает ответ. Если ответ есть - передаёт на обработку"""

        adapter_yd = HTTPAdapter(max_retries=3)  # максимальное количество повторов запроса в сессии
        session = requests.Session()  # устанавливаем сессию
        session.mount(str(self.url), adapter_yd)

        try:
            request: Response = session.get(self.url, headers=self.HEADERS, stream=True, timeout=10.24)  # запрос
            if request.status_code == 200:  # если запрос был выполнен успешно то
                l_message(gfn(), 'Успешный запрос!', color=Nm.bcolors.OKBLUE)

                self.divs_requests = self.soup_request(request.text)  # обработка ответа сервера

            else:
                l_message(gfn(), f'Неудачный запрос! Ответ сервера {request.status_code} : {str(request.text)}',
                          color=Nm.bcolors.FAIL)

        except AttributeError as err:
            l_message(gfn(), f" AttributeError: {repr(err)}", color=Nm.bcolors.FAIL)
            l_message(gfn(), f'Ошибка при установке соединения! проверьте подключение!',
                      color=Nm.bcolors.FAIL)

        return self.divs_requests

    def soup_request(self, request_text):
        """ обработка ответа с помощью BeautifulSoup. Если есть нужные данные - передаёт на поиск нужных данных в
            divs_text_shelves """

        soup = BeautifulSoup(request_text, 'lxml')  # ответ
        self.divs = soup.find_all('li', class_='serp-item')  # данные ответа

        if len(self.divs) == 0:
            l_message(gfn(), 'Ответ не содержит нужных данных :(', color=Nm.bcolors.FAIL)
            return

        l_message(gfn(), f'Всего найдено блоков ' + str(len(self.divs)), color=Nm.bcolors.OKBLUE)
        self.divs_text_shelves()

        return self.divs_requests

    def divs_text_shelves(self):
        """ищем нужные данные ответа"""

        i_row: int = 1

        for DIV in tqdm(self.divs):
            my_company_title = self.get_my_company_title(DIV)
            my_company_cid = self.get_my_company_cid(DIV)
            my_company_link_1 = self.get_my_company_link_1(DIV)
            my_company_sitelinks = self.get_my_company_sitelinks(DIV)
            my_company_text = self.get_my_company_text(DIV)
            my_company_contact = self.get_my_company_contact(DIV)

            self.divs_requests.append({'rowNom': i_row,
                                       'ques': self.ques,
                                       'company_title': my_company_title,
                                       'company_cid': my_company_cid,
                                       'company_link_1': my_company_link_1,
                                       'company_sitelinks': my_company_sitelinks,
                                       'company_text': my_company_text,
                                       'company_contact': my_company_contact})
            i_row = i_row + 1

        return self.divs_requests

    @staticmethod
    def get_my_company_title(DIV):
        """Найти и вернуть название компании"""

        try:
            my_company_title: str = DIV.find('h2', attrs={
                'class': "organic__title-wrapper typo typo_text_l typo_line_m"}).text.strip()
            l_message(gfn(), f'company_title {my_company_title}', color=Nm.bcolors.OKBLUE)

        except AttributeError as err:
            l_message(gfn(), f" AttributeError: {repr(err)}", color=Nm.bcolors.FAIL)
            my_company_title: str = 'N\A'

        return my_company_title

    @staticmethod
    def get_my_company_cid(DIV):
        """Найти и вернуть порядковый номер компании на странице."""

        try:
            my_company_cid: str = str(DIV.get('data-cid'))
            l_message(gfn(), f'company_cid {my_company_cid}', color=Nm.bcolors.OKBLUE)

        except AttributeError as err:
            l_message(gfn(), f" AttributeError: {repr(err)}", color=Nm.bcolors.FAIL)
            my_company_cid: str = ''

        return my_company_cid

    @staticmethod
    def get_my_company_contact(DIV):
        """Найти и вернуть контакты компании."""

        try:
            my_company_contact: str = DIV.find('div', attrs={
                'class': 'serp-meta__item'}).text.strip()
            l_message(gfn(), f'company_contact {my_company_contact}', color=Nm.bcolors.OKBLUE)

        except AttributeError as err:
            l_message(gfn(), f" AttributeError: {repr(err)}", color=Nm.bcolors.FAIL)
            my_company_contact: str = 'N\A'

        return my_company_contact

    @staticmethod
    def get_my_company_text(DIV):
        """Найти и вернуть описание компании."""

        try:
            my_company_text: str = DIV.find('div', attrs={
                'class': 'text-container typo typo_text_m typo_line_m organic__text'}).text.strip()
            l_message(gfn(), f'company_text  {my_company_text}', color=Nm.bcolors.OKBLUE)

        except AttributeError as err:
            l_message(gfn(), f" AttributeError: {repr(err)}", color=Nm.bcolors.FAIL)
            my_company_text: str = ''

        return my_company_text

    @staticmethod
    def get_my_company_sitelinks(DIV):
        """Найти и вернуть ссылку на сайт компании."""

        try:
            my_company_sitelinks: str = DIV.find('div', attrs={
                'class': 'sitelinks sitelinks_size_m organic__sitelinks'}).text.strip()
            l_message(gfn(), f'company_site_links  {my_company_sitelinks}', color=Nm.bcolors.OKBLUE)

        except AttributeError as err:
            l_message(gfn(), f" AttributeError: {repr(err)}", color=Nm.bcolors.FAIL)
            my_company_sitelinks: str = 'N\A'

        return my_company_sitelinks

    @staticmethod
    def get_my_company_link_1(DIV):
        """Найти и вернуть быструю ссылку на сайт компании."""

        try:
            my_company_link_1: str = DIV.find('a', attrs={
                'class': 'link link_theme_outer path__item i-bem'}).text.strip()
            text: int = my_company_link_1.rfind('>')
            if text > 0:
                my_company_link_1 = my_company_link_1[0:text - 1]
            l_message(gfn(), f'company_link_1 {my_company_link_1}', color=Nm.bcolors.OKBLUE)

        except AttributeError as err:
            l_message(gfn(), f" AttributeError: {repr(err)}", color=Nm.bcolors.FAIL)
            my_company_link_1: str = ''

        return my_company_link_1

    @staticmethod
    def _time_rand(t_start: int = 1, t_stop: int = 30):
        """функция задержки выполнения кода на рандомный промежуток """

        time_random = random.randint(t_start, t_stop)
        l_message(gfn(), f'Время ожидания нового запроса time_rand  {str(time_random)} sec', color=Nm.bcolors.OKBLUE)

        for _ in range(time_random):
            time.sleep(random.uniform(0.8, 1.2))
