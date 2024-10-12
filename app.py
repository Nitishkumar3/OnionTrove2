from dotenv import load_dotenv
import os
import json
import psycopg2
from pymongo import MongoClient

load_dotenv()

IPInfoAPI = os.getenv('IPInfoAPIKey')
Postgres = json.loads(os.getenv('PostgreSQLConnectionParams'))
MongoDB = os.getenv('MongoDBConnectionString')

