from flask import Flask
from flask import render_template, request, redirect
#from flask_sqlalchemy import SQLAlchemy
import sqlite3
import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

DATABASE = "database.db"
db.create_bank()

error_text = ""#エラー時にerror.htmlで表示するテキスト

@app.route("/")
def index():
    return render_template("home.html")


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/ranking")
def ranking():
    con = sqlite3.connect(DATABASE)
    data = con.execute("select * from user_table").fetchall()
    con.close()

    ranking_list = []
    rank = 0
    for d in data:
        rank += 1
        ranking_list.append({"rank":rank,"name":d[0],"money":d[1]})

    return render_template("ranking.html",data=ranking_list)


@app.route("/withdrawal")
def withdrawal():
    return render_template("withdrawal.html")


@app.route("/deposit")
def deposit():
    return render_template("deposit.html")


@app.route("/create",methods=["GET","POST"])
def create():
    if request.method == "POST":
        name = request.form["name"]#送信されたnameを受け取る
        if name == "":#nameが空欄だったら
            print("==error==")
        else:
            con = sqlite3.connect(DATABASE)#データベースと接続
            list_name = con.execute("select name from user_table")
            name_match_flg = False#名前がダブった判定
            for n in list_name:#なぜかnはlistになってる
                if n[0] == name:
                    name_match_flg = True
                    error_text = "この名前は既に使われています"
                    return render_template("error.html",error_text=error_text)
            
            if not(name_match_flg):#名前がダブらなかったとき
                con.execute("insert into user_table values(?,?)",[name,1000])
                con.commit()
                a = con.execute("select * from user_table")
                for b in a:
                    print(b)
        
            print(name_match_flg)
            con.close()
    return render_template("create.html")


if __name__ == "__main__":
    app.run(debug=True)