from flask import Flask,render_template, request, redirect,Response,make_response

import sqlite3
import db
import os#ファイル削除用

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'#いらんくね？

DATABASE = "database.db"
db.create_bank()


def search_data(name):#データ検索
    con = sqlite3.connect(DATABASE)
    data = con.execute("select * from user_table where name=?",[name]).fetchall()
    con.close()
    """
    for data in data_list:
        if name == data[0]:#探している名前と一致
            request_data = data
            break
    """
    return list(data[0])


def Overwrite(data):#上書き処理
    #DB
    con = sqlite3.connect(DATABASE)
    con.execute("update user_table set money = ?,debt = ? where name = ?",(data[1],data[2],data[0]))
    con.commit()
    con.close()
    #account_list.txt
    with open("info/account_list.txt","r",encoding="utf-8") as f:#読み込み
        arrange = []
        print("="*100)
        for txt in f:
            print(txt)
            name,chip,debit = txt.split()#名前、チップ、債務
            arrange.append([name,chip,debit])#.txt内容をarrangeに代入
        for i in arrange:#chipに変更を加える。
            if i[0] == data[0]:#名前が一致したら、変更を加える
                i[1] = data[1]
                i[2] = data[2]
    with open("info/account_list.txt","w",encoding="utf-8") as f:#書き込み
        for i in arrange:
            f.write("{0} {1} {2}\n".format(i[0],i[1],i[2]))
    #log.txt
    with open("info/log/" + data[0] + ".txt","a",encoding="utf-8")as f:#Log書き込み
        f.write(str(data[1]) + "\n")


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/ranking")
def ranking():
    con = sqlite3.connect(DATABASE)
    data = con.execute("select * from user_table order by money desc").fetchall()
    con.close()

    rank = 1#順位
    ranking_list = []
    for d in data:
        ranking_list.append([rank,d[0],d[1],d[2]*1000])#順位、名前、残高、借金
        rank += 1
    return render_template("ranking.html",data = ranking_list)


@app.route("/<string:name>/bank")
def bank(name):
    return render_template("bank.html",name=name)


@app.route("/<string:name>/bank/withdrawal",methods=["GET","POST"])
def withdrawal(name):
    if request.method == "POST":
        entry = request.form["entry"]

        data = search_data(name)#データを検索
        data[1] -= int(entry)

        if data[1] < 0:#moneyがマイナス
            return render_template("error.html",text="引き出し額が残高を上回っています。")
        else:
            Overwrite(data)#引き出し処理(計算結果)

        return redirect("/ranking")
    else:
        data = search_data(name)#データを検索
        money=data[1]
        debt =data[2]
        return render_template("withdrawal.html",name=name,money=money,debt=debt)

@app.route("/<string:name>/bank/acomn",methods=["GET","POST"])
def acomn(name):
    data = search_data(name)#データを検索
    return render_template("acomn.html",name=name,debt=data[2]*1000)

@app.route("/<string:name>/bank/acomn/repayment",methods=["GET","POST"])
def acomn_repayment(name):
    entry = 0#返済回数が0として置いておく。
    if request.method == "POST":
        entry = request.form.get("entry")#返済回数を取得
        if entry=="":#返済回数が空白の時、0にする
            entry = 0
        button = request.form["send"]#どのボタンが押されたのか取得
        if button == "見積もる":
            data = search_data(name)#データを検索
            #return render_template("acomn_repayment.html",name=name,money=debt[1],debt=data[2],pay_back=int(entry))
        elif button == "確定":
            data = search_data(name)#データを検索
            repayment = int(entry) * 1500#返済予定額を作成
            if int(entry) > data[2] or entry == 0:#返済回数が不正の場合
                return render_template("error.html",text="返済回数を確認してください。")
            elif (data[1] - repayment) >= 0 and int(entry) <= data[2]:#返済できる場合
                data[1] = data[1] - repayment
                data[2] = data[2] - int(entry)
                Overwrite(data)#預け入れ処理(計算結果)
                return render_template("successed_repayment.html",name=name,debt=data[2])
            elif (data[1] - repayment) < 0:#残高が足りず返済できない場合
                return render_template("error.html",text="残高が不足しています。")
            else:#予期せぬ例外
                return render_template("error.html",text="アコム,返済中,エラー")
    else:
        data = search_data(name)#データを検索
        #return render_template("acomn_repayment.html",name=name,money=debt[1],debt=data[2],pay_back=0)
    return render_template("acomn_repayment.html",name=name,money=data[1],debt=data[2],pay_back=int(entry))

@app.route("/<string:name>/bank/acomn/loan")
def acomn_loan(name):
    is_flg=True#Trueの時、融資される。
    data = search_data(name)#データを検索
    if not(data[1] == 0):#残高が0出ない場合、flgがFalseになり、融資されない。
        is_flg=False
    else:
        data[1] += 1000
        data[2] += 1
        Overwrite(data)#預け入れ処理(計算結果)
    return render_template("acomn_loan.html",name=name,is_flg=is_flg)

@app.route("/<string:name>/bank/deposit",methods=["GET","POST"])
def deposit(name):
    if request.method == "POST":
        entry = request.form["entry"]

        data = search_data(name)#データを検索
        data[1] += int(entry)
        Overwrite(data)#預け入れ処理(計算結果)

        return redirect("/ranking")
    else:
        data = search_data(name)#データを検索
        money=data[1]
        debt=data[2]
        return render_template("deposit.html",name=name,money=money,debt=debt)


@app.route("/create",methods=["GET","POST"])
def create():
    if request.method == "POST":
        name = request.form.get("name")#送信されたnameを受け取る
        if name == "":#nameが空欄だったら(上を.get()にすることで、空白はNoneになるはずが""で入っちゃってる)
            return render_template("error.html",text="名前が空白です。")
        else:
            con = sqlite3.connect(DATABASE)#データベースと接続
            list_name = con.execute("select name from user_table")
            name_match_flg = False#名前がダブった判定
            for n in list_name:#なぜかnはlistになってる
                if n[0] == name:
                    name_match_flg = True
                    return render_template("error.html",text="この名前は既に使われています")
            
            if not(name_match_flg):#名前がダブらなかったとき
                con.execute("insert into user_table values(?,?,?)",[name,1000,0])
                con.commit()
                a = con.execute("select * from user_table")
                
                with open("info/account_list.txt","a",encoding="utf-8") as f:#account_listに追加
                    f.write("{0} {1} {2}\n".format(name,1000,0))
                    print("="*100)
                with open("info/log/" + name + ".txt","a",encoding="utf-8")as f:#Log追加
                    f.write("1000\n")
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
        
        elif cmd == 2:
        #database.dbを削除してaccount_list.txtをDBにcopy
            os.remove("database.db")
            db.create_bank()
            con = sqlite3.connect(DATABASE)
            with open("info/account_list.txt","r",encoding="utf-8") as f:
                arrange = []#dataが入る配列
                for data in f:
                    name,chip,debt = data.split()#名前、チップ、債務
                    con.execute("insert into user_table values(?,?,?)",[name,int(chip),int(debt)])
                    con.commit()
            con.close()
        
        elif cmd == 4:#infoをダウンロード(バグだらけ)
            response = make_response()
            response.data  = open('info', "rb").read()
            response.headers['Content-Type'] = 'application/octet-stream'
            response.headers['Content-Disposition'] = 'attachment; filename=info'
            return response
    else:
        return render_template("debug.html")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=False)