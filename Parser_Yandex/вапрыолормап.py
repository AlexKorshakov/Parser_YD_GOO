from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QPlainTextEdit, QTextEdit, QMessageBox, \
    QApplication
from PySide2.QtWidgets import QPushButton
from PySide2.QtCore import QSize
# from PySide2.QtGui import *
import sys


class Cam_Ext(QMainWindow):

    def __init__(self, Custom):
        QMainWindow.__init__(self, Cam_Ext)

        self.setMinimumSize(QSize(700, 900))
        self.setWindowTitle("Print groupes seletionner")

        ###btn1
        self.btn = QtWidgets.QPushButton('Print groupes', self)
        self.btn.move(180, 100)
        self.btn.resize(350, 40)
        self.btn.setStyleSheet(
            "background-color: rgb(255, 255, 255); font-family: arial; font-size: 17px; font-weight: bold;")
        self.btn.clicked.connect(self.Renommer)

        self.line = QPlainTextEdit(self)
        self.line.setStyleSheet("font-size: 12px; font-weight: bold; ")
        self.line.move(100, 170)
        self.line.resize(500, 400)
        self.line.setText(self.Renommer)
        # self.line.setPlaceholderText(self.Renommer)

        self.show()

    def Renommer(self):

        import PhotoScan
        import os
        doc = PhotoScan.app.document
        pr_name = doc.path
        project_name = os.path.split(pr_name)[-1]
        print(project_name)

        groups = doc.chunk.camera_groups
        for group in groups:
            # print(group)
            if group.selected:
                self.line.appendPlainText("{}-{}-{};".format(project_name, group, seg))


def main():
    # global doc
    # doc = PhotoScan.app.document

    global app
    app = QtWidgets.QApplication.instance()
    Custom = app.activeWindow()

    dlg = Cam_Ext(Custom)

# PhotoScan.app.addMenuItem("Pp/Print groupes seletionner", main)
