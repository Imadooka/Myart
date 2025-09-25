
import os
from flask import Flask, render_template, send_file, abort
from dotenv import load_dotenv
import mysql.connector
from io import BytesIO

load_dotenv()

app = Flask(__name__)

DB_CFG = dict(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.getenv("DB_USER", "artuser"),
    password=os.getenv("DB_PASS", ""),
    database=os.getenv("DB_NAME", "artdb"),
)

def get_conn():
    return mysql.connector.connect(**DB_CFG)

@app.route("/")
def index():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, title, artist, year, medium, description_th FROM artworks ORDER BY created_at DESC")
    arts = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", arts=arts)

@app.route("/image/<int:art_id>")
def image(art_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT image, image_mime FROM artworks WHERE id=%s", (art_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row: abort(404)
    blob, mime = row
    return send_file(BytesIO(blob), mimetype=mime)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
