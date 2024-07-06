import ui_scraper as uiQT
import ui_book as uiBook
import ui_about as uiAbout
import ui_contacts as uiContacts

import db_utils as dbUtils

from scraper import ScraperManager
from image_handler import ImageLink, ImageDownload

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

# app = uiQT.QtWidgets.QApplication(sys.argv)
# MainWindow = uiQT.QtWidgets.QMainWindow()
# ui = uiQT.Ui_MainWindow()
# ui.setupUi(MainWindow)

app_book = uiBook.QtWidgets.QApplication(sys.argv)
BookWindow = uiBook.QtWidgets.QMainWindow()
ui_book = uiBook.Ui_book_Dialog()
ui_book.setupUi(BookWindow)

app_about = uiAbout.QtWidgets.QApplication(sys.argv)
AboutWindow = uiAbout.QtWidgets.QMainWindow()
ui_about = uiAbout.Ui_about_Dialog()
ui_about.setupUi(AboutWindow)

app_contacts = uiContacts.QtWidgets.QApplication(sys.argv)
ContactsWindow = uiContacts.QtWidgets.QMainWindow()
ui_contacts = uiContacts.Ui_contacts_Dialog()
ui_contacts.setupUi(ContactsWindow)

# to get only fetched books to save as csv 
list_inBooks_Fetched = []


def saveFetchedBookInfo(isbn, isbn_title, isbn_by, isbn_category, isbn_sub_category, isbn_description
                                                    , publisher,year_of_publication,book_language,num_pages, isbn_img_link):

    dbManager = dbUtils.DBManager()
    data_dect = {"isbn": isbn,
                "title": isbn_title,
                "author": isbn_by,
                "category": isbn_category,
                "sub_category": isbn_sub_category,
                "description": isbn_description,
                "publisher": publisher,
                "year_of_publication": year_of_publication,
                "language": book_language,
                "num_pages": num_pages,
                "img_link": isbn_img_link}
    dbManager.insert_data(table_name=dbManager._BOOKS, data_dect=data_dect)
    book = list(data_dect.values())
    # ui_set_book_data(book)
    ui_set_Fetchedbook_data(book)

def ui_set_book_data(book: list) -> None:
    table = ui.books_tableWidget
    rowPosition = table.rowCount()
    table.insertRow(rowPosition)
    table.setItem(rowPosition, 10, QtWidgets.QTableWidgetItem(book[0]))
    table.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(book[1]))
    table.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(book[2]))
    table.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(book[3]))
    table.setItem(rowPosition, 4, QtWidgets.QTableWidgetItem(book[4]))
    table.setItem(rowPosition, 5, QtWidgets.QTableWidgetItem(book[5]))
    table.setItem(rowPosition, 6, QtWidgets.QTableWidgetItem(book[6]))
    table.setItem(rowPosition, 7, QtWidgets.QTableWidgetItem(str(book[7])))
    table.setItem(rowPosition, 8, QtWidgets.QTableWidgetItem(book[8]))
    table.setItem(rowPosition, 9, QtWidgets.QTableWidgetItem(str(book[9])))
    # table.setItem(rowPosition, 10, QtWidgets.QTableWidgetItem(str(book[10])))     # image link
    isbn=book[0]
    img_url=str(book[10])
    if not os.path.exists('books_images/' +isbn+'.jpg'):
            print("Downloading image: "+ isbn)
            item_imageDownload.download_image_signal.emit(isbn, img_url, rowPosition)
    else:
        item_image.dataChanged_image.emit(rowPosition ,isbn, img_url)


def ui_set_Fetchedbook_data(book: list) -> None:
    table = ui.fetchedBooks_tableWidget
    rowPosition = table.rowCount()
    table.insertRow(rowPosition)
    table.setItem(rowPosition, 10, QtWidgets.QTableWidgetItem(book[0]))
    table.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(book[1]))
    table.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(book[2]))
    table.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(book[3]))
    table.setItem(rowPosition, 4, QtWidgets.QTableWidgetItem(book[4]))
    table.setItem(rowPosition, 5, QtWidgets.QTableWidgetItem(book[5]))
    table.setItem(rowPosition, 6, QtWidgets.QTableWidgetItem(book[6]))
    table.setItem(rowPosition, 7, QtWidgets.QTableWidgetItem(str(book[7])))
    table.setItem(rowPosition, 8, QtWidgets.QTableWidgetItem(book[8]))
    table.setItem(rowPosition, 9, QtWidgets.QTableWidgetItem(str(book[9])))
    # table.setItem(rowPosition, 10, QtWidgets.QTableWidgetItem(str(book[10])))     # image link
    isbn=book[0]
    img_url=str(book[10])
    if not os.path.exists('books_images/' +isbn+'.jpg'):
        print("Downloading image: "+ isbn)
        item_imageDownload.download_image_signal.emit(isbn, img_url, rowPosition)
    else:
        item_image.fetched_image_signal.emit(rowPosition ,isbn, img_url)

    #set Books and Fetched Counts
    ui.fetchedCount_label.setText(str(rowPosition+1))
    table.scrollToBottom()

