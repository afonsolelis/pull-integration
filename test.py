from flask import Flask, jsonify
import requests
from datetime import datetime, timedelta
import sqlite3

app = Flask(__name__)

DATABASE_FILE = 'local_database.db'

@app.route('/createtable', methods=['GET'])
def create_table():
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY,
        amount INTEGER,
        saleDate TEXT,
        cnpj TEXT,
        idCategory INTEGER,
        value REAL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS category (
        id INTEGER PRIMARY KEY,
        isActive BOOLEAN,
        name TEXT
    )
    """)

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "success", "message": "Tables checked/created successfully!"}), 200

@app.route('/tellme', methods=['GET'])
def return_response():
    return jsonify({"status": "success", "message": "Hello, I'm alive!"}), 200

@app.route('/update', methods=['GET'])
def update_data():
    sale_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    url = "https://intelifunctiongetdata.azurewebsites.net/api/InteliFunctionGetData"
    params = {
        "code": "pZh3gmJW_87epswrWDuB7CvQle-KqjsVh2ZJUaifiXd4AzFuOEy98w==",
        "table": "sale",
        "saleDate": sale_date,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()


        if not isinstance(data, list):
            return jsonify({"status": "error", "message": "Invalid data format from the endpoint."}), 500

        conn = sqlite3.connect(DATABASE_FILE)
        cur = conn.cursor()

        added_categories = set() # Para garantir que cada categoria seja adicionada apenas uma vez

        for sale in data:
            cur.execute("INSERT OR REPLACE INTO sales (id, amount, saleDate, cnpj, idCategory, value) VALUES (?, ?, ?, ?, ?, ?)",
                        (sale['id'], sale['amount'], sale['saleDate'], sale['cnpj'], sale['idCategory'], sale['value']))

            category = sale['category']
            if category['id'] not in added_categories:
                cur.execute("INSERT OR REPLACE INTO category (id, isActive, name) VALUES (?, ?, ?)",
                            (category['id'], category['isActive'], category['name']))
                added_categories.add(category['id'])

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"status": "success", "message": "Data updated successfully!"}), 200
    else:
        return jsonify({"status": "error", "message": "Failed to fetch data from the endpoint."}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
