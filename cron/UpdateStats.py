import pandas as pd
import requests
from io import StringIO
from datetime import datetime, timedelta
import psycopg2
from psycopg2 import sql
from functools import reduce
from dotenv import load_dotenv
import os
import json

load_dotenv()

Postgres = json.loads(os.getenv('PostgreSQLConnectionParams'))

StartDate = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')
EndDate = datetime.today().strftime('%Y-%m-%d')

def GetTorRelayUsersCount():
    # https://metrics.torproject.org/userstats-relay-country.html
    url = f"https://metrics.torproject.org/userstats-relay-country.csv?start={StartDate}&end={EndDate}&country=all&events=off"
    response = requests.get(url).text
    cleaned_response = "\n".join([line for line in response.splitlines() if not line.startswith('#')])
    data = StringIO(cleaned_response)
    df = pd.read_csv(data)
    df = df[['date', 'users']]
    df = df.rename(columns={'date': 'Date', 'users': 'TorRelayUsers'})
    df = df.ffill()
    return df

def GetTorBridgeUsersCount():
    # https://metrics.torproject.org/userstats-relay-country.html
    url = f"https://metrics.torproject.org/userstats-bridge-country.csv?start={StartDate}&end={EndDate}&country=all"
    response = requests.get(url).text
    cleaned_response = "\n".join([line for line in response.splitlines() if not line.startswith('#')])
    data = StringIO(cleaned_response)
    df = pd.read_csv(data)
    df = df[['date', 'users']]
    df = df.rename(columns={'date': 'Date', 'users': 'TorBridgeUsers'})
    df = df.ffill()
    return df

def GetOnionSiteCount():
    # https://metrics.torproject.org/hidserv-dir-v3-onions-seen.html
    url = f"https://metrics.torproject.org/hidserv-dir-v3-onions-seen.csv?start={StartDate}&end={EndDate}"
    FilteredData = "\n".join([line for line in requests.get(url).text.splitlines() if line and not line.startswith("#")])
    df = pd.read_csv(StringIO(FilteredData))
    df = df[['date', 'onions']]
    df = df.rename(columns={'date': 'Date', 'onions': 'OnionSites'})
    df = df.ffill()
    return df

def GetOnionServiceBandwidth():
    # https://metrics.torproject.org/hidserv-rend-v3-relayed-cells.html
    # Gbits/s
    url = f"https://metrics.torproject.org/hidserv-rend-v3-relayed-cells.csv?start={StartDate}&end={EndDate}"
    FilteredData = "\n".join([line for line in requests.get(url).text.splitlines() if line and not line.startswith("#")])
    df = pd.read_csv(StringIO(FilteredData))
    df = df[['date', 'relayed']]
    df = df.rename(columns={'date': 'Date', 'relayed': 'OnionServiceBandwidth'})
    df = df.ffill()
    return df

def GetTorNetworkBandwidth():
    # https://metrics.torproject.org/bandwidth.html
    url = f"https://metrics.torproject.org/bandwidth.csv?start={StartDate}&end={EndDate}"
    response = requests.get(url).text
    cleaned_response = "\n".join([line for line in response.splitlines() if not line.startswith('#')])
    data = StringIO(cleaned_response)
    df = pd.read_csv(data)
    df = df.rename(columns={'date': 'Date', 'advbw': 'TorNetworkAdvertisedBandwidth', 'bwhist': 'TorNetworkConsumedBandwidth'})
    df = df.ffill()
    return df

df_relay_users = GetTorRelayUsersCount()
df_bridge_users = GetTorBridgeUsersCount()
df_onion_sites = GetOnionSiteCount()
df_onion_bandwidth = GetOnionServiceBandwidth()
df_tor_bandwidth = GetTorNetworkBandwidth()

dfs = [df_relay_users, df_bridge_users, df_onion_sites, df_onion_bandwidth, df_tor_bandwidth]
df_combined = reduce(lambda left, right: pd.merge(left, right, on='Date', how='outer'), dfs)
df_combined = df_combined.ffill().bfill().sort_values(by='Date', ascending=False)
df_combined['Date'] = pd.to_datetime(df_combined['Date'])

try:
    with psycopg2.connect(**Postgres) as conn:
        with conn.cursor() as cursor:
            for index, row in df_combined.iterrows():
                insert_query = sql.SQL("""
                    INSERT INTO TorMetrics (date, TorRelayUsers, TorBridgeUsers, OnionSites, OnionServiceBandwidth, TorNetworkAdvertisedBandwidth, TorNetworkConsumedBandwidth)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (date) DO UPDATE SET
                        TorRelayUsers = EXCLUDED.TorRelayUsers,
                        TorBridgeUsers = EXCLUDED.TorBridgeUsers,
                        OnionSites = EXCLUDED.OnionSites,
                        OnionServiceBandwidth = EXCLUDED.OnionServiceBandwidth,
                        TorNetworkAdvertisedBandwidth = EXCLUDED.TorNetworkAdvertisedBandwidth,
                        TorNetworkConsumedBandwidth = EXCLUDED.TorNetworkConsumedBandwidth;
                """)
                
                cursor.execute(insert_query, (
                    row['Date'].date(),
                    row['TorRelayUsers'],
                    row['TorBridgeUsers'],
                    row['OnionSites'],
                    row['OnionServiceBandwidth'],
                    row['TorNetworkAdvertisedBandwidth'],
                    row['TorNetworkConsumedBandwidth']
                ))

        conn.commit()
    print("Data has been added/updated in the TorMetrics table.")
except Exception as e:
    print(f"An error occurred: {e}")