from dotenv import load_dotenv
import os
import json
import psycopg2
from pymongo import MongoClient

load_dotenv()

Postgres = json.loads(os.getenv('PostgreSQLConnectionParams'))
MongoDB = os.getenv('MongoDBConnectionString')

def TestPostgresConnection(params):
    try:
        connection = psycopg2.connect(
            dbname=params['dbname'],
            user=params['user'],
            password=params['password'],
            host=params['host'],
            port=params['port']
        )
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"PostgreSQL connected successfully. Database version: {db_version}")
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Failed to connect to PostgreSQL: {e}")

def TestMongoDBConnection(connection_string):
    try:
        client = MongoClient(connection_string)
        server_info = client.server_info()
        print(f"MongoDB connected successfully. Server version: {server_info['version']}")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

TestPostgresConnection(Postgres)
TestMongoDBConnection(MongoDB)