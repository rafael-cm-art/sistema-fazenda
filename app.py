from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "123456"

PRECO_LITRO = 2.5

# conexão com banco
def conectar():
    return sqlite3.connect("banco.db")

# criar banco e tabelas
def criar_banco():
    conn = conectar()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        senha TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS animais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        tipo TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS leite (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        animal TEXT,
        litros REAL,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS peso (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        animal TEXT,
        peso REAL,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS vacinas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        animal TEXT,
        vacina TEXT,
        data_aplicacao DATE,
        proxima_dose DATE
    )
    """)

    # cria usuário padrão
    c.execute("SELECT * FROM usuarios WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO usuarios (username, senha) VALUES ('admin','123')")

    conn.commit()
    conn.close()

# verifica login
def logado():
    return "usuario" in session

# login
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        senha = request.form["senha"]

        conn = conectar()
        c = conn.cursor()
        c.execute("SELECT * FROM usuarios WHERE username=? AND senha=?", (user, senha))
        resultado = c.fetchone()
        conn.close()

        if resultado:
            session["usuario"] = user
            return redirect("/dashboard")

    return render_template("login.html")

# dashboard
@app.route("/dashboard")
def dashboard():
    if not logado():
        return redirect("/")

    conn = conectar()
    c = conn.cursor()

    # animais
    c.execute("SELECT * FROM animais")
    animais = c.fetchall()

    # total leite
    c.execute("SELECT SUM(litros) FROM leite")
    total_leite = c.fetchone()[0] or 0

    # produção por dia
    c.execute("""
    SELECT date(data), SUM(litros)
    FROM leite
    GROUP BY date(data)
    """)
    dados = c.fetchall()

    # lucro
    lucro = total_leite * PRECO_LITRO

    # alertas de vacina (7 dias)
    c.execute("""
    SELECT animal, vacina, proxima_dose
    FROM vacinas
    WHERE date(proxima_dose) <= date('now', '+7 day')
    """)
    alertas = c.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total_leite=total_leite,
        dados=dados,
        lucro=lucro,
        animais=animais,
        alertas=alertas
    )

# tela cadastro
@app.route("/cadastro")
def cadastro():
    if not logado():
        return redirect("/")
    return render_template("cadastro.html")

# salvar animal
@app.route("/salvar", methods=["POST"])
def salvar():
    nome = request.form["nome"]
    tipo = request.form["tipo"]

    conn = conectar()
    c = conn.cursor()
    c.execute("INSERT INTO animais (nome, tipo) VALUES (?, ?)", (nome, tipo))
    conn.commit()
    conn.close()

    return redirect("/dashboard")

# registrar leite
@app.route("/leite", methods=["POST"])
def leite():
    animal = request.form["animal"]
    litros = request.form["litros"]

    conn = conectar()
    c = conn.cursor()
    c.execute("INSERT INTO leite (animal, litros) VALUES (?, ?)", (animal, litros))
    conn.commit()
    conn.close()

    return redirect("/dashboard")

# registrar peso
@app.route("/peso", methods=["POST"])
def peso():
    animal = request.form["animal"]
    peso_valor = request.form["peso"]

    conn = conectar()
    c = conn.cursor()
    c.execute("INSERT INTO peso (animal, peso) VALUES (?, ?)", (animal, peso_valor))
    conn.commit()
    conn.close()

    return redirect("/dashboard")

# registrar vacina
@app.route("/vacina", methods=["POST"])
def vacina():
    animal = request.form["animal"]
    vacina_nome = request.form["vacina"]

    hoje = datetime.now()
    proxima = hoje + timedelta(days=180)

    conn = conectar()
    c = conn.cursor()

    c.execute("""
    INSERT INTO vacinas (animal, vacina, data_aplicacao, proxima_dose)
    VALUES (?, ?, ?, ?)
    """, (
        animal,
        vacina_nome,
        hoje.strftime("%Y-%m-%d"),
        proxima.strftime("%Y-%m-%d")
    ))

    conn.commit()
    conn.close()

    return redirect("/dashboard")

# relatório
@app.route("/relatorio")
def relatorio():
    if not logado():
        return redirect("/")

    conn = conectar()
    c = conn.cursor()

    c.execute("""
    SELECT animal, SUM(litros)
    FROM leite
    WHERE strftime('%m', data) = strftime('%m', 'now')
    GROUP BY animal
    """)
    dados = c.fetchall()

    conn.close()

    return render_template("relatorio.html", dados=dados)

# logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# iniciar sistema
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)