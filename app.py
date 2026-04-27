from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "123456"

PRECO_LITRO = 2.5


# ---------------- BANCO ----------------
def conectar():
    return sqlite3.connect("banco.db")


# ---------------- ROTA INICIAL ----------------
@app.route("/")
def home():
    return redirect("/login")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect("/dashboard")
    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT data, litros FROM leite")
    dados = cursor.fetchall()

    total_leite = sum([d[1] for d in dados])
    lucro = total_leite * PRECO_LITRO

    return render_template(
        "dashboard.html",
        dados=dados,
        total_leite=total_leite,
        lucro=lucro
    )

@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")


@app.route("/relatorio")
def relatorio():
    return render_template("relatorio.html")

# ---------------- PORTA (RENDER) ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)