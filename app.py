from dotenv import load_dotenv
import os
import json
import psycopg2
from pymongo import MongoClient
from flask import Flask, jsonify, render_template
from flask_compress import Compress
from psycopg2.extras import RealDictCursor

load_dotenv()

IPInfoAPI = os.getenv('IPInfoAPIKey')
Postgres = json.loads(os.getenv('PostgreSQLConnectionParams'))
MongoDB = os.getenv('MongoDBConnectionString')
MapboxAPI = os.getenv('MapboxAPIKey')

client = MongoClient(MongoDB)
db = client['oniontrovedb'] 

app = Flask(__name__)
Compress(app) 

@app.route('/map')
def map():
    return render_template('map.html', MapboxAPI=MapboxAPI)

@app.route('/relays')
def relays():
    with open('static/TorRelaysDataTable.json', 'r') as file:
        TorRelaysDataTable = json.load(file)
    return render_template('relays.html', TorRelaysDataTable=TorRelaysDataTable)

@app.route('/api/stats', methods=['GET'])
def StatsAPI():
    try:
        with psycopg2.connect(**Postgres) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute('SELECT * FROM TorMetrics ORDER BY date DESC')
                data = cursor.fetchall()
                return jsonify(data)
    except psycopg2.DatabaseError as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)