import os
import random
import re
import time
import requests
from win32com.client import Dispatch
import win32com.client as com_client
from bs4 import BeautifulSoup
from requests import Response
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError
from tqdm import tqdm
from functools import wraps
from multiprocessing import Pool, freeze_support

VIS_LOG = False  # Отображение хода процесса в консоли
PRINT_LOG = True  # Запись лога в файл

agents = ['Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko)',
          'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko)',
          'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)',
          'Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)',
          'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0']

HEADERS = {'Accept': '*/*',
           'Connection': 'keep-alive',
           'Upgrade-Insecure-Requests': '1',
           'Cache-Control': 'max-age=0',
           'User-Agent': random.choice(agents)}


def timeit(method):
    """Деоратор отображения работы функции"""

    @wraps(method)
    def timed(*args, **kw):
        ts = time.monotonic()
        result = method(*args, **kw)
        ms = (time.monotonic() - ts) * 1000
        sec: float = round(ms / 1000, 2)

        print_args = False
        print_kwgs = True

        if print_args:
            all_args = ', '.join(tuple(f'{a!r}' for a in args))
            print('Время выполнения функции ' + f'{method.__name__}({all_args}): {ms:2.2f} ms или ' + str(sec) + 'сек.')
        elif print_kwgs:
            all_args = ', '.join(tuple(f'{k}={v!r}' for k, v in kw.items()))
            print('Время выполнения функции ' + f'{method.__name__}({all_args}): {ms:2.2f} ms или ' + str(sec) + 'сек.')
        elif print_args and print_kwgs:
            all_args = ', '.join(tuple(f'{a!r}' for a in args) + tuple(f'{k}={v!r}' for k, v in kw.items()))
            print('Время выполнения функции ' + f'{method.__name__}({all_args}): {ms:2.2f} ms или ' + str(sec) + 'сек.')
        else:
            print('Время выполнения функции ' + f'{method.__name__}: {ms:2.2f} ms или ' + str(sec) + 'сек.')
        return result

    return timed


