from dotenv import load_dotenv
import os
import json
import psycopg2
from pymongo import MongoClient
from flask import Flask, jsonify, render_template
from flask_compress import Compress

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
def index():
    return render_template('map.html', MapboxAPI=MapboxAPI)

@app.route('/relays', methods=['GET'])
def get_existing_tor_relays():
    try:
        ExistingTorRelaysData = [
            {
                'fingerprint': relay.get('fingerprint'),
                'nickname': relay.get('nickname'),
                'latitude': relay.get('latitude'),
                'longitude': relay.get('longitude'),
                'city': relay.get('city'),
                'region': relay.get('region'),
                'country_name': relay.get('country_name'),
            }
            for relay in db.TorRelayData.find({}, {
                'fingerprint': 1,
                'nickname': 1,
                'latitude': 1,
                'longitude': 1,
                'city': 1,
                'region': 1,
                'country_name': 1
            })
        ]

        return jsonify(ExistingTorRelaysData), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)