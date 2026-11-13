import os
import ssl
import pymysql
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()  # lee .env SOLO en local; en la nube se usa el panel

app = Flask(__name__, static_folder="static", static_url_path="")


def get_conn():
    kwargs = dict(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=10,
    )
    # Muchos MySQL en la nube exigen TLS: poner DB_SSL=true en el panel
    if os.getenv("DB_SSL") == "true":
        kwargs["ssl"] = ssl.create_default_context()
    return pymysql.connect(**kwargs)


@app.get("/")
def inicio():
    return app.send_static_file("index.html")


@app.get("/api/health")
def health():
    try:
        conn = get_conn()
        conn.close()
        return jsonify(ok=True, database="conectada")
    except Exception as e:
        app.logger.error("Health: %s", type(e).__name__)  # sin contraseñas
        return jsonify(ok=False, database="sin conexion"), 500


@app.get("/api/tickets")
def listar():
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT id, titulo, descripcion, solicitante, estado, creado "
                        "FROM tickets ORDER BY id DESC LIMIT 100")
            filas = cur.fetchall()
        conn.close()
        for f in filas:
            f["creado"] = str(f["creado"])
        return jsonify(filas)
    except Exception as e:
        app.logger.error("GET tickets: %s", type(e).__name__)
        return jsonify(error="No se pudo consultar"), 500


@app.post("/api/tickets")
def crear():
    d = request.get_json(silent=True) or {}
    titulo, desc, sol = d.get("titulo"), d.get("descripcion"), d.get("solicitante")
    if not (titulo and desc and sol):
        return jsonify(error="Faltan campos"), 400
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("INSERT INTO tickets (titulo, descripcion, solicitante) VALUES (%s,%s,%s)",
                        (str(titulo)[:120], str(desc), str(sol)[:80]))
            nuevo = cur.lastrowid
        conn.commit()
        conn.close()
        return jsonify(id=nuevo), 201
    except Exception as e:
        app.logger.error("POST tickets: %s", type(e).__name__)
        return jsonify(error="No se pudo registrar"), 500


if __name__ == "__main__":
    # Solo para laboratorio. En la nube se usa: gunicorn --bind 0.0.0.0:$PORT app:app
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
