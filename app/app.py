import os
import sqlite3
import random
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://escape_game:escape_game@localhost:5432/escape_game")

def get_connection():
    if "DATABASE_URL" in os.environ or os.environ.get("USE_POSTGRES") == "1":
        try:
            import psycopg
            conn = psycopg.connect(DATABASE_URL, connect_timeout=1, autocommit=True)
            return conn, "PostgreSQL"
        except Exception:
            pass
    db_path = os.path.join(os.path.dirname(__file__), "escape_game.db")
    conn = sqlite3.connect(db_path)
    init_sqlite(conn)
    return conn, "SQLite (mode autonome)"

def init_sqlite(conn):
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS salle (
        id_salle INTEGER PRIMARY KEY AUTOINCREMENT,
        code_salle TEXT NOT NULL UNIQUE,
        nom TEXT NOT NULL,
        capacite_max INTEGER NOT NULL
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS equipe (
        id_equipe INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_equipe TEXT NOT NULL
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS reservation (
        id_reservation INTEGER PRIMARY KEY AUTOINCREMENT,
        code_reservation TEXT NOT NULL UNIQUE,
        date_heure_debut TEXT NOT NULL,
        statut TEXT NOT NULL,
        montant_paye REAL NOT NULL,
        id_salle INTEGER NOT NULL,
        id_equipe INTEGER NOT NULL,
        FOREIGN KEY (id_salle) REFERENCES salle(id_salle),
        FOREIGN KEY (id_equipe) REFERENCES equipe(id_equipe),
        UNIQUE (id_salle, date_heure_debut)
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS avis (
        id_avis INTEGER PRIMARY KEY AUTOINCREMENT,
        id_reservation INTEGER NOT NULL UNIQUE,
        note INTEGER NOT NULL,
        commentaire TEXT,
        date_avis TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_reservation) REFERENCES reservation(id_reservation)
    );
    """)
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM salle")
    if cur.fetchone()[0] == 0:
        cur.executemany("INSERT INTO salle (code_salle, nom, capacite_max) VALUES (?, ?, ?)", [
            ("SALLE-MAYA", "Le Mystere du Temple Maya", 6),
            ("SALLE-LABO", "Le Laboratoire Clandestin", 6),
            ("SALLE-MANOIR", "Les Secrets du Manoir Noir", 5),
            ("SALLE-PRISON", "L Evasion d Alcatraz", 6)
        ])
        cur.executemany("INSERT INTO equipe (nom_equipe) VALUES (?)", [
            ("Les Detectives du Dimanche",),
            ("Escape Masters",),
            ("La Bande du Casse",),
            ("Team Chrono",)
        ])
        cur.executemany("INSERT INTO reservation (code_reservation, date_heure_debut, statut, montant_paye, id_salle, id_equipe) VALUES (?, ?, ?, ?, ?, ?)", [
            ("RES-2026-001", "2026-11-14 10:00:00", "TERMINEE", 120.00, 1, 1),
            ("RES-2026-002", "2026-11-14 14:00:00", "TERMINEE", 120.00, 1, 2),
            ("RES-2026-003", "2026-11-14 16:30:00", "CONFIRMEE", 140.00, 2, 3),
            ("RES-2026-004", "2026-11-15 11:00:00", "EN_ATTENTE", 130.00, 3, 4)
        ])
        cur.executemany("INSERT INTO avis (id_reservation, note, commentaire) VALUES (?, ?, ?)", [
            (1, 5, "Decors immersifs magnifiques et superbes enigmes !"),
            (2, 4, "Tres bonne experience mais quelques indices un peu trop complexes.")
        ])
        conn.commit()

@app.route("/")
def index():
    conn, db_type = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id_salle, code_salle, nom, capacite_max FROM salle ORDER BY id_salle")
    salles = cur.fetchall()

    cur.execute("SELECT id_equipe, nom_equipe FROM equipe ORDER BY id_equipe")
    equipes = cur.fetchall()

    cur.execute("""
        SELECT r.id_reservation, r.code_reservation, s.nom, e.nom_equipe, r.date_heure_debut, r.statut, r.montant_paye
        FROM reservation r
        JOIN salle s ON r.id_salle = s.id_salle
        JOIN equipe e ON r.id_equipe = e.id_equipe
        ORDER BY r.date_heure_debut DESC
    """)
    reservations = cur.fetchall()

    cur.execute("""
        SELECT r.code_reservation, a.note, a.commentaire, a.date_avis
        FROM avis a
        JOIN reservation r ON a.id_reservation = r.id_reservation
        ORDER BY a.date_avis DESC
    """)
    avis = cur.fetchall()

    conn.close()
    return render_template("index.html", salles=salles, equipes=equipes, reservations=reservations, avis=avis, db_type=db_type)

@app.route("/reserver", methods=["POST"])
def reserver():
    id_salle = int(request.form["id_salle"])
    id_equipe = int(request.form["id_equipe"])
    date_heure = request.form["date_heure_debut"].replace("T", " ")
    if len(date_heure) == 16:
        date_heure += ":00"
    montant = float(request.form["montant_paye"])
    code_res = f"RES-2026-{random.randint(100, 999)}"

    conn, db_type = get_connection()
    cur = conn.cursor()
    placeholder = "%s" if db_type == "PostgreSQL" else "?"
    sql = f"INSERT INTO reservation (code_reservation, date_heure_debut, statut, montant_paye, id_salle, id_equipe) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})"
    cur.execute(sql, (code_res, date_heure, "CONFIRMEE", montant, id_salle, id_equipe))
    if db_type != "PostgreSQL":
        conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/avis", methods=["POST"])
def post_avis():
    id_reservation = int(request.form["id_reservation"])
    note = int(request.form["note"])
    commentaire = request.form.get("commentaire", "").strip()

    conn, db_type = get_connection()
    cur = conn.cursor()
    placeholder = "%s" if db_type == "PostgreSQL" else "?"
    sql = f"INSERT INTO avis (id_reservation, note, commentaire) VALUES ({placeholder}, {placeholder}, {placeholder})"
    try:
        cur.execute(sql, (id_reservation, note, commentaire))
        if db_type != "PostgreSQL":
            conn.commit()
    except Exception:
        pass
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
