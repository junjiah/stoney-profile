import io
import sqlite3

from flask import abort, Flask, g, send_file

DB_PATH = "profiles.db"

app = Flask(__name__, static_url_path="", static_folder="static")


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
    return db


@app.route("/")
def root():
    return app.send_static_file("index.html")


@app.route("/profile/<int:ts>")
def get_profile(ts):
    cursor = get_db().cursor()
    sql = """
        select DATA from PROFILES where PIC_ID = (
            select PIC_ID from PROFILE_HISTORY where UPDATED_AT <= :ts
            order by UPDATED_AT desc limit 1
        );
    """.strip()
    cursor.execute(sql, {"ts": ts})
    res = cursor.fetchone()
    if not res:
        abort(404, description="Profile not found")

    binary_data = res[0]
    return send_file(io.BytesIO(binary_data), mimetype="image/jpeg")


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()