def ui_set_ISBNs_data(isbn_to_fetch: list) -> None:
    table = ui.isbns_tableWidget
    rowPosition = table.rowCount()
    table.insertRow(rowPosition)
    table.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(str(isbn_to_fetch[0])))

def ui_set_errors_data(fetch_error: list) -> None:
    table = ui.errorsFetch_tableWidget
    rowPosition = table.rowCount()
    table.insertRow(rowPosition)
    table.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(fetch_error[0]))
    table.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(fetch_error[1]))

def ui_get_all_books() -> None:
    dbManager = dbUtils.DBManager()
    all_book_data = dbManager.get_data(dbManager._BOOKS)
    ui.booksCount_label.setText(str(len(all_book_data)))
    ui.books_tableWidget.setRowCount(0)
    # Set Data From SQLite To Table
    for book in all_book_data:
        ui_set_book_data(book)

def ui_get_all_ISBNs() -> None:
    dbManager = dbUtils.DBManager()
    all_ISBNs_ids = dbManager.get_data(dbManager._ISBNS_TO_FETCH)
    # Clear Tab Table Content
    ui.isbns_tableWidget.setRowCount(0)
    # Set Data From SQLite To Table
    for isbn_id in all_ISBNs_ids:
        ui_set_ISBNs_data(isbn_id)

def ui_get_all_errors() -> None:
    dbManager = dbUtils.DBManager()
    all_errors = dbManager.get_data(dbManager._FETCH_ERROR)
    ui.errorsCount_label.setText(str(len(all_errors)))
    # Clear Tab Table Content
    table = ui.errorsFetch_tableWidget
    table.setRowCount(0)
    # Set Data From SQLite To Table
    for error_data in all_errors:
        ui_set_errors_data(error_data)

def scraper_function(isbn: str, mode_api: bool) -> bool:

    try:
        # Get Book info from Amazon (RapidAPI) or OpenLibrary (directly)
        fetched_info = ScraperManager(product_id=isbn, fetching_mode=mode_api).scrape()
        
        isbn = fetched_info[0]
        isbn_title = fetched_info[1]
        isbn_by = fetched_info[2]
        isbn_category = fetched_info[3]
        isbn_sub_category = fetched_info[4]
        isbn_description = fetched_info[5]
        publisher = fetched_info[6]
        year_of_publication = fetched_info[7]
        book_language = fetched_info[8]
        num_pages = fetched_info[9]
        isbn_img_link = fetched_info[10]

        saveFetchedBookInfo(isbn, isbn_title, isbn_by, isbn_category, isbn_sub_category, isbn_description
                                                    , publisher,year_of_publication,book_language,num_pages, isbn_img_link)
        list_inBooks_Fetched.append(isbn)
        return True

    except (AttributeError, KeyError) as error:
        dbManager = dbUtils.DBManager()
        data_dect = {"isbn":isbn, "error":"404 Not Found! Log: "+str(error)}
        dbManager.insert_data(dbManager._FETCH_ERROR, data_dect)
        ui.console_textEdit.append('error: not found')
        ui.console_textEdit.moveCursor(QtGui.QTextCursor.End)
        return True
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        item_show_message.show_message.emit("Internet Error","Check Internet Connection. \n\nLog:\n"+str(e))
        return False

