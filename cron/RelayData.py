import requests
import json
import psycopg2
from psycopg2 import sql
import pytz
from datetime import datetime
from pymongo import MongoClient, UpdateOne
import pycountry
import os
from dotenv import load_dotenv

load_dotenv()

IPInfoAPI = os.getenv('IPInfoAPIKey')
Postgres = json.loads(os.getenv('PostgreSQLConnectionParams'))
MongoDB = os.getenv('MongoDBConnectionString')
MapboxAPI = os.getenv('MapboxAPIKey')

client = MongoClient(MongoDB)
db = client['oniontrovedb'] 

def CheckForUpdates():
    url = "https://onionoo.torproject.org/details"
    response = requests.get(url)
    RelaysDataJSON = json.loads(response.content.decode('utf-8'))
    RelaysPublished	= RelaysDataJSON["relays_published"]

    with psycopg2.connect(**Postgres) as conn:
        with conn.cursor() as cur:
            cur.execute(sql.SQL("SELECT * FROM TorMetricsMetaData"))
            rows = cur.fetchall()
            RelaysUpdated = next((row[1] for row in rows if row[0] == 'RelaysUpdated'), None)

            RelaysUpdated = pytz.timezone('Asia/Kolkata').localize(RelaysUpdated)
            RelaysPublished = datetime.strptime(RelaysPublished, "%Y-%m-%d %H:%M:%S")
            RelaysPublished = RelaysPublished.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata'))
            current_time = datetime.now(pytz.timezone('Asia/Kolkata'))

            if (current_time.date() > RelaysUpdated.date()) and (RelaysPublished > RelaysUpdated):                
                UpdateTorNodeData(RelaysDataJSON)
                cur.execute(sql.SQL("UPDATE TorMetricsMetaData SET value = %s WHERE key = %s"), (current_time, 'RelaysUpdated'))
                conn.commit()
                return True
            else:
                return False 
            
def UpdateTorNodeData(RelaysDataJSON):
    NewRelaysData = RelaysDataJSON["relays"]
    ExistingTorRelaysData = list(db.TorRelayData.find())
    ExistingFingerprints = {relay["fingerprint"]: relay for relay in ExistingTorRelaysData}
    NewFingerprints = {relay["fingerprint"] for relay in NewRelaysData}
   
    EntriesToBeAdded = [relay for relay in NewRelaysData if relay["fingerprint"] not in ExistingFingerprints]
    EntriesToBeRemoved = [relay for relay in ExistingTorRelaysData if relay["fingerprint"] not in NewFingerprints]
    EntriesToBeUpdated = [relay for relay in NewRelaysData if relay["fingerprint"] in ExistingFingerprints]
   
    print(f"Total new relays: {len(NewRelaysData)}")
    print(f"Existing relays: {len(ExistingTorRelaysData)}")
    print(f"Relays to be added: {len(EntriesToBeAdded)}")
    print(f"Relays to be removed: {len(EntriesToBeRemoved)}")
    print(f"Relays to be updated: {len(EntriesToBeUpdated)}")
   
    FingerprintsToRemove = [relay["fingerprint"] for relay in EntriesToBeRemoved]
    Deleted = db.TorRelayData.delete_many({"fingerprint": {"$in": FingerprintsToRemove}})
    print(f"Removed: {Deleted.deleted_count}")
   
    if EntriesToBeAdded:
        for relay in EntriesToBeAdded:
            relay["ip"] = relay["or_addresses"][0].split(":")[0]
            relay.pop('country', None)
            relay.pop('country_name', None)
            relay.pop('as', None)
            relay.pop('as_name', None)

        ip_list = list(set([relay["ip"] for relay in EntriesToBeAdded]))
        print("len ip:", len(ip_list))

        aggregated_data = {}
        for i in range(0, len(ip_list), 990):
            chunk = ip_list[i:i + 990]
            data = requests.post(
                f'https://ipinfo.io/batch?token={IPInfoAPI}',
                headers={'Content-Type': 'application/json'},
                data=json.dumps(chunk)
            ).json()
            aggregated_data.update(data)

        for relay in EntriesToBeAdded:
            ip = relay["ip"]
            if ip in aggregated_data:
                relay_info = aggregated_data[ip]
                relay["city"] = relay_info.get("city", "")
                relay["region"] = relay_info.get("region", "")
                relay["timezone"] = relay_info.get("timezone", "")
                country_code = relay_info.get("country", "")
                loc = relay_info.get("loc", "")
                relay["organization"] = relay_info.get("org", "")

                try:
                    country = pycountry.countries.get(alpha_2=country_code)
                    relay["country_name"] = str(country.name)
                except AttributeError:
                    relay["country_name"] = ""

                relay["longitude"], relay["latitude"] = loc.split(',')
                
                org_string = relay["organization"]
                parts = org_string.split(' ', 1)
                if len(parts) == 2 and parts[0].startswith('AS'):
                    relay["asn"] = parts[0]
                    relay["organization"] = parts[1]
                else:
                    relay["asn"] = ""
                    relay["organization"] = org_string

    for relay in EntriesToBeUpdated:
        existing_relay = ExistingFingerprints[relay["fingerprint"]]
        relay["ip"] = relay["or_addresses"][0].split(":")[0]
        
        for field in ["city", "region", "timezone", "country_name", "latitude", "longitude", "organization", "asn"]:
            if field in existing_relay:
                relay[field] = existing_relay[field]
        
        relay.pop('country', None)
        relay.pop('country_name', None)
        relay.pop('as', None)
        relay.pop('as_name', None)

    db.TorRelayData.create_index('fingerprint', unique=True)
    operations = []
    for relay in EntriesToBeAdded + EntriesToBeUpdated:
        operations.append(
            UpdateOne(
                {"fingerprint": relay["fingerprint"]},
                {"$set": relay},
                upsert=True
            )
        )
   
    if operations:
        result = db.TorRelayData.bulk_write(operations)
        print(f"Added: {result.upserted_count}")
        print(f"Modified: {result.modified_count}")

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

    with open('static/MapTorRelaysData.json', 'w') as json_file:
        json.dump(ExistingTorRelaysData, json_file, indent=4)

    TorRelaysDataTable = [
        {
            'ID': index + 1,
            'Name': relay.get('nickname'),
            'IP Address': relay.get('ip'),
            'City': relay.get('city'),
            'Country': relay.get('country_name'),
            'Running': str(relay.get('running')),
            'Consensus Weight': relay.get('consensus_weight'),
            'Guard Probability': relay.get('guard_probability'),
            'Middle Probability': relay.get('middle_probability'),
            'Exit Probability': relay.get('exit_probability'),
        }
        for index, relay in enumerate(db.TorRelayData.find({}, {
            'nickname': 1,
            'ip': 1,
            'city': 1,
            'country_name': 1,
            'running': 1,
            'consensus_weight': 1,
            'guard_probability': 1,
            'middle_probability': 1,
            'exit_probability': 1
        }))
    ]

    with open('static/TorRelaysDataTable.json', 'w') as json_file:
        json.dump(TorRelaysDataTable, json_file, indent=4)

print(CheckForUpdates())