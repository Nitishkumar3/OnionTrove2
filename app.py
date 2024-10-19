from dotenv import load_dotenv
import os
import json
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from pymongo import MongoClient
from flask import Flask, jsonify, render_template, request, jsonify, session, redirect, url_for, flash
from flask_compress import Compress
from functools import wraps
import jwt
from datetime import datetime, timedelta
from GenAI import Llama31Instant8B, DorkAI

load_dotenv()

IPInfoAPI = os.getenv('IPInfoAPIKey')
Postgres = json.loads(os.getenv('PostgreSQLConnectionParams'))
MongoDB = os.getenv('MongoDBConnectionString')
MapboxAPI = os.getenv('MapboxAPIKey')

client = MongoClient(MongoDB)
db = client['oniontrovedb'] 

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SecretKey')
Compress(app) 

def IsLoggedIn(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session:
            token = session['SessionKey']
        else:
            flash('Please log in to access the page.', 'error')
            return redirect(url_for('login'))
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            flash('Token has expired!', 'error')
            return redirect(url_for('login'))
        except jwt.InvalidTokenError:
            flash('Token is invalid.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['login']
        password = request.form['password']
        with psycopg2.connect(**Postgres) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, password FROM users WHERE email = %s", (email,))
                user = cur.fetchone()
                if user:
                    user_id, db_password = user
                    if db_password == password:
                        token = jwt.encode({
                            'user_id': user_id,
                            'exp': datetime.utcnow() + timedelta(hours=6)
                        }, app.config['SECRET_KEY'], algorithm="HS256")
                        session['SessionKey'] = token
                        return redirect(url_for('dashboard'))
                    else:
                        flash('Invalid credentials.', 'error')
                        return redirect(url_for('login'))
                else:
                    flash('User not found.', 'error')
                    return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    return "Hi"

@app.route('/dashboard')
@IsLoggedIn
def dashboard():
    return render_template("dashboard.html")

### Keywords
@app.route('/keywords')
@IsLoggedIn
def keywords():
    with psycopg2.connect(**Postgres) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM keywords")
            keywords = cur.fetchall()
            keywords = json.dumps(dict(keywords))
            print(keywords)
    return render_template("keywords.html", keywords=keywords)

# Add Keyword
@app.route('/keywords/add', methods=['POST'])
@IsLoggedIn
def addkeyword():
    keyword = request.form['keyword']
    with psycopg2.connect(**Postgres) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT sno FROM dorks WHERE dork = %s", (keyword,))
            existing_record = cur.fetchone()
            if existing_record is None:
                insert_query = sql.SQL("INSERT INTO dorks (dork, timesused, lastused, dateadded) VALUES (%s, 0, NULL, CURRENT_TIMESTAMP)")
                cur.execute(insert_query, (keyword,))
            #     flash("Inserted new keyword")
            # else:
            #     flash("Keyword already exists")
            conn.commit()
    return redirect(url_for('keywords'))

# AI
@app.route('/keywords/ai', methods=['POST'])
@IsLoggedIn
def aidork():
    prompt = request.form['prompt']
    dorks = DorkAI(prompt)
    print(dorks)
    # flash()
    return redirect(url_for('keywords'))

@app.route('/map')
@IsLoggedIn
def map():
    return render_template('map.html', MapboxAPI=MapboxAPI)

@app.route('/relays')
@IsLoggedIn
def relays():
    with open('static/TorRelaysDataTable.json', 'r') as file:
        TorRelaysDataTable = json.load(file)
    return render_template('relays.html', TorRelaysDataTable=TorRelaysDataTable)

@app.route('/api/stats', methods=['GET'])
@IsLoggedIn
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