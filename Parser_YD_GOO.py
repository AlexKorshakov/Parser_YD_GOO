import os
import random
import time
from datetime import datetime
import requests
import win32com.client as com_client
from bs4 import BeautifulSoup
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
        return print('Книга excel открыта')

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
            # выходим из Excel
            excel.Quit()
            return print('Книга excel закрыт')


def Url_constructor(queries_path, selected_base_url, selected_region, max_pos=3):
    global divs_ques
    urls = []
    queries = open(queries_path, 'r', encoding='utf-8')
    query: list = [x.strip() for x in queries]
    queries.close()

    for ques in query:
        divs_ques = ques
        # breakpoint()
        mod_url = selected_base_url + ques.replace(' ', '%20') + '&lr=' + str(selected_region)
        print('url ' + mod_url)
        for i in range(max_pos):
            if i == 0:
                urls.append({'url': mod_url, 'ques': divs_ques})
            else:
                url = str(mod_url + '&p=' + str(i))
                if url not in urls:
                    urls.append({'url': url, 'ques': divs_ques})
                    print('url ' + url)
    return urls


def Parser_YD_GOO(urls, my_headers, full_path):
    global divs, soup, request, my_requests, requests, divs_requests
    url_counter: int = 0
    divs_requests = []
    for it_url in urls:
        if url_counter != 0:
            # Для всех ссылок КРОМЕ ПЕРВОЙ задаём рандомный промежуток задежки. ШОБ ЗРАЗУ НЕ ЗАБАНИЛИ
            # задаём рандомеый промежуток задержки (от 1 до 30 сек)
            time_rand = random.randint(1, 30)
            print('Время ожидания нового запроса time_rand ' + str(time_rand) + ' sec')
            for _ in tqdm(range(time_rand)):
                time.sleep(1)

        start_def: datetime = datetime.now()
        session = requests.Session()
        # proxy?
        request = session.get(it_url['url'], headers=my_headers, stream=True)
        if request.status_code == 200:
            soup = BeautifulSoup(request.text, 'lxml')
            divs = soup.find_all('li', class_='serp-item')
            if len(divs) > 0:
                print('Всего найдено ' + str(len(divs)))
                # дербаним выдачу
                divs_text_shelves(divs, str(url_counter), it_url['ques'], divs_requests)
                url_counter += 1
            else:
                print('Ответ не содержит нужных данных :(')
                print('Ответ сайта ' + str(request.status_code))
        else:
            print('Неудачный запрос! Ответ сервера ' + str(request.status_code))
        print('Время выполнения Parser_YD_GOO: ' + str(datetime.now() - start_def))
    else:
        print('Error or Done ' + str(request.status_code))
    file_writer(divs_requests, full_path)


def divs_text_shelves(my_divs, url_counter, url_ques, my_divs_requests=None):
    #  парсим нужные данные
    #  если лист со словарями(значениями) не создан - создаём сразу с заголовками
    if len(my_divs_requests) == 0:
        my_divs_requests.append(
            {'rowNom': 'п\п',
             'ques': 'Ключ',
             'company_title': 'Название компании',
             'company_cid': 'Позиция',
             'company_link_1': 'Ссылка',
             'company_sitelinks': 'Быстрая',
             'company_text': 'Описалово',
             'company_contact': 'Контакты'}
        )

    i_row: int = 1
    for DIV in my_divs:
        i_row = i_row + 1
        try:
            my_company_title = DIV.find('h2', attrs={
                'class': "organic__title-wrapper typo typo_text_l typo_line_m"}).text
            print('company_title ' + my_company_title)
        except:
            my_company_title: str = ''
        try:
            my_company_cid = str(url_counter) + str(DIV.get('data-cid'))
            print('company_cid ' + my_company_cid)
        except:
            my_company_cid: str = ''
        try:
            my_company_link_1 = DIV.find('a', attrs={
                'class': 'link link_theme_outer path__item i-bem'}).text
            print('company_link_1 ' + my_company_link_1)
        except:
            my_company_link_1: str = ''
        try:
            my_company_sitelinks = DIV.find('div', attrs={
                'class': 'sitelinks sitelinks_size_m organic__sitelinks'}).text
            print('company_sitelinks ' + my_company_sitelinks)
        except:
            my_company_sitelinks: str = ''
        try:
            my_company_text = DIV.find('div', attrs={
                'class': 'text-container typo typo_text_m typo_line_m organic__text'}).text
            print('company_text ' + my_company_text)
        except:
            my_company_text: str = ''
        try:
            my_company_contact = DIV.find('div', attrs={
                'class': 'serp-meta__item'}).text
            print('company_contact ' + my_company_contact)
        except:
            my_company_contact: str = ''
        print(' * * * ')

        my_divs_requests.append(
            {'rowNom': i_row,
             'ques': url_ques,
             'company_title': my_company_title,
             'company_cid': my_company_cid,
             'company_link_1': my_company_link_1,
             'company_sitelinks': my_company_sitelinks,
             'company_text': my_company_text,
             'company_contact': my_company_contact}
        )
    return my_divs_requests


def file_writer(my_divs_requests, my_full_path):
    # if int(len(divs_requests)) == 0:
    #     print('нет данных для записи')
    #     exit()
    # else:
    start_def: datetime = datetime.now()
    try:
        ExcelApp.app_open()
        if os.path.exists(my_full_path):
            os.remove(my_full_path)
            ExcelApp.file_create(my_full_path)
        else:
            pass
            #  ExcelApp.file_create(my_full_path)
        try:
            print('начало file_writer')
            try:
                # открываем книгу по пути full_path
                wb = com_client.Dispatch("Excel.Application").Workbooks.Open(my_full_path)
                print('Книга создана')

                doc_row: int = 1
                for divs_iter in my_divs_requests:
                    wb.Worksheets('Лист1').Cells(doc_row, 1).Value = divs_iter['rowNom']
                    wb.Worksheets('Лист1').Cells(doc_row, 2).Value = divs_iter['ques']
                    wb.Worksheets('Лист1').Cells(doc_row, 3).Value = divs_iter['company_title']
                    wb.Worksheets('Лист1').Cells(doc_row, 4).Value = divs_iter['company_cid']
                    wb.Worksheets('Лист1').Cells(doc_row, 5).Value = divs_iter['company_link_1']
                    wb.Worksheets('Лист1').Cells(doc_row, 6).Value = divs_iter['company_sitelinks']
                    wb.Worksheets('Лист1').Cells(doc_row, 7).Value = divs_iter['company_text']
                    wb.Worksheets('Лист1').Cells(doc_row, 8).Value = divs_iter['company_contact']
                    doc_row += 1

                com_client.Dispatch("Excel.Application").DisplayAlerts = False
                wb.Close(True, my_full_path)
            except:
                print('Книга не создана')
                ExcelApp.app_close()
        except:
            print('Не книга не создана')
            return
    except:
        print('file_writer не сработал')
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

    urls = Url_constructor(queries_path, base_url, region, url_max_pos)
    Parser_YD_GOO(urls, headers, full_path)
    file_writer(divs_requests, full_path)
    print('Парсинг завершен')


if __name__ == '__main__':
    main()