def getISBN_info() -> None:
    ui.progressBar.show()
    # 1. get list of all isbns 
    dbManager = dbUtils.DBManager()
    isbns_list = dbManager.get_data(dbManager._ISBNS_TO_FETCH)
    # 2. get list length for progressbabr
    isbns_count = len(isbns_list)
    if isbns_count == 0:
        progressBarFinish()
        
        item_show_message.show_message.emit("Information","No ISBNs stored in database to fetch! \nPlease add new ISBNs to fetch.")
        return
    print(f'{isbns_count}  {isbns_list}')
    counter_progress = 0
    mode_api = ui.fetch_mode_Toggle.isChecked()
    # 3. fetch each on of them 
    for isbn_id in isbns_list:
        isbn = isbn_id[0]
        print(f'------------\n{isbn} fetching')
        ui.console_textEdit.append( '--------------------------\nget: ' + str(isbn))
        ui.console_textEdit.moveCursor(QtGui.QTextCursor.End)

        counter_progress += 1
        if not scraper_function(isbn, mode_api):
            break
        # 4. on success, delete from isbn to fetch 
        dbManager.delete_data(dbManager._ISBNS_TO_FETCH, isbn)
        item_progressbar.dataChanged.emit(int((counter_progress/isbns_count)*100))
    
    time.sleep(1) # Used to wait for downloading last book image
    item_show_message.show_message.emit("Message","Fetch Operation Done !")
    progressBarFinish()
    ui_get_all_errors()
    ui_get_all_books()
    ui.console_textEdit.append( '............\nFetching Ended\n--------------------------')
    ui.console_textEdit.moveCursor(QtGui.QTextCursor.End)
    ui_get_all_ISBNs()


def onCountChanged(value: int) -> None:
    ui.progressBar.setValue(value)

def progressBarFinish() -> None:
    ui.progressBar.hide()
    onCountChanged(0)

def start_update() -> None:
    threading.Thread(target=getISBN_info, daemon=True).start()

def parseCSV(filePath: str) -> None:
    # CVS Column Names
    col_names = ['isbn']
    # Use Pandas to parse the CSV file
    csvData = pd.read_csv(filePath,names=col_names, header=None, converters={'isbn': lambda x: str(x)})
    # csvData["isbn"] = csvData["isbn"].astype(str)
    dbManager = dbUtils.DBManager()
    # Loop through the Rows
    list_inBooks_Fetched.clear()
    for i,row in csvData.iterrows():
        if not dbManager.isInDataBase(dbManager._FETCH_ERROR ,row['isbn']):
            if not dbManager.isInDataBase(dbManager._BOOKS ,row['isbn']):
                dbManager.insert_data(dbManager._ISBNS_TO_FETCH, {'isbn':row['isbn']})
            else:
                list_inBooks_Fetched.append(row['isbn'])
    ui.inBooksCount_label.setText(str(len(list_inBooks_Fetched)))
    ui_get_all_ISBNs()

def open_file() -> None:
    path = QFileDialog.getOpenFileName(MainWindow, "Open",filter="CSV Files (*.csv)")[0]
    if path:
        newWorkplace()
        ui.csvFilePath_lineEdit.setText(path) 
        parseCSV(path)

def save_books_CSV() -> None:
    dbManager = dbUtils.DBManager()
    data = dbManager.get_data(dbManager._BOOKS)
    path = QFileDialog.getSaveFileName(MainWindow, 'Save File', "saved_books.csv","CSV Files (*.csv);;All Files (*)")[0]
    if path:
        cols = ['isbn', 'title', 'author', 'category', 'sub_category', 'description'
                                                        , 'publisher','year_of_publication','language','num_pages','img_link']
        df = pd.DataFrame(data=data, columns=cols)
        df.to_csv(path, index=False)

def save_logsError_CSV() -> None:
    dbManager = dbUtils.DBManager()
    data = dbManager.get_data(dbManager._FETCH_ERROR)
    path = QFileDialog.getSaveFileName(MainWindow, 'Save File', "saved_errors_Log.csv","CSV Files (*.csv);;All Files (*)")[0]
    if path:
        cols = ['isbn', 'error']
        df = pd.DataFrame(data=data, columns=cols)
        df.to_csv(path, index=False)

def save_fetchedBooks_CSV() -> None:
    dbManager = dbUtils.DBManager()
    data = dbManager.get_data_FetchedBooks(list_inBooks_Fetched)
    path = QFileDialog.getSaveFileName(MainWindow, 'Save File', "fetched_books.csv","CSV Files (*.csv);;All Files (*)")[0]
    if path:
        cols = ['isbn', 'title', 'author', 'category', 'sub_category', 'description'
                                                        , 'publisher','year_of_publication','language','num_pages','img_link']
        df = pd.DataFrame(data=data, columns=cols)
        df.to_csv(path, index=False)
        
def clearErrorsTable(id_isbn: str) -> None:
    dbManager =dbUtils.DBManager()
    # clear all fetch erros from DB using (id_isbn = %)
    dbManager.delete_data(dbManager._FETCH_ERROR, id_isbn)  
    ui_get_all_errors()

