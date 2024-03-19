import sqlite3, datetime
class Database_Manager:
    @classmethod
    def __init__(cls, connection:sqlite3.Connection) -> None:
        cls.connection = connection
        cls.cursor = cls.connection.cursor()
        cls.cursor.execute( 'CREATE TABLE IF NOT EXISTS results (hash TEXT PRIMARY KEY, title TEXT, href TEXT, price TEXT, stamp DATETIME)' )

    def add_result(self, hash:str, title:str, href:str, price:str) -> None:
        dataset = (hash, title, href, price, datetime.datetime.now())
        self.cursor.execute('INSERT INTO results (hash, title, href, price, stamp) VALUES (?, ?, ?, ?, ?)', dataset)
        self.connection.commit()

    def select_all(self, table:str) -> list:
        self.cursor.execute( f'SELECT * FROM {table}' )
        return self.cursor.fetchall()
    
    def select_column(self, table:str, column:str, data:str) -> list:
        self.cursor.execute( f'SELECT {column} FROM {table} WHERE {column} = ?', (data,) )
        return self.cursor.fetchone()