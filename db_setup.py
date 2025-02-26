# create database in Sqlite3
import sqlite3
from sqlite3 import Error

def create_db_and_table(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
        c = conn.cursor()
        c.execute('''CREATE TABLE radio_names (name text UNIQUE)''')
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    create_db_and_table("radio_names.db")


