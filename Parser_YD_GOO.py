import os
import random
import time
import requests
import win32com.client as com_client
from datetime import datetime
from bs4 import BeautifulSoup
from requests import Response
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError
from tqdm import tqdm
from win32com.client import Dispatch


class ExcelApp(object):

    @classmethod
    def app_open(cls):
        # открываем Excel в скрытом режиме, отключаем обновление экрана и сообщения системы
        excel = Dispatch("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        excel.ScreenUpdating = False
        return print('Успешно запустили Excel')

    @classmethod
    def file_create(cls, full_path):
        excel = Dispatch("Excel.Application")
        wbook = excel.Workbooks.Add()
        # wbook.Worksheets.Add()
        wbook.SaveAs(full_path)
        return print('Книга создана в my_full_path')

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
            return print('Excel закрыт')


def url_constructor(queries_path, selected_base_url, selected_region, max_pos=3):
    # формируем запрос из запчастей
    urls = []
    # открываем файл с ключами по пути queries_path и считываем ключи
    queries = open(queries_path, 'r', encoding='utf-8')
    query: list = [x.strip() for x in queries]
    queries.close()

    for ques in query:  # перебираем ключи и формируем url на их основе
        divs_ques: str = ques
        # breakpoint()
        mod_url = selected_base_url + ques.replace(' ', '%20') + '&lr=' + str(selected_region)
        print('url ' + mod_url)

        for i in range(max_pos):  # дополняем url и формируем для кажного запроса
            if i == 0:
                urls.append({'url': mod_url, 'ques': divs_ques})  # перывя ссылка с ключем
            else:
                url = str(mod_url + '&p=' + str(i))
                if url not in urls:
                    urls.append({'url': url, 'ques': divs_ques})  # остальные ссылки с ключом
                    print('url ' + url)
    return urls


def time_rand(t_start: int = 1, t_stop: int = 30):
    # функция задержки выполнения кода на рандомный промежуток
    time_random = random.randint(t_start, t_stop)  # задаём рандомеый промежуток задержки (от 1 до 30 сек)
    print('Время ожидания нового запроса time_rand ' + str(time_random) + ' sec')
    for _ in tqdm(range(time_random)):
        time.sleep(1)


def Parser_YD_GOO(urls, my_headers):
    # основная функция парсера
    # создаём сессию (session), отправляем запрос (request), получаем ответ (request.text), варим суп (soup)
    url_counter: int = 0
    divs_requests = []  # создаем список ДО начала сессии
    for it_url in urls:
        if url_counter != 0:  # Для всех ссылок КРОМЕ ПЕРВОЙ задаём рандомный промежуток задежки.
            time_rand(2, 15)

        adapter_yd = HTTPAdapter(max_retries=3)  # транспортный адаптер — максимальное количество повторов запроса
        start_def: datetime = datetime.now()
        session = requests.Session()  # устанавливаем сессию
        session.mount(it_url['url'], adapter_yd)
        # proxy?
        try:
            request: Response = session.get(it_url['url'], headers=my_headers, stream=True)  # запрос
            if request.status_code == 200:  # если запрос был выполнен успешно то
                soup = BeautifulSoup(request.text, 'lxml')  # ответ
                divs = soup.find_all('li', class_='serp-item')  # данные ответа

                if len(divs) > 0:  # если ответ на запрос что то содержит то
                    print(f' \n Всего найдено ' + str(len(divs)))
                    # дербаним выдачу. передаём ответ сервера (divs), номер запроса (url_counter), ключ(it_url['ques']),
                    # и словарь с распарсенной выдачей(divs_requests)
                    divs_text_shelves(divs, str(url_counter), it_url['ques'], divs_requests)  # парсим данные ответа
                    url_counter += 1
                else:
                    print('Ответ не содержит нужных данных :(')
                    print('Ответ сайта ' + str(request.status_code))
            else:
                print('Неудачный запрос! Ответ сервера ' + str(request.status_code))
                print('Error or Done {0}'.format(str(request.status_code)))
        except ConnectionError as ce:
            print(f'\nОшибка при установке соединения! проверьте подключение!\n ')
            print(ce)
            continue
        print('Время выполнения Parser_YD_GOO: ' + str(datetime.now() - start_def))

    return divs_requests


def divs_text_shelves(my_divs, url_counter, url_ques, my_divs_requests=None):
    #  парсим нужные данные ответа
    if len(my_divs_requests) == 0:  # если лист со словарями(значениями) не создан - создаём сразу с заголовками
        my_divs_requests.append({'rowNom': 'п\п',
                                 'ques': 'Ключ',
                                 'company_title': 'Название компании',
                                 'company_cid': 'Позиция',
                                 'company_link_1': 'Ссылка',
                                 'company_sitelinks': 'Быстрая',
                                 'company_text': 'Описалово',
                                 'company_contact': 'Контакты'})
    i_row: int = 1
    for DIV in my_divs:
        i_row = i_row + 1
        try:
            my_company_title: str = DIV.find('h2', attrs={
                'class': "organic__title-wrapper typo typo_text_l typo_line_m"}).text
            print('company_title ' + my_company_title)
        except:
            my_company_title: str = ''
        try:
            my_company_cid: str = str(url_counter) + str(DIV.get('data-cid'))
            print('company_cid ' + my_company_cid)
        except:
            my_company_cid: str = ''
        try:
            my_company_link_1: str = DIV.find('a', attrs={
                'class': 'link link_theme_outer path__item i-bem'}).text
            print('company_link_1 ' + my_company_link_1)
        except:
            my_company_link_1: str = ''
        try:
            my_company_sitelinks: str = DIV.find('div', attrs={
                'class': 'sitelinks sitelinks_size_m organic__sitelinks'}).text
            print('company_sitelinks ' + my_company_sitelinks)
        except:
            my_company_sitelinks: str = ''
        try:
            my_company_text: str = DIV.find('div', attrs={
                'class': 'text-container typo typo_text_m typo_line_m organic__text'}).text
            print('company_text ' + my_company_text)
        except:
            my_company_text: str = ''
        try:
            my_company_contact: str = DIV.find('div', attrs={
                'class': 'serp-meta__item'}).text
            print('company_contact ' + my_company_contact)
        except:
            my_company_contact: str = ''
        print(f' * * * \n')

        my_divs_requests.append({'rowNom': i_row,
                                 'ques': url_ques,
                                 'company_title': my_company_title,
                                 'company_cid': my_company_cid,
                                 'company_link_1': my_company_link_1,
                                 'company_sitelinks': my_company_sitelinks,
                                 'company_text': my_company_text,
                                 'company_contact': my_company_contact})
    return my_divs_requests


def file_writer(my_divs_requests, my_full_path):
    if len(my_divs_requests) == 0:
        print(f' \n Нет данных для записи в файл! \n ')
        exit()

    start_def: datetime = datetime.now()
    try:
        ExcelApp.app_open()
        if os.path.exists(my_full_path):  # файл excel существует то
            os.remove(my_full_path)  # удаляем
            ExcelApp.file_create(my_full_path)  # создаём новый файл

        try:
            print('Начало записи данных в файл')
            try:
                # открываем книгу по пути full_path
                wb = com_client.Dispatch("Excel.Application").Workbooks.Open(my_full_path)
                print('Книга открыта')

                doc_row: int = 1
                for divs_iter in my_divs_requests:  # записываем данные
                    wb.Worksheets('Лист1').Cells(doc_row, 1).Value = divs_iter['rowNom']
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
                print('Данные записаны')
            except:
                print('Не удалось открыть книгу')
                ExcelApp.app_close()
        except:
            print('Не удалось записать данные')
            return
    except:
        print('Ошибка при создании файла')
    finally:

        ExcelApp.app_close()
        finish = datetime.now()
        print('Время выполнения file_writer: ' + str(finish - start_def))


def main():
    headers = {'accept': '*/*',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
    # headers = {'accept': '*/*',
    #            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
    #                          'Chrome/80.0.3987.106 Safari/537.36'}
    # базовый запрос
    base_url: str = f'https://www.yandex.ru/search/ads?text='
    # задаём полный путь к файлу с выгрузкой
    full_path = r'C:\Users\DeusEx\PycharmProjects\Parser_YD_GOO\Parser_YD_GOO.xlsx'
    # задаём полный путь к файлу с ключами
    queries_path = r'C:\Users\DeusEx\PycharmProjects\Parser_YD_GOO\queries.txt'
    # задаём максимальное кооличество запросов
    url_max_pos = 1
    # Задаём регион. Санкт-Петербург – 2. Краснодар  - 35
    # Список идентификаторов российских регионов https://tech.yandex.ru/xml/doc/dg/reference/regions-docpage/
    region = 32

    urls = url_constructor(queries_path, base_url, region, url_max_pos)
    divs_requests = Parser_YD_GOO(urls, headers)
    file_writer(divs_requests, full_path)
    print(f'\nПарсинг завершен\n ')


if __name__ == '__main__':
    main()
