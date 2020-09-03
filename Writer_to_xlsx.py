import os

import win32com.client
from win32com.universal import com_error

import general_setting as gs
from Parser_Yandex import PASSED
from Servises import Notify_by_Message as Nm
from Servises.Notify_by_Message import get_function_name as gfn, l_message


class Writer_to_xlsx:
    def __init__(self, divs_requests, full_path_to_file):
        self.divs_requests = divs_requests
        self.excel_app = None
        self.wbook = None
        self.full_path_to_file = full_path_to_file

    def file_writer(self):
        """Записываем данные в файл Excel."""

        doc_row: int = 1
        self.create_headers_divs_requests()

        if len(self.divs_requests) <= 2:
            l_message(gfn(), f' \n Нет данных для записи в файл! \n ', color=Nm.bcolors.FAIL)
            return

        excel_app, wbook = self.create_workbook()

        if __debug__ and not PASSED:
            assert excel_app is not None, 'Не удалось подключится к Ecxel'
            assert wbook is not None, 'Не удалось создать книгу'

        try:
            l_message(gfn(), 'Начало записи данных в файл', color=Nm.bcolors.OKBLUE)

            for divs_iter in self.divs_requests:  # записываем данные
                if doc_row == 1:
                    wbook.Worksheets('Лист1').Cells(doc_row, 1).Value = divs_iter['rowNom']
                else:
                    wbook.Worksheets('Лист1').Cells(doc_row, 1).Value = doc_row - 1

                wbook.Worksheets('Лист1').Cells(doc_row, 2).Value = divs_iter['ques']
                wbook.Worksheets('Лист1').Cells(doc_row, 3).Value = divs_iter['company_title']
                wbook.Worksheets('Лист1').Cells(doc_row, 4).Value = divs_iter['company_cid']
                wbook.Worksheets('Лист1').Cells(doc_row, 5).Value = divs_iter['company_link_1']
                wbook.Worksheets('Лист1').Cells(doc_row, 6).Value = divs_iter['company_sitelinks']
                wbook.Worksheets('Лист1').Cells(doc_row, 7).Value = divs_iter['company_text']
                wbook.Worksheets('Лист1').Cells(doc_row, 8).Value = divs_iter['company_contact']
                doc_row += 1

            wbook.Close(True, self.full_path_to_file)  # сохраняем изменения и закрываем
            self.excel_app_quit()

            l_message(gfn(), 'Данные записаны', color=Nm.bcolors.OKBLUE)

        except Exception as err:
            l_message(gfn(), f" Exception: {repr(err)}", color=Nm.bcolors.FAIL)
            l_message(gfn(), 'Не удалось записать данные', color=Nm.bcolors.FAIL)
            self.excel_app_quit()
            return

    def create_headers_divs_requests(self):
        """Создание заголовков в list с распарсенными данными."""

        return self.divs_requests.insert(0, gs.heders)

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