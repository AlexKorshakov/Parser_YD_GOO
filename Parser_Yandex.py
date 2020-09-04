from requests.exceptions import ConnectionError
from tqdm import tqdm

import general_setting as gs
from Parser import Parser
from Servises import Notify_by_Message as Nm
from Servises.Notify_by_Message import get_function_name as gfn
from Servises.Notify_by_Message import l_message
from Servises.Writer_xlsx import Writer_to_xlsx
from Servises.timeit import timeit

PASSED = False


class Parser_YD(Parser):

    def __init__(self, *, urls):
        super(Parser, self).__init__()
        self.HEADERS_MASTER = gs.HEADERS
        self.HEADERS_SLAVE = gs.HEADERS_TEST
        self.urls = urls
        self.divs_requests: list = []
        self.result: list = []
        self.ques = None
        self.url = None
        self.request = None
        self.divs = None

    def start_work(self):
        """основная функция парсера"""

        for number, item_url in enumerate(self.urls):
            l_message(gfn(), f"\nЗапрос номер: {number + 1} \n", color=Nm.bcolors.OKBLUE)
            try:
                self.url = item_url['url']
                self.ques = item_url['ques']
                self.get_it()
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

            text: int = my_company_contact.rfind('+')
            if text > 0:
                my_company_contact = my_company_contact[text:]

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
            text: int = my_company_link_1.rfind('›')
            if text > 0:
                my_company_link_1 = my_company_link_1[0:text]
            l_message(gfn(), f'company_link_1 {my_company_link_1}', color=Nm.bcolors.OKBLUE)

        except AttributeError as err:
            l_message(gfn(), f" AttributeError: {repr(err)}", color=Nm.bcolors.FAIL)
            my_company_link_1: str = ''

        return my_company_link_1


@timeit
def url_constructor(queries_path, selected_base_url, selected_region, within_time, numdoc=10, max_pos=3):
    """формируем запрос из запчастей"""

    urls = []
    # открываем файл с ключами по пути queries_path и считываем ключи
    with open(queries_path, 'r', encoding='utf-8') as file:
        query = [x.strip() for x in file]

    for ques in query:  # перебираем ключи и формируем url на их основе
        divs_ques: str = ques
        if numdoc == 10:
            mod_url = selected_base_url + ques.replace(' ', '%20') + '&lr=' + str(selected_region) + '&within=' + str(
                within_time) + '&lang=ru'
        else:
            mod_url = selected_base_url + ques.replace(' ', '%20') + '&lr=' + str(selected_region) + '&within=' + str(
                within_time) + '&lang=ru' + '&numdoc=' + str(numdoc)

        l_message(gfn(), mod_url, color=Nm.bcolors.OKBLUE)

        for i in range(max_pos):  # дополняем url и формируем для кажного запроса
            if i == 0:
                urls.append({'url': mod_url, 'ques': divs_ques})  # перывя ссылка с ключем

            else:
                url = str(mod_url + '&p=' + str(i))
                if url not in urls:
                    urls.append({'url': url, 'ques': divs_ques})  # остальные ссылки с ключом
                    l_message(gfn(), mod_url, color=Nm.bcolors.OKBLUE)
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
