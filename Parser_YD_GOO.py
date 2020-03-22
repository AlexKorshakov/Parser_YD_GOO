import os
import requests
import win32com.client as com_client
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Union
import time


class ExcelApp(object):

    @classmethod
    def app_open(self):
        # открываем Excel в скрытом режиме, отключаем обновление экрана и сообщения системы
        excel = com_client.Dispatch("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        excel.ScreenUpdating = False
        return print('Книга excel открыта')

    @classmethod
    def app_close(self):
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
    def file_create(self, full_path):
        excel = com_client.Dispatch("Excel.Application")
        wbook = excel.Workbooks.Add()
        # wbook.Worksheets.Add()
        wbook.SaveAs(full_path)
        return print('Книга создана в full_path')


def Parser_YD_GOO(base_url, headers, maxPos = 5):
    global company_title, company_link_1, company_text, company_contact, bar, divs, div, soup
    start_def: datetime = datetime.now()
    MyRequests = []
    urls = [base_url]

    session = requests.Session()
    request = session.get(base_url, headers=headers)
    if request.status_code == 200:
        soup = BeautifulSoup(request.text, 'lxml')

        for i in range(maxPos):
            if i >= 1:
                url = str(base_url + '&p=' + str(i))
                if url not in urls:
                    urls.append(url)
                    print('url ' + url)

    for url in urls:
        session = requests.Session()
        request = session.get(url, headers=headers,  stream = True)
        if request.status_code == 200:
            soup = BeautifulSoup(request.text, 'lxml')
            divs = soup.find_all('li', class_='serp-item')
            # divs = soup.find_all('li', attrs={'class': 'serp-item'})
            if len(divs) > 0:
                print(str(len(divs)))
            else:
                print('неудачный запрос')
            iRow: int = 0

        for div in divs:

            try:
                try:
                    company_title = div.find('h2',
                                             attrs={'class': 'organic__title-wrapper typo typo_text_l typo_line_m'}).text
                    print('company_title ' + company_title)
                except:
                    pass
                try:
                    company_link_1 = div.find('a', attrs={'class': 'link link_theme_outer path__item i-bem'}).text
                    # Link_2 = div.find(class_='link link_theme_outer path__item i-bem link_js_inited')['href']
                    print('company_link_1 ' + company_link_1)
                except:
                    pass
                try:
                    company_text = div.find('div', attrs={
                        'class': 'text-container typo typo_text_m typo_line_m organic__text'}).text
                    print('company_text ' + company_text)
                except:
                    pass
                try:
                    company_contact = div.find('div', attrs={
                        'class': 'serp-meta__item'}).text
                    print('company_contact ' + company_contact)
                except:
                    pass

                iRow: int = iRow + 1

                MyRequests.append({
                    'rowNom': iRow,
                    'company_title': company_title,
                    'company_link_1': company_link_1,
                    'company_text': company_text,
                    'company_contact': company_contact
                })
            except:
                pass
        finish = datetime.now()
        print('Всего:' + str(len(MyRequests)) + ' ' + 'Время выполнения lxml: ' + str(finish - start_def))
    else:
        print('Error or Done ' + str(request.status_code))
    return MyRequests


def file_writer_win32(MyRequests, fullpath):
    if int(len(MyRequests)) == 0:
        print('нет данных для записи')
        exit()
    else:

        start_def: datetime = datetime.now()
        ExcelApp.app_open()

        try:
            if os.path.exists(fullpath):
                os.remove(fullpath)
                ExcelApp.file_create(fullpath)
            else:
                pass
                ExcelApp.file_create(fullpath)

            try:
                print('начало file_writer_win32')

                try:
                    wb = com_client.Dispatch("Excel.Application").Workbooks.Open(fullpath)
                    print('Книга создана')

                    iRow: int = 0
                    for MyRequest in MyRequests:
                        iRow += 1
                        wb.Worksheets('Лист1').Cells(iRow, 1).Value = iRow
                        wb.Worksheets('Лист1').Cells(iRow, 2).Value = MyRequest['company_title']
                        wb.Worksheets('Лист1').Cells(iRow, 3).Value = MyRequest['company_link_1']
                        wb.Worksheets('Лист1').Cells(iRow, 4).Value = MyRequest['company_text']
                        wb.Worksheets('Лист1').Cells(iRow, 5).Value = MyRequest['company_contact']

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


headers = {'accept': '*/*',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/80.0.3987.106 Safari/537.36'}
base_url: str = f'https://yandex.ru/search/?text=%D0%B7%D0%B0%D0%BF%D1%87%D0%B0%D1%81%D1%82%D0%B8%20%D0%BD%D0%B0%20%D1%82%D1%80%D0%B0%D0%BA%D1%82%D0%BE%D1%80&lr=2'
fullpath = r'C:\Users\DeusEx\PycharmProjects\Parser_YD_GOO\Parser_YD_GOO.xlsx'
maxPos = 5

MyRequest = Parser_YD_GOO(base_url, headers, maxPos)
file_writer_win32(MyRequest, fullpath)
print('Парсинг завершен')
