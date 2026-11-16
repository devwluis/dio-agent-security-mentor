"""
app_corrigido.py: versão corrigida do app.py (laboratório local).

Mudanças:
1. Consulta parametrizada (mitiga SQL Injection, CWE-89 / OWASP A03:2021).
2. Senha guardada com hash (werkzeug), nunca em texto puro.
3. debug desligado e servidor preso a 127.0.0.1.
4. Mesma mensagem de erro para usuário inexistente e senha errada.
"""

import sqlite3
from flask import Flask, request
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
DB_PATH = "usuarios_seguro.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def setup_db():
    conn = get_connection()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, "
        "usuario TEXT UNIQUE, senha_hash TEXT)"
    )
    conn.execute(
        "INSERT OR IGNORE INTO usuarios (usuario, senha_hash) VALUES (?, ?)",
        ("admin", generate_password_hash("admin123")),  # senha só de laboratório
    )
    conn.commit()
    conn.close()


@app.route("/login", methods=["POST"])
def login():
    usuario = request.form.get("usuario", "")
    senha = request.form.get("senha", "")

    conn = get_connection()
    linha = conn.execute(
        "SELECT senha_hash FROM usuarios WHERE usuario = ?", (usuario,)
    ).fetchone()
    conn.close()

    if linha and check_password_hash(linha[0], senha):
        return {"status": "ok", "mensagem": f"Bem-vindo, {usuario}!"}
    return {"status": "erro", "mensagem": "Credenciais invalidas"}, 401


if __name__ == "__main__":
    setup_db()
    app.run(debug=False, host="127.0.0.1", port=5000)
