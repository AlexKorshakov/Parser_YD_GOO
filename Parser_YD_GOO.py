import os
import requests
import random
import time
from tqdm import tqdm
import win32com.client as com_client
from datetime import datetime
from bs4 import BeautifulSoup


class ExcelApp(object):

    @classmethod
    def app_open(cls):
        # открываем Excel в скрытом режиме, отключаем обновление экрана и сообщения системы
        excel = com_client.Dispatch("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        excel.ScreenUpdating = False
        return print('Книга excel открыта')

    @classmethod
    def app_close(cls):

        global excel
        try:
            # включаем обновление экрана и сообщения системы
            excel = com_client.Dispatch("Excel.Application")
            excel.Visible = True
            excel.DisplayAlerts = True
            excel.ScreenUpdating = True
            # выходим из Excel
        finally:
            excel.Quit()
        return print('Книга excel закрыт')

    @classmethod
    def file_create(cls, full_path):
        excel = com_client.Dispatch("Excel.Application")
        wbook = excel.Workbooks.Add()
        # wbook.Worksheets.Add()
        wbook.SaveAs(full_path)
        return print('Книга создана в full_path')


def Url_constructor(queries_path, selected_base_url, selected_region, max_pos=3):
    global urls
    urls = []
    queries = open(queries_path, 'r', encoding='utf-8')
    query: list = [x.strip() for x in queries]
    queries.close()

    for ques in query:
        mod_url = selected_base_url + ques.replace(' ', '%20') + '&lr=' + str(selected_region)
        urls.append(mod_url)
        print('url ' + mod_url)
        for i in range(max_pos):
            if i >= 1:
                url = str(mod_url + '&p=' + str(i))
                if url not in urls:
                    urls.append(url)
                    print('url ' + url)
    return urls


# noinspection PyGlobalUndefined
def Parser_YD_GOO(my_urls, my_headers):
    global company_title, company_link_1, company_text, company_contact, bar, divs, div, soup, request, company_sitelinks

    my_requests = []

    for url in my_urls:
        if url == my_urls[0]:
            pass
        else:
            time_rand = random.randint(1, 30)
            print('Время ожидания нового запроса time_rand ' + str(time_rand) + ' sec')

            # my_counter = range(time_rand)
            for item in tqdm(range(time_rand)):
                time.sleep(1)
            # time.sleep(time_rand)

        start_def: datetime = datetime.now()
        session = requests.Session()

        # proxy?
        request = session.get(url, headers=my_headers, stream=True)
        if request.status_code == 200:
            soup = BeautifulSoup(request.text, 'lxml')
            # print(soup)
            divs = soup.find_all('li', class_='serp-item')
            # divs = soup.find_all('li', attrs={'class': 'serp-item'})
            if len(divs) > 0:
                print(str(len(divs)))
            else:
                print('Ответ не содержит нужных данных :(')
                print('Ответ сайта ' + str(request.status_code))
        else:
            print('Ответ сервера ' + str(request.status_code))

        i_row: int = 0
        for div in divs:

            try:
                try:
                    company_title = ''
                    company_title = div.find('h2', attrs={
                        'class': "organic__title-wrapper typo typo_text_l typo_line_m"}).text
                    print('company_title ' + company_title)
                except:
                    pass
                try:
                    company_link_1 = ''
                    company_link_1 = div.find('a', attrs={'class': 'path path_show-https organic__path'}).text
                    # Link_2 = div.find(class_='link link_theme_outer path__item i-bem link_js_inited')['href']
                    print('company_link_1 ' + company_link_1)
                except:
                    pass
                try:

                    company_sitelinks = ''
                    company_sitelinks = div.find('div', attrs={
                        'class': 'sitelinks sitelinks_size_m organic__sitelinks'}).text
                    print('company_sitelinks ' + company_sitelinks)
                except:
                    pass

                try:
                    company_text = ''
                    company_text = div.find('div', attrs={
                        'class': 'text-container typo typo_text_m typo_line_m organic__text'}).text
                    print('company_text ' + company_text)
                except:
                    pass
                try:
                    company_contact = ''
                    company_contact = div.find('div', attrs={
                        'class': 'serp-meta__item'}).text
                    print('company_contact ' + company_contact)
                except:
                    pass
                print(' * * * ')
                i_row: int = i_row + 1

                my_requests.append({
                    'rowNom': i_row,
                    'company_title': company_title,
                    'company_link_1': company_link_1,
                    'company_sitelinks': company_sitelinks,
                    'company_text': company_text,
                    'company_contact': company_contact
                })
            except:
                pass
        finish = datetime.now()
        print('Всего:' + str(len(my_requests)) + ' ' + 'Время выполнения lxml: ' + str(finish - start_def))
    else:
        print('Error or Done ' + str(request.status_code))

    return my_requests


def file_writer_win32(my_requests, full_path):
    if int(len(my_requests)) == 0:
        print('нет данных для записи')
        exit()
    else:
        start_def: datetime = datetime.now()
        try:
            ExcelApp.app_open()
            if os.path.exists(full_path):
                os.remove(full_path)
                ExcelApp.file_create(full_path)
            else:
                pass
                ExcelApp.file_create(full_path)

            try:
                print('начало file_writer_win32')

                try:
                    wb = com_client.Dispatch("Excel.Application").Workbooks.Open(full_path)
                    print('Книга создана')

                    i_row: int = 1
                    wb.Worksheets('Лист1').Cells(i_row, 1).Value = r'Номер п\п'
                    wb.Worksheets('Лист1').Cells(i_row, 2).Value = 'Название компании'
                    wb.Worksheets('Лист1').Cells(i_row, 3).Value = 'Ссылка'
                    wb.Worksheets('Лист1').Cells(i_row, 4).Value = 'Быстрая ссылка'
                    wb.Worksheets('Лист1').Cells(i_row, 5).Value = 'Описалово'
                    wb.Worksheets('Лист1').Cells(i_row, 6).Value = 'Контакты'

                    for MyRequest in my_requests:
                        i_row += 1
                        wb.Worksheets('Лист1').Cells(i_row, 1).Value = i_row
                        wb.Worksheets('Лист1').Cells(i_row, 2).Value = MyRequest['company_title']
                        wb.Worksheets('Лист1').Cells(i_row, 3).Value = MyRequest['company_link_1']
                        wb.Worksheets('Лист1').Cells(i_row, 4).Value = MyRequest['company_sitelinks']
                        wb.Worksheets('Лист1').Cells(i_row, 5).Value = MyRequest['company_text']
                        wb.Worksheets('Лист1').Cells(i_row, 6).Value = MyRequest['company_contact']

                except:
                    print('Книга не создана')
                    ExcelApp.app_close()

            except:
                print('Не книга не создана')
                return

        except:
            print('file_writer_win32 не сработал')

        finally:
            ExcelApp.app_close()
            finish = datetime.now()
            print('Время выполнения file_writer_win32: ' + str(finish - start_def))


headers = {'accept': '*/*', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
# headers = {'accept': '*/*',
#            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
#                          'Chrome/80.0.3987.106 Safari/537.36'}
# базовый запрос
base_url: str = f'https://www.yandex.ru/search/ads?text='
# задаём полный путь к файлу с выгрузкой
full_path = r'C:\Users\DeusEx\PycharmProjects\Parser_YD_GOO\Parser_YD_GOO.xlsx'
queries_path = r'C:\Users\DeusEx\PycharmProjects\Parser_YD_GOO\queries.txt'
# задаём максимальное кооличество запросов
maxPos = 4
# Задаём регион. Санкт-Петербург – 2. Краснодар  - 35
# Список идентификаторов российских регионов https://tech.yandex.ru/xml/doc/dg/reference/regions-docpage/
region = 2

MyRequest = Parser_YD_GOO(Url_constructor(queries_path, base_url, region, maxPos), headers)
file_writer_win32(MyRequest, full_path)
print('Парсинг завершен')