def clearISBNsToFetchTable(id_isbn: str) -> None:
    dbManager =dbUtils.DBManager()
    # clear all fetch erros from DB using (id_isbn = %)
    dbManager.delete_data(dbManager._ISBNS_TO_FETCH, id_isbn)  
    ui_get_all_ISBNs()

def newWorkplace() -> None:
    ui.inBooksCount_label.setText('0')
    ui.errorsCount_label.setText('0')
    ui.fetchedCount_label.setText('0')
    ui.csvFilePath_lineEdit.clear()
    ui.console_textEdit.setText('     <Get or Error>')
    ui.isbns_tableWidget.setRowCount(0)
    ui.fetchedBooks_tableWidget.setRowCount(0)
    clearISBNsToFetchTable('%')
    clearErrorsTable('%')

# Open Web Browser -----
def openAmazonWebpage() -> None:
    isbn = ui_book.isbn_label.text()
    print(isbn)
    webbrowser.open_new_tab('https://www.amazon.com/dp/'+isbn)

def openGoogleWebpage(error_log) -> None:
    error_search = error_log.replace(' ','+')
    webbrowser.open_new_tab('https://www.google.com/search?q='+ error_search)

def openContactWebpage(contact_link) -> None:
    webbrowser.open_new_tab(contact_link)

# ---------------------------------------
class ProgressbarChanger(QObject):
    data_changed = pyqtSignal(int, name="dataChanged")

    def onDataChanged(self,value: int) -> None:
        ui.progressBar.setValue(value)

item_progressbar = ProgressbarChanger()

# ----------------------------------------
class MessageBoxSignal(QObject):
    # This class initiate image cell in Books table
    data_changed_image = pyqtSignal(str, str, name="show_message")

    def onDataChanged(self,title: str, text:str) -> None:
        msg = QMessageBox()
        msg.setWindowIcon(QIcon('files/app_icon.jpg'))
        msg.setIcon(QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.Ok)
        # start the app
        retval = msg.exec_()

item_show_message = MessageBoxSignal()


# -------------------------------------------
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

# ---------------- ContextMenus -----------------------

def errorsFetch_ContextMenu(position: int) -> None:
    menu = QMenu()
    delete_action = menu.addAction(QIcon('files/menuContext_icons/trash.png'), "Delete")
    search_action = menu.addAction(QIcon('files/menuContext_icons/google.png'),"Search In Google")
    action = menu.exec_(ui.errorsFetch_tableWidget.mapToGlobal(position))
    # Actions tasks
    errors_table = ui.errorsFetch_tableWidget
    row = errors_table.currentRow()
    if action == search_action:
        error_log = errors_table.item(row, 1).text()
        openGoogleWebpage(error_log)
    elif action == delete_action:
        if row != -1:
            isbn = errors_table.item(row, 0).text()
            clearErrorsTable(isbn)
            ui_get_all_errors()

def books_ContextMenu(position: int) -> None:
    menu = QMenu()
    bookPreview_action = menu.addAction(QIcon('files/menuContext_icons/books.png'), "Preview Book Details")
    opebWeb_action = menu.addAction(QIcon('files/menuContext_icons/amz.png'),"Open In Amazon.com")
    action = menu.exec_(ui.books_tableWidget.mapToGlobal(position))
    # Actions tasks
    book_table = ui.books_tableWidget
    row = book_table.currentRow()
    if row == -1:
        return
    if action == opebWeb_action:
        isbn = book_table.item(row, 10).text()
        webbrowser.open_new_tab('https://www.amazon.com/dp/'+isbn)
    elif action == bookPreview_action:
        showBookInfo(book_table)

def fetchedBooks_ContextMenu(position: int) -> None:
    menu = QMenu()
    bookPreview_action = menu.addAction(QIcon('files/menuContext_icons/books.png'), "Preview Book Details")
    opebWeb_action = menu.addAction(QIcon('files/menuContext_icons/amz.png'),"Open In Amazon.com")
    action = menu.exec_(ui.fetchedBooks_tableWidget.mapToGlobal(position))
    # Actions tasks
    book_table = ui.fetchedBooks_tableWidget
    row = book_table.currentRow()
    if row == -1:
        return
    if action == opebWeb_action:
        isbn = book_table.item(row, 10).text()
        webbrowser.open_new_tab('https://www.amazon.com/dp/'+isbn)
    elif action == bookPreview_action:
        showBookInfo(book_table)

