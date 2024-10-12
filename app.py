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

if __name__ == '__main__':
    app.run(debug=True)