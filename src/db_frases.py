import sqlite3
from sqlite3 import Error


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"connect The error '{e}' occurred")

    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"execute The error '{e}' occurred")


def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"read The error '{e}' occurred")




def create_table():
    q = """
    CREATE TABLE IF NOT EXISTS frases (
        frase_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        eng_frase TEXT NOT NULL,
        rus_frase TEXT NOT NULL
        );
    """
    return q

def rows_rows():
    q = """
    SELECT COUNT(*) from frases
    """
    return q




def output_frase(number):
    q = """
    SELECT eng_frase,rus_frase from frases
    WHERE frase_id=""" + str(number)
    return q

def get_all_frases():
    q = """
    SELECT frase_id,eng_frase,rus_frase from frases
    """
    return q

def delete_value(num):
    q = "DELETE FROM frases WHERE frase_id = " + str(num)
    return q

def add_value(eng_frase, rus_frase):
    add_card = """
INSERT INTO frases (eng_frase, rus_frase)
VALUES ('""" + eng_frase + "', '" + rus_frase + "');"
    return add_card


# id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
# eng_frase TEXT NOT NULL,
# rus_text TEXT NOT NULL,