# ---------------------------------------
def viewTab(qWidget_tab) -> None:
    ui.main_tabWidget.setCurrentWidget(qWidget_tab)

def init_MainWindow() -> None:
    # Set Fixed Windows sizes
    MainWindow.setFixedSize(1015, 728)        
    BookWindow.setFixedSize(830, 620)   
    AboutWindow.setFixedSize(490, 720)   
    ContactsWindow.setFixedSize(458, 498) 

    # Push Buttons click funtions   
    ui.fetchInfo_pushButton.clicked.connect(lambda: start_update())
    ui.saveCSV_pushButton.clicked.connect(lambda: save_books_CSV()) 
    ui.saveFetched_pushButton.clicked.connect(lambda: save_fetchedBooks_CSV()) 
    ui.saveLogsErrors_pushButton.clicked.connect(lambda: save_logsError_CSV()) 
    ui.openFile_pushButton.clicked.connect(open_file) 
    ui.clearErrors_pushButton.clicked.connect(lambda: clearErrorsTable('%'))
    ui.plot_pushButton.clicked.connect(showPlot) 
    progressBarFinish()

    # Menu actions
    ui.actionOpen.triggered.connect(open_file)
    ui.actionExit.triggered.connect(MainWindow.close)
    ui.actionISBNs_to_fetch.triggered.connect(lambda: viewTab(ui.isbnsFetch_tab))
    ui.actionFetch_Errors.triggered.connect(lambda: viewTab(ui.fetchErros_tab))
    ui.actionAll_Books.triggered.connect(lambda: viewTab(ui.allBooks_tab))
    ui.actionSave_AllBooks.triggered.connect(lambda: save_books_CSV())
    ui.actionSave_FetchedBooks.triggered.connect(lambda: save_fetchedBooks_CSV())
    ui.actionNew.triggered.connect(lambda:  newWorkplace())
    ui.actionAbout_App.triggered.connect(lambda: openDialog(AboutWindow))
    ui.actionContacts.triggered.connect(lambda: openDialog(ContactsWindow))

    # Prepare Singals and Threads
    item_progressbar.dataChanged.connect(item_progressbar.onDataChanged)
    item_image.dataChanged_image.connect(item_image.onDataChanged)
    item_image.fetched_image_signal.connect(item_image.onFetchedBookImage)
    item_show_message.show_message.connect(item_show_message.onDataChanged) 
    item_imageDownload.download_image_signal.connect(item_imageDownload.display)
  
    # Books table config
    ui.books_tableWidget.verticalHeader().sectionDoubleClicked.connect(lambda: showBookInfo(ui.books_tableWidget))
    ui.books_tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
    ui.books_tableWidget.customContextMenuRequested.connect(books_ContextMenu)

    # Fetched Books table config
    ui.fetchedBooks_tableWidget.verticalHeader().sectionDoubleClicked.connect(lambda: showBookInfo(ui.fetchedBooks_tableWidget))
    ui.fetchedBooks_tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
    ui.fetchedBooks_tableWidget.customContextMenuRequested.connect(fetchedBooks_ContextMenu)
    
    # Fetch errors table config
    ui.errorsFetch_tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
    ui.errorsFetch_tableWidget.customContextMenuRequested.connect(errorsFetch_ContextMenu)
    
    # Get all data to their Tables
    ui_get_all_books()
    ui_get_all_ISBNs()
    ui_get_all_errors()


def openDialog(widget_dialog: QMainWindow) -> None:
    ph = MainWindow.geometry().height()
    pw = MainWindow.geometry().width()
    px = MainWindow.pos().x()
    py = MainWindow.pos().y()
    dw = widget_dialog.width()
    dh = widget_dialog.height()   
    widget_dialog.setGeometry(int((pw-dw)/2) + px, int((ph-dh)/2) + py, dw, dh )
    widget_dialog.setWindowModality(Qt.ApplicationModal)
    widget_dialog.show()

def showPlot() -> None:
    dbManager = dbUtils.DBManager()
    data = dbManager.get_data(dbManager._BOOKS)
    cols = ['isbn', 'title', 'author', 'category', 'sub_category', 'description'
                                                        , 'publisher','year_of_publication','language','num_pages','img_link']
    df = pd.DataFrame(data=data, columns=cols)
    df_groupedBy_year = df.groupby(by='year_of_publication').count()['isbn']
    fig = plt.figure(figsize = (10, 5))
    plt.bar(df_groupedBy_year.index , df_groupedBy_year.array, width = 0.7)
    plt.xlabel("Book Publication Year")
    plt.ylabel("No. of Books")
    plt.title("Number of Books Published Per Year")
    plt.tight_layout()
    plt.show()