class ExcelApp(object):

    @classmethod
    def app_open(cls):
        # открываем Excel в скрытом режиме, отключаем обновление экрана и сообщения системы
        excel = Dispatch("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        excel.ScreenUpdating = False
        return log_visrec('ExcelApp', 'Успешно запустили Excel')

    @classmethod
    def file_create(cls, full_path):
        excel = Dispatch("Excel.Application")
        wbook = excel.Workbooks.Add()
        # wbook.Worksheets.Add()
        wbook.SaveAs(full_path)
        return log_visrec('ExcelApp', 'Книга создана в my_full_path')

    @classmethod
    def app_close(cls):
        global excel
        try:
            # включаем обновление экрана и сообщения системы
            excel = Dispatch("Excel.Application")
            excel.Visible = True
            excel.DisplayAlerts = True
            excel.ScreenUpdating = True
        finally:
            excel.Quit()  # выходим из Excel
            return log_visrec('ExcelApp', 'Excel закрыт')


def log_visrec(param_name: str = None, param_value=None, r_log: bool = VIS_LOG, r_print: bool = PRINT_LOG):
    """Функция логирования и отображения в терминале"""

    try:
        if r_log:
            if len(param_value) < 200:
                print(f'Параметр {param_name} Значение: {param_value}')
            else:
                print(f'Параметр {param_name} Значение: {param_value[:200] + "..."}')
    except:
        print('log_visrec: Ошибка вывода в консоль')
    try:
        if r_print:
            file = open('Log.txt', 'a', encoding='utf-8')
            text = f'Параметр {param_name}. Значение : {param_value}'
            file.write(text + '\n')
            file.close()
    except:
        print('log_visrec: Ошибка записи в файл')


def time_rand(t_start: int = 1, t_stop: int = 30):
    """функция задержки выполнения кода на рандомный промежуток """
    time_random = random.randint(t_start, t_stop)  # задаём рандомеый промежуток задержки (от 1 до 30 сек)
    log_visrec('Время ожидания нового запроса time_rand ' + str(time_random) + ' sec')
    for _ in tqdm(range(time_random)):
        time.sleep(1)


@timeit
def url_constructor(queries_path, selected_base_url, selected_region, max_pos=3):
    """формируем запрос из запчастей"""
    urls = []
    # открываем файл с ключами по пути queries_path и считываем ключи
    queries = open(queries_path, 'r', encoding='utf-8')
    query: list = [x.strip() for x in queries]
    queries.close()

    for ques in query:  # перебираем ключи и формируем url на их основе
        divs_ques: str = ques
        # breakpoint()
        mod_url = selected_base_url + '?q=' + ques.replace(' ', '+') + selected_region + '&oq=' + ques.replace(
            ' ', '+') + selected_region + "&lr=lang_ru"
        log_visrec('url', mod_url)

        for i in range(max_pos):  # дополняем url и формируем для кажного запроса
            if i == 0:
                urls.append({'url': mod_url, 'ques': divs_ques})  # перывя ссылка с ключем
            else:
                url = str(mod_url + '&start=' + str(i))
                if url not in urls:
                    urls.append({'url': url, 'ques': divs_ques})  # остальные ссылки с ключом
                    log_visrec('url', url)
    return urls


@timeit
def Parser_YD_GOO(urls, divs_requests):
    """основная функция парсера"""
    # создаём сессию (session), отправляем запрос (request), получаем ответ (request.text), варим суп (soup)
    url_counter: int = 1

    adapter_yd = HTTPAdapter(max_retries=3)  # транспортный адаптер — максимальное количество повторов запроса
    session = requests.Session()  # устанавливаем сессию

    for it_url in urls:
        if url_counter != 1:  # Для всех ссылок КРОМЕ ПЕРВОЙ задаём рандомный промежуток задежки.
            time_rand(2, 10)

        session.mount(it_url['url'], adapter_yd)
        # proxy?
        try:
            request: Response = session.get(it_url['url'], headers=HEADERS, stream=True, timeout=5.24)  # запрос
            url_counter += 1
            if request.status_code == 200:  # если запрос был выполнен успешно то
                log_visrec('Parser_YD_GOO', 'Успешный запрос!')
                # обработка ответа сервера
                divs_requests = soup_request(request.text, url_counter, it_url['ques'], divs_requests)
            else:
                log_visrec('Parser_YD_GOO', 'Неудачный запрос! Ответ сервера{0}'.format(str(request.status_code)), True)
        except ConnectionError as ce:
            log_visrec('Parser_YD_GOO', f'Ошибка при установке соединения! проверьте подключение!', True)
            log_visrec('Parser_YD_GOO', str(ce.args), True)
            continue

    return divs_requests


@timeit
def Parser_YD_GOO_parallel(urls, divs_requests, options=None, callback=None):
    """основная функция мульти парсера"""

    pool_urls: list = []  # создаем список url
    for key_urls in urls:
        pool_urls.append(key_urls['url'])
    log_visrec('check_headers_parallel_pool_urls', str(pool_urls))

    # if not options:
    # options= options.result()

    if Pool:
        results = []
        freeze_support()
        pool = Pool(processes=4)
        for url in pool_urls:
            result = pool.apply_async(get_it, args=(url, divs_requests,), callback=callback)
            time.sleep(0.5)
            results.append(result)
            log_visrec('check_headers_parallel', str(results))

        pool.close()
        pool.join()
    else:
        raise Exception('no parallelism supported')

    log_visrec('Parser_YD_GOO_parallel_divs_requests', divs_requests)
    return divs_requests


@timeit
def get_it(url, divs_requests, ques=None):
    """ функция посылает запрос и получает ответ"""
    adapter_yd = HTTPAdapter(max_retries=3)  # транспортный адаптер — максимальное количество повторов запроса
    session = requests.Session()  # устанавливаем сессию
    session.mount(str(url), adapter_yd)

    try:
        request: Response = session.get(url, headers=HEADERS, stream=True, timeout=10.24)  # запрос
        if request.status_code == 200:  # если запрос был выполнен успешно то
            log_visrec('get_it', 'Успешный запрос!')
            divs_requests = soup_request(request.text, 1, ques, divs_requests)  # обработка ответа сервера

    except Exception as ce:
        log_visrec('get_it', f'Ошибка при установке соединения! проверьте подключение!', True)
        log_visrec('get_it', str(ce.args), True)

    log_visrec('get_it_divs_requests', divs_requests)
    return divs_requests


@timeit
def soup_request(r_text, url_counter, it_url_soup, divs_requests):
    """ обработка ответа с помощью BeautifulSoup """
    soup = BeautifulSoup(r_text, 'lxml')  # ответ
    divs = soup.find_all('li', class_='ads-ad')  # данные ответа

    if len(divs) > 0:  # если ответ на запрос что то содержит то
        log_visrec('soup_request', f'Всего найдено блоков ' + str(len(divs)), True)
        # дербаним выдачу. передаём ответ сервера (divs), номер запроса (url_counter), ключ(it_url['ques']),
        # и словарь с распарсенной выдачей(divs_requests)
        divs_text_shelves(divs, url_counter, it_url_soup, divs_requests)  # парсим данные ответа
        url_counter += 1
    else:
        log_visrec('soup_request', 'Ответ не содержит нужных данных :(', True)

    log_visrec('soup_request_divs_requests', divs_requests)
    return divs_requests


@timeit
def divs_text_shelves(my_divs, url_counter, url_ques, my_divs_requests=None):
    """парсим нужные данные ответа"""

    if len(my_divs_requests) == 0:  # если лист со словарями(значениями) не создан - создаём сразу с заголовками
        my_divs_requests.append({'rowNom': 'п\п',  # i_row
                                 'ques': 'Ключ',  # url_ques
                                 'company_title': 'Название компании',  # my_company_title
                                 'company_cid': 'Позиция',  # my_company_cid
                                 'company_link_1': 'Ссылка',  # my_company_link_1
                                 'company_sitelinks': 'Быстрая',  # my_company_sitelinks
                                 'company_text': 'Описалово',  # my_company_text
                                 'company_contact': 'Контакты'})  # my_company_contact
    i_row: int = 1
    for DIV in my_divs:
        try:
            my_company_cid: str = str(i_row - 1)
            log_visrec('company_cid ', my_company_cid)
        except:
            my_company_cid: str = ''
        try:
            my_company_link_1: str = DIV.find('div', attrs={'class': 'ads-visurl'}).text.replace('Реклама', ' ')
            x: int = my_company_link_1.index('/')
            my_company_link_1 = my_company_link_1[2:x]
            log_visrec('company_link_1 ', my_company_link_1)
        except:
            my_company_link_1: str = ''
        try:
            my_company_sitelinks: str = DIV.find('div', attrs={'ul': 'OkkX2d'}).text
            log_visrec('company_sitelinks ', my_company_sitelinks)
        except:
            my_company_sitelinks: str = ''
        try:
            my_company_text: str = DIV.find('div', attrs={'class': 'ads-creative'}).text
            log_visrec('company_text ', my_company_text)
        except:
            my_company_text: str = ''
        try:
            my_company_contact: str = DIV.find('div', attrs={'class': 'ads-visurl'}).text
            contact: str = my_company_contact
            contact = contact[len(contact) - len('0 (000) 000-00-00'):].strip()  # берём последние символы по маске
            contact = re.sub(r'\D', '', contact, count=0)  # удаляем всё кроме чисел
            if contact.isdigit() and len(contact) == 11:  # если осталось 11 цифр то это ном.телефона
                my_company_contact = my_company_contact[len(my_company_contact) - len('0 (000) 000-00-00'):]
            else:
                my_company_contact = ''
            log_visrec('company_contact ', my_company_contact)
        except:
            my_company_contact: str = ''
        try:
            my_company_title: str = DIV.text.replace('Почему мне показано это объявление?', ' ')
            my_company_title.replace('Реклама', '').strip()
            my_company_title.replace(my_company_contact, ' ')
            log_visrec('company_title ', my_company_title)
        except:
            my_company_title: str = 'N\A'
        log_visrec('конец итерации', f' * * * \n')

        my_divs_requests.append({'rowNom': i_row,
                                 'ques': url_ques,
                                 'company_title': my_company_title,
                                 'company_cid': my_company_cid,
                                 'company_link_1': my_company_link_1,
                                 'company_sitelinks': my_company_sitelinks,
                                 'company_text': my_company_text,
                                 'company_contact': my_company_contact})
        i_row = i_row + 1

    log_visrec('divs_text_shelves_divs_requests', my_divs_requests, False, True)
    return my_divs_requests


@timeit
def file_writer(my_divs_requests, my_full_path):
    """Записываем данные в файл Excel"""

    if len(my_divs_requests) <= 2:
        log_visrec('file_writer', f' \n Нет данных для записи в файл! \n ', True)
        exit()

    try:
        ExcelApp.app_open()
        if os.path.exists(my_full_path):  # файл excel существует то
            os.remove(my_full_path)  # удаляем
            ExcelApp.file_create(my_full_path)  # создаём новый файл

        try:
            log_visrec('file_writer', 'Начало записи данных в файл')
            try:
                # открываем книгу по пути full_path
                wb = com_client.Dispatch("Excel.Application").Workbooks.Open(my_full_path)
                log_visrec('file_writer', 'Книга открыта')

                doc_row: int = 1
                for divs_iter in my_divs_requests:  # записываем данные
                    if doc_row == 1:
                        wb.Worksheets('Лист1').Cells(doc_row, 1).Value = divs_iter['rowNom']
                    else:
                        wb.Worksheets('Лист1').Cells(doc_row, 1).Value = doc_row - 1
                    wb.Worksheets('Лист1').Cells(doc_row, 2).Value = divs_iter['ques']
                    wb.Worksheets('Лист1').Cells(doc_row, 3).Value = divs_iter['company_title']
                    wb.Worksheets('Лист1').Cells(doc_row, 4).Value = divs_iter['company_cid']
                    wb.Worksheets('Лист1').Cells(doc_row, 5).Value = divs_iter['company_link_1']
                    wb.Worksheets('Лист1').Cells(doc_row, 6).Value = divs_iter['company_sitelinks']
                    wb.Worksheets('Лист1').Cells(doc_row, 7).Value = divs_iter['company_text']
                    wb.Worksheets('Лист1').Cells(doc_row, 8).Value = divs_iter['company_contact']
                    doc_row += 1

                com_client.Dispatch("Excel.Application").DisplayAlerts = False  # отключаем обновление экрана
                wb.Close(True, my_full_path)  # сохраняем изменения и закрываем
                log_visrec('file_writer', 'Данные записаны', True)
            except:
                log_visrec('file_writer', 'Не удалось открыть книгу', True)
                ExcelApp.app_close()
        except:
            log_visrec('file_writer', 'Не удалось записать данные', True)
            return
    except:
        log_visrec('file_writer', 'Ошибка при создании файла', True)
    finally:

        ExcelApp.app_close()


@timeit
def main():
    """Основная функция с параметрами"""
    # идетификатор

    # базовый запрос
    base_url: str = f'https://www.google.com/search'
    # задаём полный путь к файлу с выгрузкой
    full_path = r'C:\Users\DeusEx\PycharmProjects\Parser_YD_GOO\Parser_Google.xlsx'
    # задаём полный путь к файлу с ключами
    queries_path = r'C:\Users\DeusEx\PycharmProjects\Parser_YD_GOO\queries.txt'
    # задаём максимальное кооличество запросов
    url_max_pos = 2
    # Задаём регион
    region = '+' + 'Краснодар'

    divs_requests: list = []  # создаем список

    urls = url_constructor(queries_path, base_url, region, url_max_pos)

    # divs_requests = Parser_YD_GOO(urls, divs_requests)  # последовательные запросы
    divs_requests = Parser_YD_GOO_parallel(urls, divs_requests)  # паралельные запросы
    file_writer(divs_requests, full_path)
    log_visrec('main', 'Парсинг завершен', True)


if __name__ == '__main__':
    main()
