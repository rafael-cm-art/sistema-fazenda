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
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        # 🔐 ADMIN FIXO
        if usuario == "admin" and senha == "123":
            session["usuario"] = usuario
            return redirect("/dashboard")

        # 🔎 FUNCIONÁRIOS DO BANCO
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM funcionarios
            WHERE usuario=? AND senha=?
        """, (usuario, senha))

        user = cursor.fetchone()
        conn.close()

        if user:
            session["usuario"] = usuario
            return redirect("/dashboard")
        else:
            return "Usuário ou senha inválidos"

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

@app.route("/salvar", methods=["POST"])
def salvar():
    conn = conectar()
    cursor = conn.cursor()

    nome = request.form["nome"]
    tipo = request.form["tipo"]

    cursor.execute("""
        INSERT INTO animais (nome, tipo)
        VALUES (?, ?)
    """, (nome, tipo))

    conn.commit()
    conn.close()

    return redirect("/cadastro")

@app.route("/dashboard")
def dashboard():

    if "usuario" not in session:
        return redirect("/login")

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