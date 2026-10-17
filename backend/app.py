# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template_string
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = "attendance.db"

AUTHORIZED_USERS = {
    "B39A1C2D": "Yesim Ulgen",
    "63A06829": "Ogrenci - 2"
}

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT NOT NULL,
            name TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route('/api/attendance', methods=['POST'])
def record_attendance():
    data = request.get_json()
    if not data or 'uid' not in data:
        return jsonify({"status": "error", "message": "UID bulunamadi"}), 400

    uid = data['uid'].strip().upper()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if uid in AUTHORIZED_USERS:
        user_name = AUTHORIZED_USERS[uid]
        status_code = 200
    else:
        user_name = "Yetkisiz / Tanimsiz"
        status_code = 403

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO attendance (uid, name, timestamp) VALUES (?, ?, ?)", (uid, user_name, now))
    conn.commit()
    conn.close()

    print(f"[{'ONAYLANDI' if status_code == 200 else 'REDDEDILDI'}] {user_name} ({uid}) - {now}")
    return jsonify({"status": "success" if status_code == 200 else "unauthorized", "name": user_name, "time": now}), status_code

@app.route('/')
def dashboard():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, uid, timestamp FROM attendance ORDER BY id DESC")
    records = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) FROM attendance")
    total_scans = cursor.fetchone()[0]
    conn.close()

    last_user = records[0][1] if records else "Henuz Yok"

    html = """
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>IoT Attendance Hub</title>
        <meta http-equiv="refresh" content="3">
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg: #0f172a;
                --card-bg: #1e293b;
                --accent: #6366f1;
                --text-main: #f8fafc;
                --text-muted: #94a3b8;
                --border: rgba(255, 255, 255, 0.08);
                --success: #10b981;
                --danger: #ef4444;
            }
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
            body { background-color: var(--bg); color: var(--text-main); min-height: 100vh; padding: 40px 20px; }
            .container { max-width: 1000px; margin: 0 auto; }
            
            .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
            .header h1 { font-size: 26px; font-weight: 700; letter-spacing: -0.5px; }
            .live-badge { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--success); font-weight: 600; }
            .pulse { width: 9px; height: 9px; background: var(--success); border-radius: 50%; box-shadow: 0 0 10px var(--success); animation: pulse 1.5s infinite; }
            @keyframes pulse { 0% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(1.2); } 100% { opacity: 1; transform: scale(1); } }

            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 18px; margin-bottom: 30px; }
            .stat-card { background: var(--card-bg); padding: 20px; border-radius: 14px; border: 1px solid var(--border); }
            .stat-title { font-size: 13px; color: var(--text-muted); font-weight: 500; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
            .stat-value { font-size: 24px; font-weight: 700; color: #fff; }

            .table-container { background: var(--card-bg); border-radius: 16px; border: 1px solid var(--border); overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
            table { width: 100%; border-collapse: collapse; text-align: left; font-size: 14px; }
            th { background: rgba(255, 255, 255, 0.03); color: var(--text-muted); font-weight: 600; padding: 16px 20px; border-bottom: 1px solid var(--border); }
            td { padding: 16px 20px; border-bottom: 1px solid var(--border); color: var(--text-main); }
            tr:last-child td { border-bottom: none; }
            tr:hover { background: rgba(255, 255, 255, 0.02); }

            .uid-tag { font-family: monospace; background: rgba(99, 102, 241, 0.15); color: #818cf8; padding: 4px 8px; border-radius: 6px; font-size: 13px; font-weight: 600; }
            .badge { display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
            .badge-success { background: rgba(16, 185, 129, 0.15); color: var(--success); }
            .badge-danger { background: rgba(239, 68, 68, 0.15); color: var(--danger); }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div>
                    <h1>Yoklama ve Erisim Paneli</h1>
                    <p style="color: var(--text-muted); font-size: 14px; margin-top: 4px;">ESP32 RFID Canli Takip Arayuzu</p>
                </div>
                <div class="live-badge">
                    <div class="pulse"></div> CANLI BAGLANTI
                </div>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-title">Toplam Okuma</div>
                    <div class="stat-value">{{ total_scans }}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">Son Giris Yapan</div>
                    <div class="stat-value" style="font-size: 20px; color: #818cf8;">{{ last_user }}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">Sunucu Portu</div>
                    <div class="stat-value">5000</div>
                </div>
            </div>

            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Kullanici / Kart Sahibi</th>
                            <th>Kart UID</th>
                            <th>Giris Saati</th>
                            <th>Erisim Durumu</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for row in records %}
                        <tr>
                            <td style="color: var(--text-muted);">{{ row[0] }}</td>
                            <td><strong>{{ row[1] }}</strong></td>
                            <td><span class="uid-tag">{{ row[2] }}</span></td>
                            <td style="color: var(--text-muted);">{{ row[3] }}</td>
                            <td>
                                {% if row[1] != 'Yetkisiz / Tanimsiz' %}
                                    <span class="badge badge-success">Onaylandi</span>
                                {% else %}
                                    <span class="badge badge-danger">Yetkisiz</span>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, records=records, total_scans=total_scans, last_user=last_user)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)