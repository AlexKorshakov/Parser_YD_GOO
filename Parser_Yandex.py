from requests.exceptions import ConnectionError
from tqdm import tqdm

import general_setting as gs
import text_shelves as ts
from Parser import Parser
from Servises import Notify_by_Message as Nm
from Servises.Notify_by_Message import get_function_name as gfn
from Servises.Notify_by_Message import l_message
from Servises.Writer_xlsx import Writer_to_xlsx
from Servises.timeit import timeit

PASSED = False

__date__ = '07.09.2020'


class Parser_YD(Parser):

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

    def start_work(self):
        """основная функция парсера"""

        assert self.urls is not None, gfn() + "urls not passed"

        for number, item_url in enumerate(self.urls):
            l_message(gfn(), f"\nЗапрос номер: {number + 1} \n", color=Nm.bcolors.OKBLUE)

            if number <= 0:
                try:
                    self.url = item_url['url']
                    self.ques = item_url['ques']

                    assert self.url is not None, gfn() + "url not passed from self.urls" + "iteration: " + str(number)
                    assert self.ques is not None, gfn() + "ques not passed from self.urls" + "iteration: " + str(number)

                    self.get_response()
                    self.soup_request()  # обработка ответа сервера

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

                    self.soup_request()  # обработка ответа сервера

                    if self.divs is not None:
                        self.divs_text_shelves()
                        self.result.extend(list(self.divs_requests))
                    self._time_rand(2, 4)
                except ConnectionError as err:
                    l_message(gfn(), f" ConnectionError: {repr(err)}", color=Nm.bcolors.FAIL)
                    continue

        self.write_to_excel()

    def write_to_excel(self):
        file_writer = Writer_to_xlsx(self.divs_requests, gs.full_path)
        file_writer.file_writer()

    def divs_text_shelves(self):
        """ищем нужные данные ответа"""

        i_row: int = 1
        for DIV in tqdm(self.divs):
            my_company_title: str = ts.get_my_company_title(DIV)
            my_company_cid: str = ts.get_my_company_cid(DIV)
            my_company_link_1: str = ts.get_my_company_link_1(DIV)
            my_company_site_links: str = ts.get_my_company_sitelinks(DIV)
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
def url_constructor(queries_path, selected_base_url, selected_region, within_time, num_doc=10, max_pos=3):
    """формируем запрос из запчастей"""

    urls = []
    # открываем файл с ключами по пути queries_path и считываем ключи
    with open(queries_path, 'r', encoding='utf-8') as file:
        query = [x.strip() for x in file]

    for ques in query:  # перебираем ключи и формируем url на их основе
        divs_ques: str = ques
        if num_doc == 10:
            mod_url = selected_base_url + ques.replace(' ', '%20') + '&lr=' + str(selected_region) + '&within=' + str(
                within_time) + '&lang=ru'
        else:
            mod_url = selected_base_url + ques.replace(' ', '%20') + '&lr=' + str(selected_region) + '&within=' + str(
                within_time) + '&lang=ru' + '&num_doc=' + str(num_doc)

        for i in range(max_pos):  # дополняем url и формируем для кажного запроса
            if i == 0:
                l_message(gfn(), mod_url, color=Nm.bcolors.OKBLUE)
                urls.append({'url': mod_url, 'ques': divs_ques})  # перывя ссылка с ключем

            else:
                url = str(mod_url + '&p=' + str(i))

                if url not in urls:
                    l_message(gfn(), url, color=Nm.bcolors.OKBLUE)
                    urls.append({'url': url, 'ques': divs_ques})  # остальные ссылки с ключом

    return urls


@timeit
def main():
    """Основная функция с параметрами."""

    l_message(gfn(), '\n**** Start ****\n', color=Nm.bcolors.OKBLUE)

    urls = url_constructor(gs.queries_path, gs.base_url, gs.region, gs.within_time, gs.num_doc, gs.url_max_pos)

    parser = Parser_YD(urls=urls)
    parser.start_work()

    l_message(gfn(), '\n**** Done ****\n', color=Nm.bcolors.OKBLUE)


if __name__ == '__main__':
    main()

    # divs_requests = parser.start_work()
    # file_writer = Writer_to_xlsx(divs_requests, gs.full_path)
    # file_writer.file_writer()

    # if gs.max_process == 1:
    #     divs_requests = Parser(urls)
    #     file_writer(divs_requests, gs.full_path)
    # else:
    #     divs_requests = Parser_parallel(urls, gs.max_process)  # паралельные запросы
    #     file_writer(divs_requests, gs.full_path)  # запись данных в файл
