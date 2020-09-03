import os

import win32com.client
from requests.exceptions import ConnectionError
from win32com.universal import com_error

import general_setting as gs
from Parser import Parser
from Servises import Notify_by_Message as Nm
from Servises.Notify_by_Message import get_function_name as gfn
from Servises.Notify_by_Message import l_message
from Servises.timeit import timeit

PASSED = False


class Writer_to_xlsx:
    def __init__(self, divs_requests, full_path_to_file):
        self.divs_requests = divs_requests
        self.excel_app = None
        self.wbook = None
        self.full_path_to_file = full_path_to_file

    def file_writer(self):
        """Записываем данные в файл Excel."""

        if len(self.divs_requests) == 0:
            l_message(gfn(), f' \n Нет данных для записи в файл! \n ', color=Nm.bcolors.FAIL)
            return

        self.insert_headers_divs_requests()
        excel_app, wbook = self.create_workbook()

        if __debug__ and not PASSED:
            assert excel_app is not None, 'Не удалось подключится к Ecxel'
            assert wbook is not None, 'Не удалось создать книгу'

        try:
            self._write_to_sheet()
            wbook.Close(True, self.full_path_to_file)  # сохраняем изменения и закрываем
            self.excel_app_quit()

        except Exception as err:
            l_message(gfn(), f" Exception: {repr(err)}", color=Nm.bcolors.FAIL)
            l_message(gfn(), 'Не удалось записать данные', color=Nm.bcolors.FAIL)
            self.excel_app_quit()
            return

    def _write_to_sheet(self):
        """Запись данных на лист."""

        l_message(gfn(), 'Начало записи данных в файл', color=Nm.bcolors.OKBLUE)
        doc_row: int = 1
        for divs_iter in self.divs_requests:  # записываем данные

            if doc_row == 1:
                self.wbook.Worksheets.Item(1).Cells(doc_row, 1).Value = divs_iter['rowNom']
            else:
                self.wbook.Worksheets.Item(1).Cells(doc_row, 1).Value = doc_row - 1
            self.wbook.Worksheets.Item(1).Cells(doc_row, 2).Value = divs_iter['ques']
            self.wbook.Worksheets.Item(1).Cells(doc_row, 3).Value = divs_iter['company_title']
            self.wbook.Worksheets.Item(1).Cells(doc_row, 4).Value = divs_iter['company_cid']
            self.wbook.Worksheets.Item(1).Cells(doc_row, 5).Value = divs_iter['company_link_1']
            self.wbook.Worksheets.Item(1).Cells(doc_row, 6).Value = divs_iter['company_sitelinks']
            self.wbook.Worksheets.Item(1).Cells(doc_row, 7).Value = divs_iter['company_text']
            self.wbook.Worksheets.Item(1).Cells(doc_row, 8).Value = divs_iter['company_contact']
            doc_row += 1
        l_message(gfn(), 'Данные записаны', color=Nm.bcolors.OKBLUE)

    def insert_headers_divs_requests(self):
        """Создание заголовков в list с распарсенными данными."""

        return self.divs_requests.insert(0, gs.headers_tab)

    def create_workbook(self):
        """ Создание обектов приложения Excel и обьекта страницы."""

        try:
            self.excel_app = win32com.client.gencache.EnsureDispatch('Excel.Application')
            self.excel_app_start()

            if os.path.exists(self.full_path_to_file):  # файл excel существует то удаляем
                os.remove(self.full_path_to_file)

            self.wbook = self.excel_app.Workbooks.Add()
            self.wbook.SaveAs(self.full_path_to_file)
            l_message(gfn(), f'Книга создана в {self.full_path_to_file}', color=Nm.bcolors.OKBLUE)

            self.wbook = self.excel_app.Workbooks.Open(self.full_path_to_file)

        except com_error as err:
            l_message(gfn(), f" pywintypes.com_error: {repr(err)}", color=Nm.bcolors.FAIL)

        except TypeError as err:
            l_message(gfn(), f"  TypeError: {repr(err)}", color=Nm.bcolors.FAIL)
            try:
                self.wbook.Close(False)  # save the workbook
                self.excel_app_quit()
                l_message(gfn(), "**** Аварийное завершение программы ****", color=Nm.bcolors.FAIL)

            except AttributeError as err:
                l_message(gfn(), f" AttributeError: {repr(err)}", color=Nm.bcolors.FAIL)
                quit()

        return self.excel_app, self.wbook

    def excel_app_start(self):
        """ Старт приложения Excel"""

        self.excel_app.DisplayAlerts = False  # отключаем обновление экрана
        self.excel_app.Visible = False
        self.excel_app.ScreenUpdating = False

    def excel_app_quit(self):
        """Выход из приложения Excel"""

        self.excel_app.DisplayAlerts = True  # отключаем обновление экрана
        self.excel_app.Visible = True
        self.excel_app.ScreenUpdating = True
        self.excel_app.Quit()


class Parser_YD(Parser):

    def __init__(self, *, urls):
        super(Parser, self).__init__()
        self.HEADERS = gs.HEADERS
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
