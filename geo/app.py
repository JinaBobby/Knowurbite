from flask import Flask, jsonify, render_template
import sqlite3

app = Flask(__name__)

def get_vendor_data():
    conn = sqlite3.connect("knowurbite.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT vendor_name, gstin, latitude, longitude, risk_score, complaints, lab_confirmed
        FROM vendors
    """)

    rows = cursor.fetchall()
    conn.close()

    vendors = []
    for row in rows:
        vendors.append({
            "name": row[0],
            "gstin": row[1],
            "lat": row[2],
            "lon": row[3],
            "risk_score": row[4],
            "complaints": row[5],
            "lab_confirmed": bool(row[6])
        })
    return vendors

@app.route("/")
def dashboard():
    return render_template("officer_map.html")

@app.route("/api/vendors")
def vendor_api():
    # 🔹 Sample Vendor Data
    vendors = [
        {
            "name": "ABC Milk Store",
            "gstin": "32ABCDE1234F1Z5",
            "lat": 9.9816,
            "lon": 76.2999,
            "risk_score": 85,
            "complaints": 6,
            "lab_confirmed": True
        },
        {
            "name": "Fresh Spices Hub",
            "gstin": "32FGHIJ5678K2L6",
            "lat": 10.0159,
            "lon": 76.3419,
            "risk_score": 62,
            "complaints": 3,
            "lab_confirmed": False
        },
        {
            "name": "Pure Ghee Traders",
            "gstin": "29MNOPQ1122R3Z7",
            "lat": 11.2588,
            "lon": 75.7804,
            "risk_score": 28,
            "complaints": 1,
            "lab_confirmed": False
        }
    ]
    return jsonify(vendors)

if __name__ == "__main__":
    app.run(debug=True)