def init_BookWindow() -> None:
    ui_book.pushButton.clicked.connect(BookWindow.close)
    ui_book.webPage_pushButton.clicked.connect(openAmazonWebpage)

def init_AboutWindow() -> None:
    AboutWindow.setWindowFlags(Qt.FramelessWindowHint)
    AboutWindow.setAttribute(Qt.WA_TranslucentBackground)
    # creating a QGraphicsDropShadowEffect object
    shadow = QtWidgets.QGraphicsDropShadowEffect()
    shadow.setOffset(5, 5)
    shadow.setBlurRadius(30)
    ui_about.widget.setGraphicsEffect(shadow)

def init_ContactsWindow() -> None: 
    ContactsWindow.setWindowFlags(Qt.FramelessWindowHint)
    ContactsWindow.setAttribute(Qt.WA_TranslucentBackground)
    ui_contacts.contactLinkedin_pushButton.clicked.connect(lambda: openContactWebpage(ui_contacts.contactLinkedin_pushButton.text().strip()))
    ui_contacts.contactResearchgate_pushButton.clicked.connect(lambda: openContactWebpage(ui_contacts.contactResearchgate_pushButton.text().strip()))
    ui_contacts.contactKaggle_pushButton.clicked.connect(lambda: openContactWebpage(ui_contacts.contactKaggle_pushButton.text().strip()))
    ui_contacts.contactTwitter_pushButton.clicked.connect(lambda: openContactWebpage(ui_contacts.contactTwitter_pushButton.text().strip()))
    # creating a QGraphicsDropShadowEffect object
    shadow = QtWidgets.QGraphicsDropShadowEffect()
    shadow.setOffset(5, 5)
    shadow.setBlurRadius(30)
    ui_contacts.widget.setGraphicsEffect(shadow)

def showBookInfo(caller_widget: QtWidgets.QTableWidget) -> None:
    # Show Dialog of all book info
    row = caller_widget.currentRow()

    isbn = caller_widget.item(row, 10).text()
    title = caller_widget.item(row, 1).text()
    author = caller_widget.item(row, 2).text()
    category = caller_widget.item(row, 3).text()
    sub_category = caller_widget.item(row, 4).text()
    description = caller_widget.item(row, 5).text()
    publisher = caller_widget.item(row, 6).text()
    year_of_publication = caller_widget.item(row, 7).text()
    language = caller_widget.item(row, 8).text()
    num_pages = caller_widget.item(row, 9).text()    

    ui_book.isbn_label.setText(isbn)
    ui_book.title_label.setText(title)
    ui_book.byAuthor_label.setText("By "+ author+" (Author)")
    ui_book.category_label.setText(category)
    ui_book.subCategory_label.setText(sub_category)
    ui_book.description_textEdit.setText(description)
    ui_book.publisher_label.setText(publisher)
    ui_book.yearPub_label.setText(year_of_publication)
    ui_book.language_label.setText(language)
    ui_book.numPages_label.setText(num_pages)

    pixmap = QPixmap('books_images/'+ isbn +'.jpg')
    if (not pixmap.isNull()):
        pixmap = pixmap.scaled(240, 240, QtCore.Qt.KeepAspectRatio)
        ui_book.imageBook_label.setPixmap(pixmap)
    else:
        ui_book.imageBook_label.setText('Not available at the moment.')

    BookWindow.show()


# Tasks to do
# - 

# -------------------------

# init_MainWindow()
init_BookWindow()
init_AboutWindow()
init_ContactsWindow()

class MainWindowApp(QMainWindow):
    def closeEvent(self,event):
        result = QMessageBox.question(self, "Confirm Exit...",
                        "Are you sure you want to exit ?",
                        QMessageBox.Yes| QMessageBox.No)
        event.ignore()
        if result == QMessageBox.Yes:
            event.accept()

if __name__ == "__main__":
    import sys
    app = uiQT.QtWidgets.QApplication(sys.argv)
    MainWindow = MainWindowApp()
    ui = uiQT.Ui_MainWindow()
    ui.setupUi(MainWindow)

    # Calling Signals
    item_imageDownload = ImageDownload(ui)
    item_image = ImageLink(ui)

    # Initial GUI after adding closeEvent to the MainWindow class
    init_MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())

# if __name__ == '__main__':
#     MainWindow.show()
#     sys.exit(app.exec_())