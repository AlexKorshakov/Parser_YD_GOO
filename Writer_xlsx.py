


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

# def time_rand(t_start: int = 1, t_stop: int = 10, pb_visio=True):
#     """Функция задержки выполнения кода на рандомный промежуток
#     с обёрткой tqdm для отображение выполнеия
#
#     :param t_start: начало диапазона: int
#     :param t_stop: конец диапазона: int
#     :param pb_visio: отображение прогрессбара: boolean
#     """
#     time_random = random.randint(t_start, t_stop)  # задаём рандомный промежуток задержки (от 1 до 10 сек)
#     l_message(gfn(), f'Время ожидания нового запроса time_rand ' + str(time_random) + ' sec', color=Nm.bcolors.FAIL)
#     if pb_visio:
#         for _ in tqdm(range(time_random)):
#             time.sleep(random.uniform(0.9, 1.1))
#     else:
#         for _ in range(time_random):
#             time.sleep(random.uniform(0.9, 1.1))
