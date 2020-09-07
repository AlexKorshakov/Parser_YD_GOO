from requests.exceptions import ConnectionError
from tqdm import tqdm

import general_setting as gs
import text_shelves_google as ts
from Parser import Parser
from Servises import Notify_by_Message as Nm
from Servises.Notify_by_Message import get_function_name as gfn
from Servises.Notify_by_Message import l_message
from Servises.Writer_xlsx import Writer_to_xlsx
from Servises.timeit import timeit

PASSED = False

__date__ = '07.09.2020'
_name_ = 'Parser_Google'


class Parser_Google(Parser):

    def __init__(self, *, urls):
        super(Parser, self).__init__()
        self.urls = urls
        self.divs_requests: list = []
        self.result: list = []
        self.ques = None
        self.url = None
        self.request = None
        self.divs = None
        self.HEADERS = [gs.HEADERS_TEST, gs.kad_head]
        self.full_path_to_file = gs.full_path
        self.proxy_path = gs.proxy_path
        self.request_timeout = gs.request_timeout
        self.proxyes: list = []  # создаем список c прокси
        self.full_path = gs.full_path + _name_ + ' ' + gs.date_today + gs.extention

    def start_work(self):
        """основная функция парсера"""

        assert self.urls is not None, gfn() + "urls not passed"

        for number, item_url in enumerate(self.urls):
            l_message(gfn(), f"\nЗапрос номер: {number + 1} \n", color=Nm.bcolors.OKBLUE)

            if number <= 10:
                try:
                    self.url = item_url['url']
                    self.ques = item_url['ques']

                    assert self.url is not None, gfn() + "url not passed from self.urls" + "iteration: " + str(number)
                    assert self.ques is not None, gfn() + "ques not passed from self.urls" + "iteration: " + str(number)

                    self.get_response()
                    self.soup_request_google()  # обработка ответа сервера

                    if self.divs is not None:
                        self.divs_text_shelves()
                        self.result.extend(list(self.divs_requests))
                    self._time_rand(2, 4)

                except ConnectionError as err:
                    l_message(gfn(), f" ConnectionError: {repr(err)}", color=Nm.bcolors.FAIL)
                    continue

            else:
                try:
                    self.proxyes = self.generate_proxi_pool()
                    self.get_response_with_proxy()

                    self.soup_request_google()  # обработка ответа сервера

                    if self.divs is not None:
                        self.divs_text_shelves()
                        self.result.extend(list(self.divs_requests))
                    self._time_rand(2, 4)
                except ConnectionError as err:
                    l_message(gfn(), f" ConnectionError: {repr(err)}", color=Nm.bcolors.FAIL)
                    continue

        self.write_to_excel()

    def write_to_excel(self):
        file_writer = Writer_to_xlsx(self.divs_requests, self.full_path)
        file_writer.file_writer()

    def divs_text_shelves(self):
        """ищем нужные данные ответа"""

        i_row: int = 1
        for DIV in tqdm(self.divs):
            my_company_title: str = ts.get_my_company_title(DIV)
            my_company_cid: str = ts.get_my_company_cid(i_row)
            my_company_link_1: str = ts.get_my_company_link_1(DIV)
            my_company_site_links: str = ts.get_my_company_site_links(DIV)
            my_company_text: str = ts.get_my_company_text(DIV)
            my_company_contact: str = ts.get_my_company_contact(DIV)

            self.divs_requests.append({'rowNom': i_row,
                                       'ques': self.ques,
                                       'company_title': my_company_title,
                                       'company_cid': my_company_cid,
                                       'company_link_1': my_company_link_1,
                                       'company_sitelinks': my_company_site_links,
                                       'company_text': my_company_text,
                                       'company_contact': my_company_contact})
            i_row = i_row + 1


@timeit
def main():
    """Основная функция с параметрами."""

    l_message(gfn(), '\n**** Start ****\n', color=Nm.bcolors.OKBLUE)

    urls = url_constructor_for_google(gs.queries_path, gs.base_url_google, gs.region_google, gs.url_max_pos_google)

    parser = Parser_Google(urls=urls)
    parser.start_work()

    l_message(gfn(), '\n**** Done ****\n', color=Nm.bcolors.OKBLUE)


@timeit
def url_constructor_for_google(queries_path, selected_base_url, selected_region, max_pos=3):
    """Формируем запрос из запчастей"""

    urls = []
    # открываем файл с ключами по пути queries_path и считываем ключи
    queries = open(queries_path, 'r', encoding='utf-8')
    query: list = [x.strip() for x in queries]
    queries.close()

    for ques in query:  # перебираем ключи и формируем url на их основе
        divs_ques: str = ques
        mod_url = selected_base_url + '?q=' + ques.replace(' ', '+') + selected_region

        l_message(gfn(), mod_url, color=Nm.bcolors.OKBLUE)

        for i in range(max_pos):  # дополняем url и формируем для кажного запроса
            if i == 0:
                urls.append({'url': mod_url, 'ques': divs_ques})  # перывя ссылка с ключем
            else:
                url = str(mod_url + '&start=' + str(i) + '0')
                if url not in urls:
                    urls.append({'url': url, 'ques': divs_ques})  # остальные ссылки с ключом
                    l_message(gfn(), url, color=Nm.bcolors.OKBLUE)
    return urls


if __name__ == '__main__':
    main()
