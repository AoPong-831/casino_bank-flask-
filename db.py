import sqlite3

DATABASE = "database.db"

def create_bank():
    con = sqlite3.connect(DATABASE)
    con.execute("CREATE TABLE IF NOT EXISTS user_table (name, money, debt, visits, date)")
    con.close()