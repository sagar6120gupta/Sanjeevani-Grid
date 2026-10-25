import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).resolve().parent / "database" / "sanjeevani.db"

SUPPLIES = {
    "Anti-venom": "antivenom",
    "Rabies vaccine": "rabies_vaccine",
    "O-negative blood": "oneg_blood",
    "Oxygen": "oxygen",
}

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS phcs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            phone TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock (
            phc_id INTEGER PRIMARY KEY,
            antivenom INTEGER NOT NULL DEFAULT 0,
            rabies_vaccine INTEGER NOT NULL DEFAULT 0,
            oneg_blood INTEGER NOT NULL DEFAULT 0,
            oxygen INTEGER NOT NULL DEFAULT 0,
            last_updated TEXT,
            FOREIGN KEY (phc_id) REFERENCES phcs(id)
        )
    """)

    conn.commit()

    count = cur.execute("SELECT COUNT(*) AS c FROM phcs").fetchone()["c"]
    if count == 0:
        seed_demo_data(conn)

    conn.close()

def seed_demo_data(conn):
    # Demo coordinates are illustrative locations around Mathura.
    phcs = [
        ("PHC Raya", "Raya, Mathura, Uttar Pradesh", 27.5622, 77.7895, "919876500001"),
        ("PHC Baldeo", "Baldeo, Mathura, Uttar Pradesh", 27.4169, 77.8170, "919876500002"),
        ("PHC Govardhan", "Govardhan, Mathura, Uttar Pradesh", 27.4974, 77.4626, "919876500003"),
        ("PHC Chhata", "Chhata, Mathura, Uttar Pradesh", 27.7167, 77.2000, "919876500004"),
        ("PHC Farah", "Farah, Mathura, Uttar Pradesh", 27.3250, 77.7600, "919876500005"),
        ("PHC Naujheel", "Naujheel, Mathura, Uttar Pradesh", 27.8000, 77.7300, "919876500006"),
        ("PHC Mant", "Mant, Mathura, Uttar Pradesh", 27.6800, 77.5800, "919876500007"),
        ("PHC Kosi Kalan", "Kosi Kalan, Mathura, Uttar Pradesh", 27.7950, 77.4350, "919876500008"),
        ("PHC Sonai", "Sonai, Mathura, Uttar Pradesh", 27.4300, 77.7000, "919876500009"),
        ("PHC Jait", "Jait, Mathura, Uttar Pradesh", 27.5600, 77.6500, "919876500010"),
    ]

    cur = conn.cursor()
    now = datetime.now()

    for i, row in enumerate(phcs):
        cur.execute("""
            INSERT INTO phcs (name, address, latitude, longitude, phone)
            VALUES (?, ?, ?, ?, ?)
        """, row)
        phc_id = cur.lastrowid

        # Deliberately varied demo inventory and freshness.
        values = [
            (1, 1, 1, 1, now - timedelta(minutes=8)),
            (1, 0, 1, 1, now - timedelta(minutes=25)),
            (0, 1, 0, 1, now - timedelta(hours=2)),
            (1, 1, 0, 0, now - timedelta(hours=4)),
            (0, 0, 1, 1, now - timedelta(hours=1)),
            (1, 0, 0, 1, now - timedelta(hours=27)),  # becomes unverified
            (0, 1, 1, 0, now - timedelta(minutes=40)),
            (1, 1, 1, 0, now - timedelta(hours=5)),
            (0, 0, 0, 1, now - timedelta(minutes=15)),
            (1, 1, 0, 1, now - timedelta(minutes=55)),
        ][i]

        cur.execute("""
            INSERT INTO stock
            (phc_id, antivenom, rabies_vaccine, oneg_blood, oxygen, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (phc_id, values[0], values[1], values[2], values[3], values[4].isoformat()))

    conn.commit()

def get_all_phcs():
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.*, s.antivenom, s.rabies_vaccine, s.oneg_blood, s.oxygen,
               s.last_updated
        FROM phcs p
        JOIN stock s ON p.id = s.phc_id
        ORDER BY p.name
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_phc(phc_id):
    conn = get_connection()
    row = conn.execute("""
        SELECT p.*, s.antivenom, s.rabies_vaccine, s.oneg_blood, s.oxygen,
               s.last_updated
        FROM phcs p
        JOIN stock s ON p.id = s.phc_id
        WHERE p.id = ?
    """, (phc_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_stock(phc_id, stock_values):
    conn = get_connection()
    conn.execute("""
        UPDATE stock
        SET antivenom = ?,
            rabies_vaccine = ?,
            oneg_blood = ?,
            oxygen = ?,
            last_updated = ?
        WHERE phc_id = ?
    """, (
        int(stock_values["antivenom"]),
        int(stock_values["rabies_vaccine"]),
        int(stock_values["oneg_blood"]),
        int(stock_values["oxygen"]),
        datetime.now().isoformat(),
        phc_id,
    ))
    conn.commit()
    conn.close()

def get_dashboard_stats():
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) AS c FROM phcs").fetchone()["c"]
    stock = conn.execute("""
        SELECT
            SUM(antivenom) AS antivenom,
            SUM(rabies_vaccine) AS rabies_vaccine,
            SUM(oneg_blood) AS oneg_blood,
            SUM(oxygen) AS oxygen
        FROM stock
    """).fetchone()

    rows = conn.execute("SELECT last_updated FROM stock").fetchall()
    conn.close()

    now = datetime.now()
    unverified = 0
    for row in rows:
        try:
            dt = datetime.fromisoformat(row["last_updated"])
            if now - dt > timedelta(hours=24):
                unverified += 1
        except Exception:
            unverified += 1

    return {
        "total_phcs": total,
        "antivenom": int(stock["antivenom"] or 0),
        "rabies_vaccine": int(stock["rabies_vaccine"] or 0),
        "oneg_blood": int(stock["oneg_blood"] or 0),
        "oxygen": int(stock["oxygen"] or 0),
        "unverified": unverified,
    }
