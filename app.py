from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "123456"

PRECO_LITRO = 2.5


# ---------------- BANCO ----------------
def conectar():
    return sqlite3.connect("banco.db")


# cria tabelas automaticamente
def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS funcionarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        usuario TEXT,
        senha TEXT
    )
    """)

    conn.commit()
    conn.close()


criar_tabelas()


# ---------------- ROTA INICIAL ----------------
@app.route("/")
def home():
    return redirect("/login")


# ---------------- LOGIN (SIMPLES POR ENQUANTO) ----------------
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


# ---------------- CADASTRO ANIMAIS ----------------
@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")


# ---------------- RELATORIO ----------------
@app.route("/relatorio")
def relatorio():
    return render_template("relatorio.html")


# ---------------- FUNCIONARIOS ----------------
@app.route("/funcionarios", methods=["GET", "POST"])
def funcionarios():

    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        nome = request.form["nome"]
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        cursor.execute("""
        INSERT INTO funcionarios (nome, usuario, senha)
        VALUES (?, ?, ?)
        """, (nome, usuario, senha))

        conn.commit()

    cursor.execute("SELECT * FROM funcionarios")
    dados = cursor.fetchall()

    conn.close()

    return render_template("funcionarios.html", dados=dados)


# ---------------- PORTA (RENDER) ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)