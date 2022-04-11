from flask import Flask
from flask import render_template, request, redirect

app = Flask(__name__)

@app.route("/",methods=["GET","POST"])
def index():
    return render_template("index.html")

@app.route("/ranking")
def ranking():
    return render_template("ranking.html")
    

if __name__ == "__main__":
    app.run(debug=True)