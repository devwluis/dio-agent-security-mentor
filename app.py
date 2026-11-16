"""
app.py: aplicação de exemplo DELIBERADAMENTE vulnerável, para o desafio
GuardAI (DIO). Uso exclusivo em laboratório local/próprio. Nunca exponha
isto a uma rede que não seja sua.

O login monta a consulta SQL concatenando a entrada do usuário:
vulnerável a SQL Injection (CWE-89 / OWASP A03:2021-Injection).
"""

import sqlite3
from flask import Flask, request

app = Flask(__name__)
DB_PATH = "usuarios.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def setup_db():
    conn = get_connection()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, "
        "usuario TEXT, senha TEXT)"
    )
    conn.execute(
        "INSERT OR IGNORE INTO usuarios (id, usuario, senha) "
        "VALUES (1, 'admin', 'admin123')"
    )
    conn.commit()
    conn.close()


@app.route("/login", methods=["POST"])
def login():
    usuario = request.form.get("usuario", "")
    senha = request.form.get("senha", "")

    # VULNERÁVEL: concatenação direta da entrada do usuário na query.
    query = (
        "SELECT * FROM usuarios WHERE usuario = '" + usuario +
        "' AND senha = '" + senha + "'"
    )

    conn = get_connection()
    cursor = conn.execute(query)
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        return {"status": "ok", "mensagem": f"Bem-vindo, {usuario}!"}
    return {"status": "erro", "mensagem": "Credenciais invalidas"}, 401


if __name__ == "__main__":
    setup_db()
    app.run(debug=False, host="127.0.0.1", port=5000)
