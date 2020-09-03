from requests.exceptions import ConnectionError
import general_setting as gs
from Parser import Parser
from Servises import Notify_by_Message as Nm
from Servises.Notify_by_Message import get_function_name, get_function_name as gfn
from Servises.Notify_by_Message import l_message
from Servises.timeit import timeit
from Writer_to_xlsx import Writer_to_xlsx

PASSED = False


class Parser_YD(Parser):

    def __init__(self, *, urls):
        super(Parser, self).__init__()
        self.HEADERS = gs.HEADERS
        self.urls = urls
        self.divs_requests: list = []
        self.ques = None
        self.url = None

    def start_work(self):
        """основная функция парсера"""

        for item_url in self.urls:
            try:
                self.url = item_url['url']
                self.ques = item_url['ques']

                self.result = self.get_it()
                self.divs_requests.extend(list(self.result))
                self._time_rand(2, 4)

            except ConnectionError as err:
                l_message(gfn(), f" ConnectionError: {repr(err)}", color=Nm.bcolors.FAIL)
                continue

        return self.divs_requests


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

        l_message(get_function_name(), mod_url, color=Nm.bcolors.OKBLUE)

        for i in range(max_pos):  # дополняем url и формируем для кажного запроса
            if i == 0:
                urls.append({'url': mod_url, 'ques': divs_ques})  # перывя ссылка с ключем

            else:
                url = str(mod_url + '&p=' + str(i))
                if url not in urls:
                    urls.append({'url': url, 'ques': divs_ques})  # остальные ссылки с ключом
                    l_message(get_function_name(), mod_url, color=Nm.bcolors.OKBLUE)
    return urls


@timeit
def main():
    """Основная функция с параметрами."""

    l_message(gfn(), '\n**** Start ****\n', color=Nm.bcolors.OKBLUE)

    urls = url_constructor(gs.queries_path, gs.base_url, gs.region, gs.within_time, gs.num_doc, gs.url_max_pos)

    parser = Parser_YD(urls=urls)
    divs_requests = parser.start_work()

    file_writer = Writer_to_xlsx(divs_requests, gs.full_path)
    file_writer.file_writer()

    # if gs.max_process == 1:
    #     divs_requests = Parser(urls)
    #     file_writer(divs_requests, gs.full_path)
    # else:
    #     divs_requests = Parser_parallel(urls, gs.max_process)  # паралельные запросы
    #     file_writer(divs_requests, gs.full_path)  # запись данных в файл

    l_message(gfn(), '\n**** Done ****\n', color=Nm.bcolors.OKBLUE)


if __name__ == '__main__':
    main()

# @timeit
# def Parser_parallel(urls, max_process: int) -> list:
#     """основная функция мульти парсера"""
#
#     pool_urls: list = []  # создаем список / очередь url
#     divs_requests_all: list = []  # создаем список  с ответами
#
#     for key_urls in urls:
#         pool_urls.append(key_urls['url'])  # создаем список / очередь url
#
#     with concurrent.futures.ProcessPoolExecutor(max_workers=max_process)as executor:  # создаем очередь процессов
#         results = [executor.submit(get_it, my_url) for my_url in pool_urls]  # каждый процесс берёт свой URL
#
#         for future in concurrent.futures.as_completed(results):  # Ответы
#             try:
#                 if not len(list(future.result())) == 0:  # если результат что то содержит то добавляем
#                     divs_requests_all.extend(list(future.result()))
#
#             except Exception as err:
#                 l_message(gfn(), f" Exception: {repr(err)}", color=Nm.bcolors.FAIL)
#         l_message(gfn(), str(divs_requests_all), color=Nm.bcolors.OKBLUE)
#
#     return divs_requests_all
#
#
# @timeit
# def file_writer(my_divs_requests, full_path_to_file: str = None):
#     """Записываем данные в файл Excel."""
#
#     doc_row: int = 1
#
#     create_headers_divs_requests(my_divs_requests)
#
#     if len(my_divs_requests) <= 2:
#         l_message(gfn(), f' \n Нет данных для записи в файл! \n ', color=Nm.bcolors.FAIL)
#         return
#
#     excel_app, wbook = create_workbook(full_path_to_file=full_path_to_file)
#
#     if __debug__ and not PASSED:
#         assert excel_app is not None, 'Не удалось подключится к Ecxel'
#         assert wbook is not None, 'Не удалось создать книгу'
#
#     try:
#         l_message(gfn(), 'Начало записи данных в файл', color=Nm.bcolors.OKBLUE)
#
#         for divs_iter in tqdm(my_divs_requests, ):  # записываем данные
#             if doc_row == 1:
#                 wbook.Worksheets('Лист1').Cells(doc_row, 1).Value = divs_iter['rowNom']
#             else:
#                 wbook.Worksheets('Лист1').Cells(doc_row, 1).Value = doc_row - 1
#
#             wbook.Worksheets('Лист1').Cells(doc_row, 2).Value = divs_iter['ques']
#             wbook.Worksheets('Лист1').Cells(doc_row, 3).Value = divs_iter['company_title']
#             wbook.Worksheets('Лист1').Cells(doc_row, 4).Value = divs_iter['company_cid']
#             wbook.Worksheets('Лист1').Cells(doc_row, 5).Value = divs_iter['company_link_1']
#             wbook.Worksheets('Лист1').Cells(doc_row, 6).Value = divs_iter['company_sitelinks']
#             wbook.Worksheets('Лист1').Cells(doc_row, 7).Value = divs_iter['company_text']
#             wbook.Worksheets('Лист1').Cells(doc_row, 8).Value = divs_iter['company_contact']
#             doc_row += 1
#
#         wbook.Close(True, full_path_to_file)  # сохраняем изменения и закрываем
#         excel_app_quit(excel_app)
#
#         l_message(gfn(), 'Данные записаны', color=Nm.bcolors.OKBLUE)
#
#     except Exception as err:
#         l_message(gfn(), f" Exception: {repr(err)}", color=Nm.bcolors.FAIL)
#         l_message(gfn(), 'Не удалось записать данные', color=Nm.bcolors.FAIL)
#         excel_app_quit(excel_app)
#         return
