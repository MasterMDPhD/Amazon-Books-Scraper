import sqlite3
from sqlite3 import Error

class DBManager():
    # Tables name
    _BOOKS = 'books'
    _FETCH_ERROR = 'fetch_error'
    _ISBNS_TO_FETCH = 'isbns_to_fetch'

    def __init__(self):
        self.db_file = "db_books_sqlite.db"
        self.create_tables()

    def get_connection(self):
        try:
            return sqlite3.connect(self.db_file)
        except Error as e:
            print(e)
       

    def create_tables(self):
        conn = self.get_connection()
        cur = conn.cursor()

        table_books = 'CREATE TABLE IF NOT EXISTS '+ self._BOOKS +' (                         \
                                "isbn"	TEXT,                       \
                                "title"	TEXT,                       \
                                "author"	TEXT,                   \
                                "category"	TEXT,                   \
                                "sub_category"	TEXT,               \
                                "description"	TEXT,               \
                                "publisher"	TEXT,                   \
                                "year_of_publication"	INTEGER,    \
                                "language"	TEXT,                   \
                                "num_pages"	INTEGER,                \
                                "img_link"	TEXT,                   \
                                PRIMARY KEY("isbn")                 \
                            );'
        table_isbns_to_fetch = 'CREATE TABLE IF NOT EXISTS '+ self._ISBNS_TO_FETCH +' (                         \
                                "isbn"	TEXT,                       \
                                PRIMARY KEY("isbn")                 \
                            );'
        table_fetch_errors = 'CREATE TABLE IF NOT EXISTS '+ self._FETCH_ERROR +' (                         \
                                "isbn"	TEXT,                       \
                                "error"	TEXT,                       \
                                PRIMARY KEY("isbn")                 \
                            );'


        cur.execute(table_books)
        conn.commit()

        cur.execute(table_isbns_to_fetch)
        conn.commit()

        cur.execute(table_fetch_errors)
        conn.commit()

        conn.close()

    def insert_data(self, table_name, data_dect ):
        print("insert data ..." + table_name)
        
        if table_name == self._BOOKS:
            table_cols = "(?,?,?,?,?,?,?,?,?,?,?)"
        elif table_name == self._FETCH_ERROR:
            table_cols = "(?,?)"
        elif table_name == self._ISBNS_TO_FETCH:
            table_cols = "(?)"
        
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('INSERT OR IGNORE INTO '+table_name+ ' VALUES ' + table_cols, list(data_dect.values()))
        conn.commit()
        conn.close()

    def delete_data(self, table_name, id_isbn):
        print("delete data ..."+ table_name)
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM '+table_name+ ' WHERE isbn like "'+ id_isbn +'"')
        conn.commit()
        conn.close()
    
    def get_data(self, table_name):
        print("get rows ..." + table_name)
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM ' + table_name)
        data = cur.fetchall()
        # print(data)
        return data
    
    def get_data_FetchedBooks(self, list_inBooks_Fetched):
        print("get rows ..." + self._BOOKS)
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM " +  self._BOOKS + " WHERE isbn IN "+ str(list_inBooks_Fetched).replace('[','(').replace(']',')'))
        data = cur.fetchall()
        # print(data)
        return data

    def isInDataBase(self, table_name, id_isbn):
        print("Check " + table_name + " ... "+ id_isbn)
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM ' + table_name + ' WHERE isbn = "'+ id_isbn +'"')
        data = cur.fetchall()
        return len(data)


"""    


data_dect = {"isbn": "X01065MO9X",
                "title":"aaa",
                "author":"master",
                "category":"app",
                "sub_category":"py",
                "description":"this app ...",
                "publisher":"baath",
                "year_of_publication":"2022",
                "language":"en",
                "num_pages":"632",}

                "https://images-na.ssl-images-amazon.com/images/I/51bD+RXQtdL._SY344_BO1,204,203,200_.jpg",
                "https://images-na.ssl-images-amazon.com/images/I/41AflTLUTGL._SY291_BO1,204,203,200_QL40_FMwebp_.jpg",
                "https://images-na.ssl-images-amazon.com/images/I/5197SGZ9KNL._SY291_BO1,204,203,200_QL40_FMwebp_.jpg",


dbManager = DBManager()

dbManager.insert_data(table_name="books", data_dect=data_dect)
dbManager.delete_data(table_name="books", id_isbn="X00065MO9X")

dbManager.get_data(table_name="books")
"""