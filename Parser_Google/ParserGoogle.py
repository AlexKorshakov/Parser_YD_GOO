from requests.exceptions import ConnectionError
from tqdm import tqdm

from Parser_Google import general_setting_google_parser as gs, text_shelves_google as ts
from Parser_ABC.Parser import Parser
from Servises import Notify_by_Message as Nm
from Servises.Notify_by_Message import get_function_name as gfn
from Servises.Notify_by_Message import l_message
from Servises.Writer_xlsx import WriterToXLSX
from Servises.timeit import timeit

PASSED = False

__date__ = '19.09.2020'
_name_ = 'Parser_Google'
print(f'Invoking __init__.py for {__name__}')


class ParserGoogle(Parser):

    def __init__(self, *, urls):
        super(ParserGoogle, self).__init__(self, urls)
        self.urls = urls

        self.divs_requests: list = []
        self.result: list = []
        self.proxyes: list = []  # создаем список c прокси

        self.ques = None
        self.url = None
        self.request = None
        self.divs = None

        self.HEADERS = [gs.HEADERS_TEST, gs.kad_head]
        self.full_path_to_file = gs.full_path
        self.proxy_path = gs.proxy_path
        self.request_timeout = gs.request_timeout

        self.full_path = gs.full_path + _name_ + ' ' + gs.date_today + gs.extension

        self.soup_name = gs.soup_name
        self.soup_class = gs.soup_class
        self.soup_attribute = gs.soup_attribute

    def start_work(self):
        """ функция парсера.
        """

        assert self.urls is not None, f"{gfn()} urls not passed"

        for number, item_url in enumerate(self.urls):
            l_message(gfn(), f"\nЗапрос номер: {number + 1} \n", color=Nm.BColors.OKBLUE)

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
                l_message(gfn(), f" ConnectionError: {repr(err)}", color=Nm.BColors.FAIL)
                continue

        self.write_data_to_file()

    def divs_text_shelves(self):
        """ищем нужные данные ответа"""

        i_row: int = 1
        for div in tqdm(self.divs):
            my_company_title: str = ts.get_my_company_title(div)
            my_company_cid: str = ts.get_my_company_cid(i_row)
            my_company_link_1: str = ts.get_my_company_link_1(div)
            my_company_site_links: str = ts.get_my_company_site_links(div)
            my_company_text: str = ts.get_my_company_text(div)
            my_company_contact: str = ts.get_my_company_contact(div)

            self.divs_requests.append({'rowNom': i_row,
                                       'ques': self.ques,
                                       'company_title': my_company_title,
                                       'company_cid': my_company_cid,
                                       'company_link_1': my_company_link_1,
                                       'company_sitelinks': my_company_site_links,
                                       'company_text': my_company_text,
                                       'company_contact': my_company_contact})
            i_row = i_row + 1

    def write_data_to_file(self):
        """ Запись данных в файл.
        """
        file_writer = WriterToXLSX(self.divs_requests, self.full_path)
        file_writer.file_writer()


@timeit
def url_constructor_google(queries_path: str, selected_base_url: str, selected_region: str, max_pos: int = 3):
    """ Формирование запросов из запчастей.
    """

    urls = []
    # открываем файл с ключами по пути queries_path и считываем ключи
    with open(queries_path, 'r', encoding='utf-8') as file:
        query: list = [x.strip() for x in file]

    for ques in query:  # перебираем ключи и формируем url на их основе
        divs_ques: str = ques
        mod_url = selected_base_url + '?q=' + ques.replace(' ', '+') + selected_region

        l_message(gfn(), mod_url, color=Nm.BColors.OKBLUE)

        for i in range(max_pos):  # дополняем url и формируем для кажного запроса
            if i == 0:
                urls.append({'url': mod_url, 'ques': divs_ques})  # перывя ссылка с ключем
            else:
                url = str(mod_url + '&start=' + str(i) + '0')
                if url not in urls:
                    urls.append({'url': url, 'ques': divs_ques})  # остальные ссылки с ключом
                    l_message(gfn(), url, color=Nm.BColors.OKBLUE)
    return urls


@timeit
def main():
    """Основная функция с параметрами.
    """

    l_message(gfn(), '\n**** Start ****\n', color=Nm.BColors.OKBLUE)

    urls = url_constructor_google(gs.queries_path, gs.base_url_google, gs.region_google, gs.url_max_pos_google)

    parser = ParserGoogle(urls=urls)
    parser.start_work()

    l_message(gfn(), '\n**** Done ****\n', color=Nm.BColors.OKBLUE)


if __name__ == '__main__':
    main()
