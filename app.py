from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
import sqlite3


app.secret_key = "123456"

PRECO_LITRO = 2.5


# ---------------- BANCO ----------------
def conectar():
    return sqlite3.connect("banco3.db")


# cria tabelas automaticamente
def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS funcionarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        usuario TEXT,
        senha TEXT,
        fazenda_id INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fazendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS animais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        tipo TEXT,
        brinco TEXT,
        sexo TEXT,
        fazenda_id INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS anotacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        animal_id INTEGER,
        texto TEXT,
        data TEXT
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

    # 🔥 NOVO (guarda a fazenda)
    if len(user) > 4:
        session["fazenda_id"] = user[4]
    else:
        session["fazenda_id"] = 1  # padrão temporário

    return redirect("/dashboard")

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/cadastro")
def cadastro():
    conn = sqlite3.connect("banco3.db")
    cursor = conn.cursor()

    # ANIMAIS (protege erro de tabela inexistente)
    try:
        cursor.execute(
            "SELECT * FROM animais WHERE fazenda_id = ?",
            (session.get("fazenda_id", 1),)
        )
        animais = cursor.fetchall()
    except:
        animais = []

    # ANOTAÇÕES (protege também)
    try:
        cursor.execute("SELECT * FROM anotacoes")
        anotacoes = cursor.fetchall()
    except:
        anotacoes = []

    conn.close()

    return render_template(
        "cadastro.html",
        animais=animais,
        anotacoes=anotacoes
    )

from datetime import datetime

@app.route("/anotar/<int:animal_id>", methods=["POST"])
def anotar(animal_id):
    conn = sqlite3.connect("banco3.db")
    cursor = conn.cursor()

    texto = request.form["texto"]
    data = datetime.now().strftime("%d/%m/%Y")

    cursor.execute("""
        INSERT INTO anotacoes (animal_id, texto, data)
        VALUES (?, ?, ?)
    """, (animal_id, texto, data))

    conn.commit()
    conn.close()

    return redirect("/cadastro")

@app.route("/salvar", methods=["POST"])
def salvar():
    conn = sqlite3.connect("banco3.db")
    cursor = conn.cursor()

    nome = request.form.get("nome")
    tipo = request.form.get("tipo")
    brinco = request.form.get("brinco", "")
    sexo = request.form.get("sexo", "")

    cursor.execute("""
        INSERT INTO animais (nome, tipo, brinco, sexo, fazenda_id)
        VALUES (?, ?, ?, ?, ?)
        """, (nome, tipo, brinco, sexo, session["fazenda_id"]))

    conn.commit()
    conn.close()

    return redirect("/cadastro")

@app.route("/excluir_funcionario/<int:id>")
def excluir_funcionario(id):
    if session.get("usuario") != "admin":
        return "Acesso negado"

    conn = sqlite3.connect("banco3.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM funcionarios WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    return redirect("/funcionarios")

@app.route("/excluir/<int:id>")
def excluir(id):
    conn = sqlite3.connect("banco3.db")
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM anotacoes WHERE animal_id = ?", (id,))
    except:
        pass

    try:
        cursor.execute("DELETE FROM animais WHERE id = ?", (id,))
    except:
        pass

    conn.commit()
    conn.close()

    return redirect("/cadastro")

@app.route("/dashboard")
def dashboard():

    if "usuario" not in session:
        return redirect("/login")

    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT data, litros FROM leite")
        dados = cursor.fetchall()
    except:
        dados = []

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
    if "usuario" not in session:
        return redirect("/login")

    conn = sqlite3.connect("banco3.db")
    cursor = conn.cursor()

    if request.method == "POST":
        # só admin pode cadastrar
        if session.get("usuario") != "admin":
            return "Acesso negado"

        nome = request.form["nome"]
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        cursor.execute("""
        INSERT INTO funcionarios (nome, usuario, senha)
        VALUES (?, ?, ?)
        """, (nome, usuario, senha))

        conn.commit()

    cursor.execute(
        "SELECT * FROM funcionarios WHERE fazenda_id = ?",
        (session.get("fazenda_id", 1),)
    )
    dados = cursor.fetchall()

    conn.close()

    return render_template("funcionarios.html", dados=dados)


# ---------------- PORTA (RENDER) ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)