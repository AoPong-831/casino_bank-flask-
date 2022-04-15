from flask import Flask
from flask import render_template, request, redirect
#from flask_sqlalchemy import SQLAlchemy
import sqlite3
import db

DATABASE = "database.db"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db.create_bank()

@app.route("/")
def index():
    return render_template("home.html")


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/ranking")
def ranking():
    return render_template("ranking.html")


@app.route("/withdrawal")
def withdrawal():
    return render_template("withdrawal.html")


@app.route("/deposit")
def deposit():
    return render_template("deposit.html")


@app.route("/create")
def create():
    return render_template("create.html")


if __name__ == "__main__":
    app.run(debug=True)