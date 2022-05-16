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


def search_data(name):#データ検索
    con = sqlite3.connect(DATABASE)
    data_list = con.execute("select * from user_table").fetchall()
    con.close()

    for data in data_list:
        if name == data[0]:#探している名前と一致
            request_data = data
            break
    
    return request_data


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
        ranking_list.append({"rank":rank,"name":d[0],"money":d[1],"debt":int(d[2]) * 1000})

    return render_template("ranking.html",data=ranking_list)


@app.route("/<string:name>/bank")
def bank(name):
    return render_template("bank.html",name=name)



@app.route("/<string:name>/withdrawal",methods=["GET","POST"])
def withdrawal(name):
    if request.method == "POST":
        entry = request.form["entry"]
        
        data = search_data(name)#データを検索

        cal_result = data[1] - int(entry)#引き出し処理(計算結果)

        #上書き処理
        con = sqlite3.connect(DATABASE)
        con.execute("update user_table set money = ? where name = ?",(cal_result,data[0]))
        con.commit()
        con.close()

        print("エラー？")
        return redirect("/ranking")
    else:
        return render_template("withdrawal.html")


@app.route("/<string:name>/deposit",methods=["GET","POST"])
def deposit(name):
    if request.method == "POST":
        entry = request.form["entry"]
        
        data = search_data(name)#データを検索

        cal_result = data[1] + int(entry)#預け入れ処理(計算結果)

        #上書き処理
        con = sqlite3.connect(DATABASE)
        con.execute("update user_table set money = ? where name = ?",(cal_result,data[0]))
        con.commit()
        con.close()

        print("エラー？")
        return redirect("/ranking")
    else:
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
                con.execute("insert into user_table values(?,?,?)",[name,1000,0])
                con.commit()
                a = con.execute("select * from user_table")
                return render_template("successed_create_account.html",name=name)

            con.close()
    else:
        return render_template("create.html")

@app.route("/debug",methods=["GET","POST"])
def debug():
    if request.method == "POST":
        cmd = int(request.form["cmd"])#送信されたcmdを受け取る

        if cmd == 1:#DBの中身をコンソールに表示
            con = sqlite3.connect(DATABASE)
            data_list = con.execute("select * from user_table").fetchall()
            print("="*10,"[DB]")
            for data in data_list:
                print(data)
            print("="*10)
            con.close()
        
        elif cmd == 2:#account_list.txtをDBにcopy
            con = sqlite3.connect(DATABASE)
            with open("info/account_list.txt","r",encoding="utf-8") as f:
                arrange = []#dataが入る配列
                for data in f:
                    name,chip,debt = data.split()#名前、チップ、債務
                    con.execute("insert into user_table values(?,?,?)",[name,chip,debt])
                    con.commit()
            con.close()

        return render_template("debug.html")
    else:
        return render_template("debug.html")


if __name__ == "__main__":
    app.run(debug=True)