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
from GenAI import DorkAI
from werkzeug.exceptions import BadRequest, InternalServerError

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
    try:
        with psycopg2.connect(**Postgres) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM dorks")
                keywords = cur.fetchall()

        FormattedKeywords = []

        for index, (id_num, keyword, times_used, last_used, date_added) in enumerate(keywords):
            formatted_keyword = {
                "id": id_num,
                "keyword": keyword,
                "lastused": last_used.strftime("%Y-%m-%d %H:%M") if last_used else None,
                "timesused": times_used,
                "dateadded": date_added.strftime("%Y-%m-%d %H:%M")
            }
            FormattedKeywords.append(formatted_keyword)

        print(FormattedKeywords)
        return render_template("keywords/index.html", keywords=FormattedKeywords)
    except psycopg2.Error as e:
        flash(f"Database error: {str(e)}", "error")
        return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}", "error")
        return redirect(url_for('dashboard'))

# Delete Keyword
@app.route('/keywords/delete/<int:id>')
@IsLoggedIn
def deletekeyword(id):
    try:
        with psycopg2.connect(**Postgres) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM dorks WHERE sno = %s RETURNING *", (id,))
                deleted_row = cur.fetchone()

                if deleted_row:
                    flash("Keyword deleted successfully", "success")
                    return redirect(url_for('keywords'))
                else:
                    flash("Keyword not deleted", "error")
                    return redirect(url_for('keywords'))
    except Exception as e:
        flash(e)
        return redirect(url_for('keywords'))
    
# Add Keyword
@app.route('/keywords/add', methods=['POST'])
@IsLoggedIn
def addkeyword():
    keyword = request.form['keyword']
    try:
        with psycopg2.connect(**Postgres) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT sno FROM dorks WHERE dork = %s", (keyword,))
                existing_record = cur.fetchone()
                if existing_record is None:
                    insert_query = sql.SQL("INSERT INTO dorks (dork, timesused, lastused, dateadded) VALUES (%s, 0, NULL, CURRENT_TIMESTAMP)")
                    cur.execute(insert_query, (keyword,))
                    flash("Keyword added successfully", "success")
                else:
                    flash("Keyword already exists", "info")
                conn.commit()
        return redirect(url_for('keywords'))
    except psycopg2.Error as e:
        conn.rollback()
        flash(f"Database error: {str(e)}", "error")
        return redirect(url_for('keywords'))
    except Exception as e:
        conn.rollback()
        flash(f"An unexpected error occurred: {str(e)}", "error")
        return redirect(url_for('keywords'))
    
# AI Dorks
@app.route('/keywords/ai', methods=['POST'])
@IsLoggedIn
def aidork():
    try:
        prompt = request.form['prompt']
        dorks = DorkAI(prompt)
        return render_template('keywords/aidork.html', dorks=dorks)
    except KeyError:
        return jsonify({'error': 'Missing prompt in form data'}), 400
    except Exception as e:
        app.logger.error(f"An error occurred in aidork: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

# @app.route('/keywords/ai/add', methods=['POST'])
# @IsLoggedIn
# def aidorkadd():
#     try:
#         aidorks = request.json

#         if not aidorks:
#             raise BadRequest('No JSON data provided')
        
#         with psycopg2.connect(**Postgres) as conn:
#             with conn.cursor() as cur:
#                 cur.execute("SELECT dork FROM dorks WHERE dork = ANY(%s)", (aidorks,))
#                 existing_keywords = {row[0] for row in cur.fetchall()}  
#                 new_keywords = [keyword for keyword in aidorks if keyword not in existing_keywords]
#                 if new_keywords:
#                     insert_query = sql.SQL("INSERT INTO dorks (dork, timesused, lastused, dateadded) VALUES (%s, 0, NULL, CURRENT_TIMESTAMP)")
#                     cur.executemany(insert_query, [(keyword,) for keyword in new_keywords])
#                     flash(f"{len(new_keywords)} new keywords added successfully", "success")
#                 else:
#                     flash("No new keywords to add", "info")
#                 conn.commit()
#         return jsonify({'message': 'Data received'}), 200
#     except BadRequest as e:
#         return jsonify({'error': str(e)}), 400
#     except Exception as e:
#         app.logger.error(f"An error occurred in aidorkadd: {str(e)}")
#         return jsonify({'error': 'An unexpected error occurred'}), 500

# AI Dorks Add
@app.route('/keywords/ai/add', methods=['POST'])
@IsLoggedIn
def aidorkadd():
    try:
        aidorks = request.json
        if not aidorks:
            raise BadRequest('No JSON data provided')
        
        if not isinstance(aidorks, list):
            raise BadRequest('Invalid data format. Expected a list of keywords.')

        with psycopg2.connect(**Postgres) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("SELECT dork FROM dorks WHERE dork = ANY(%s)", (aidorks,))
                    existing_keywords = {row[0] for row in cur.fetchall()}  
                    new_keywords = [keyword for keyword in aidorks if keyword not in existing_keywords]
                    
                    if new_keywords:
                        insert_query = sql.SQL("INSERT INTO dorks (dork, timesused, lastused, dateadded) VALUES (%s, 0, NULL, CURRENT_TIMESTAMP)")
                        cur.executemany(insert_query, [(keyword,) for keyword in new_keywords])
                        conn.commit()
                        flash(f"{len(new_keywords)} new keywords added successfully", "success")
                    else:
                        flash("No new keywords to add", "info")
                    
                    return jsonify({'message': 'Data processed successfully', 'new_keywords_added': len(new_keywords)}), 200
                
                except psycopg2.Error as db_error:
                    conn.rollback()
                    app.logger.error(f"Database error in aidorkadd: {str(db_error)}")
                    return jsonify({'error': 'A database error occurred'}), 500

    except BadRequest as e:
        app.logger.warning(f"Bad request in aidorkadd: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except json.JSONDecodeError:
        app.logger.warning("Invalid JSON data received in aidorkadd")
        return jsonify({'error': 'Invalid JSON data'}), 400
    except Exception as e:
        app.logger.error(f"An unexpected error occurred in aidorkadd: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

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