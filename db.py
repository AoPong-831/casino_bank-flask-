import sqlite3

DATABASE = "database.db"

def create_bank():
    con = sqlite3.connect(DATABASE)
    con.execute("CREATE TABLE IF NOT EXISTS user_table (name, money, debt, visits, date)")
    con.close()

def create_all_ranking(DATABASE):
    con = sqlite3.connect(DATABASE)
    #名前,純資産,残高,返済額,借金
    con.execute("CREATE TABLE IF NOT EXISTS user_table (name, net_worth,money,repayment,debt)")
    con.close()