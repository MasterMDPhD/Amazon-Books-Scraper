import ui_scraper as uiQT
import ui_book as uiBook
import ui_about as uiAbout
import ui_contacts as uiContacts

import db_utils as dbUtils

import sys
import os.path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QAction, QFileDialog, QMessageBox, QInputDialog, QMenu
from PyQt5.QtCore import QThread, pyqtSignal, QObject, Qt
import threading
import time
import re
import requests
from bs4 import BeautifulSoup
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

from PyQt5.QtGui import QPixmap, QIcon

import urllib
from urllib.error import URLError
import webbrowser

class ImageLink(QObject):
    # This class initiate image cell in Books table
    data_changed_image = pyqtSignal(int, str, str, name="dataChanged_image")
    fetched_image = pyqtSignal(int, str, str, name="fetched_image_signal")

    def __init__(self, ui):
        super().__init__()
        self.ui = ui
    def onDataChanged(self,rowPosition: int, isbn: str, img_url: str) -> None:
        table = self.ui.books_tableWidget
        pixmap = QPixmap('books_images/' + isbn + '.jpg')
        pixmap = pixmap.scaled(100, 100, QtCore.Qt.KeepAspectRatio)
        if (not pixmap.isNull()):
            label = QtWidgets.QLabel()
            label.setPixmap(pixmap)
            table.setCellWidget(rowPosition,0, label)
        else:
            table.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(img_url))
 
    def onFetchedBookImage(self,rowPosition: int, isbn: str, img_url: str) -> None:
        table = self.ui.fetchedBooks_tableWidget
        pixmap = QPixmap('books_images/' + isbn + '.jpg')
        pixmap = pixmap.scaled(100, 100, QtCore.Qt.KeepAspectRatio)
        if (not pixmap.isNull()):
            label = QtWidgets.QLabel()
            label.setPixmap(pixmap)
            table.setCellWidget(rowPosition,0, label)
        else:
            item_imageDownload.download_image_signal.emit(isbn, img_url, rowPosition)


# ---------------------------------------
from PyQt5.QtCore import pyqtSlot, Qt, QUrl
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)
class ImageDownload(QObject):
    # This class initiate image cell in Books table
    download_image = pyqtSignal(str, str,int, name="download_image_signal")

    def __init__(self, ui):
        super().__init__()
        self.ui = ui

    def getCheckImage(self) -> None:
        request = QNetworkRequest(QUrl(self.url))
        request.setRawHeader(b'User-Agent', self.userAgent)
        self.reply = self.manager.get(request)

    def display(self, isbn: str, url: str, rowPosition: int) -> None:
        try:
            self.userAgent = b'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
            self.manager = QNetworkAccessManager()
            self.manager.finished.connect(self.on_finished)
            self.isbn = isbn
            self.url = url
            self.rowPosition = rowPosition
            print(f'Display Image -  {isbn} : {url}')
            self.getCheckImage()
        except Exception:
            import traceback
            print(traceback.format_exc())


    def on_finished(self) -> None:
        target = self.reply.attribute(QNetworkRequest.RedirectionTargetAttribute)
        if self.reply.error():
            print(f'error:: {self.reply.errorString()}')
            return
        elif target:
            newUrl = self.reply.url().resolved(target)
            self.getCheckImage()
            return

        try:
            with open('books_images/'+ self.isbn +'.jpg', 'wb') as handler:
                handler.write(self.reply.readAll())
            table = self.ui.fetchedBooks_tableWidget
            pixmap = QPixmap('books_images/' + self.isbn + '.jpg')
            pixmap = pixmap.scaled(100, 100, QtCore.Qt.KeepAspectRatio)
            if (not pixmap.isNull()):
                label = QtWidgets.QLabel()
                label.setPixmap(pixmap)
                table.setCellWidget(self.rowPosition,0, label)
            else:
                table.setItem(self.rowPosition, 0, QtWidgets.QTableWidgetItem('img_url'))
        except URLError as err:
                    print(str(err))

