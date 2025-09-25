
"""
Seed script: insert 5 artworks (images + Thai descriptions) into MySQL on VM1.

Usage:
  1) Put your 5 image files into a folder named "images" (same dir as this script).
  2) Create a descriptions.json (see example below) with 5 records (title, artist, year, medium, description_th, filename).
  3) Set DB connection env via .env or export variables.
  4) Run:  python seed.py

Example descriptions.json:
[
  {
    "title": "สายลมเหนือผิวน้ำ",
    "artist": "ไม่ทราบ",
    "year": "2025",
    "medium": "สีน้ำบนกระดาษ",
    "description_th": "ฉันชอบงานชิ้นนี้เพราะโทนสีเย็นทำให้รู้สึกสงบ คลื่นบางเบาเหมือนเสียงลมหายใจ...",
    "filename": "art1.jpg"
  },
  {
    "title": "แสงเย็นย่านเก่า",
    "artist": "ไม่ทราบ",
    "year": "2024",
    "medium": "สีน้ำมันบนผ้าใบ",
    "description_th": "ภาพสะท้อนแสงสุดท้ายของวันบนอาคารเก่า ทำให้คิดถึงความทรงจำในเมืองเล็ก...",
    "filename": "art2.jpg"
  }
]
"""
import os, json, mimetypes, mysql.connector
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")   # VM1 Private IP
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "artuser")
DB_PASS = os.getenv("DB_PASS", "strong_password_here")
DB_NAME = os.getenv("DB_NAME", "artdb")

def main():
    with open("descriptions.json", "r", encoding="utf-8") as f:
        records = json.load(f)

    conn = mysql.connector.connect(
        host=DB_HOST, port=DB_PORT,
        user=DB_USER, password=DB_PASS, database=DB_NAME
    )
    cur = conn.cursor()

    for rec in records:
        path = os.path.join("images", rec["filename"])
        with open(path, "rb") as imgf:
            blob = imgf.read()
        mime = mimetypes.guess_type(rec["filename"])[0] or "image/jpeg"

        cur.execute(
            """
            INSERT INTO artworks (title, artist, year, medium, description_th, image, image_mime)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (rec.get("title"), rec.get("artist"), rec.get("year"),
             rec.get("medium"), rec.get("description_th"), blob, mime)
        )
        print(f"Inserted: {rec.get('title')}")

    conn.commit()
    cur.close()
    conn.close()
    print("Done.")

if __name__ == "__main__":
    main()
