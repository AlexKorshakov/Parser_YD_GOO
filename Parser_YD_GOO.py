import os
import requests
import win32com.client as com_client
from datetime import datetime
from typing import Union
# from tqdm import tqdm
from bs4 import BeautifulSoup


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
        # включаем обновление экрана и сообщения системы
        excel = com_client.Dispatch("Excel.Application")
        excel.Visible = True
        excel.DisplayAlerts = True
        excel.ScreenUpdating = True
        # выходим из Excel
        excel.Quit()
        return print('Книга excel закрыт')

    @classmethod
    def file_create(self, full_path):
        excel = com_client.Dispatch("Excel.Application")
        wbook = excel.Workbooks.Add()
        # wbook.Worksheets.Add()
        wbook.SaveAs(full_path)
        return print('Книга создана в full_path')


def Parser_YD_GOO(base_url, headers):
    start_def: datetime = datetime.now()
    MyRequests = []
    urls = [base_url]

    session = requests.Session()
    request = session.get(base_url, headers=headers)
    if request.status_code == 200:
        # print(request.content)
        soup = BeautifulSoup(request.text, 'lxml')

        try:
            pagination = soup.find_all('a', attrs={'class': 'link link_theme_none link_target_serp pager__item pager__item_kind_page i-bem'})
            count = int(pagination[-1].text)
            for i in range(count):
                if i >= 1:
                    url = str(base_url + '&p=' + str(i))
                    if url not in urls:
                        urls.append(url)
        except:
            pass
    for url in urls:
        request = session.get(url, headers=headers)
        soup = BeautifulSoup(request.text, 'lxml')
        divs = soup.find_all('li', attrs={'class': 'serp-item'})
        iRow = 0
        for div in divs:
            try:
                try:
                    companytitle = div.find('h2', attrs={'class': 'organic__title-wrapper typo typo_text_l typo_line_m'}).text
                except:
                    pass
                try:
                    companyLink_1 = div.find('a', attrs={'class': 'link link_theme_outer path__item i-bem'}).text
                    # Link_2 = div.find(class_='link link_theme_outer path__item i-bem link_js_inited')['href']
                except:
                    pass
                try:
                    companytext = div.find('div', attrs={'class': 'text-container typo typo_text_m typo_line_m organic__text'}).text
                except:
                    pass
                iRow: Union[int, iRow] = iRow + 1

                MyRequests.append({
                    'rowNom': iRow,
                    'companytitle': companytitle,
                    'companyLink_1': companyLink_1,
                    'companytext': companytext
                })
            except:
                pass
        finish = datetime.now()
        print('Всего:' + str(len(MyRequests)) + ' ' + 'Время выполнения lxml: ' + str(finish - start_def))
    else:
        print('Error or Done ' + str(request.status_code))
    return MyRequests


def file_writer_win32(MyRequests , fullpath):
    start_def: datetime = datetime.now()
    ExcelApp.app_open()

    iRow: int = 0
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
                    wb.Worksheets('Лист1').Cells(iRow, 1).Value = iRow  # - 2
                    wb.Worksheets('Лист1').Cells(iRow, 2).Value = MyRequest['companytitle']
                    wb.Worksheets('Лист1').Cells(iRow, 3).Value = MyRequest['companyLink_1']
                    wb.Worksheets('Лист1').Cells(iRow, 4).Value = MyRequest['companytext']

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
base_url: str = f'https://yandex.ru/search/?text=%D0%B7%D0%B0%D0%BF%D1%87%D0%B0%D1%81%D1%82%D0%B8%20%D0%BD%D0%B0%20%D1%82%D1%80%D0%B0%D0%BA%D1%82%D0%BE%D1%80&lr=2 '
fullpath = r'C:\Users\DeusEx\PycharmProjects\Parser_YD_GOO\Parser_YD_GOO.xlsx'

MyRequest = Parser_YD_GOO(base_url, headers)
file_writer_win32(MyRequest, fullpath)
print('Парсинг завершен')
