from flask import Flask, request, jsonify, render_template
import sqlite3
import csv
import os

app = Flask(__name__)

DATABASE = "guests.db"
CSV_FILE = "guests_with_ids.csv"


# -----------------------------
# CREATE DATABASE + TABLE
# -----------------------------
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS guests (
            unique_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            checked_in INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()

init_db()


# -----------------------------
# IMPORT CSV INTO DATABASE
# (Runs safely, no duplicates)
# -----------------------------
def import_csv_to_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                cursor.execute("""
                    INSERT OR IGNORE INTO guests (unique_id, name)
                    VALUES (?, ?)
                """, (row["unique_id"], row["name"]))

        conn.commit()

    conn.close()

import_csv_to_db()


# -----------------------------
# SCANNER PAGE
# -----------------------------
@app.route('/')
def scanner_page():
    return render_template('scanner.html')


# -----------------------------
# CHECK-IN ROUTE (PERMANENT)
# -----------------------------
@app.route('/checkin', methods=['POST'])
def checkin():
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No JSON received"}), 400

    scanned_id = data.get("id")

    if not scanned_id:
        return jsonify({"status": "error", "message": "No ID in JSON"}), 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name, checked_in FROM guests WHERE unique_id = ?",
        (scanned_id,)
    )

    guest = cursor.fetchone()

    if not guest:
        conn.close()
        return jsonify({"status": "error", "message": "Guest not found"})

    name, checked_in = guest

    if checked_in == 1:
        conn.close()
        return jsonify({"status": "already", "name": name})

    cursor.execute(
        "UPDATE guests SET checked_in = 1 WHERE unique_id = ?",
        (scanned_id,)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "name": name
    })


# -----------------------------
# GET ALL GUESTS (FOR SIDEBAR)
# -----------------------------
@app.route('/guests', methods=['GET'])
def get_guests():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT unique_id, name, checked_in FROM guests")
    rows = cursor.fetchall()

    conn.close()

    guests = []
    for row in rows:
        guests.append({
            "id": row[0],
            "name": row[1],
            "checked_in": bool(row[2])
        })

    return jsonify(guests)


# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
