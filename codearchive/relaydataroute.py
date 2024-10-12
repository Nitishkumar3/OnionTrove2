# @app.route('/relays', methods=['GET'])
# def get_existing_tor_relays():
#     try:
#         ExistingTorRelaysData = [
#             {
#                 'fingerprint': relay.get('fingerprint'),
#                 'nickname': relay.get('nickname'),
#                 'latitude': relay.get('latitude'),
#                 'longitude': relay.get('longitude'),
#                 'city': relay.get('city'),
#                 'region': relay.get('region'),
#                 'country_name': relay.get('country_name'),
#             }
#             for relay in db.TorRelayData.find({}, {
#                 'fingerprint': 1,
#                 'nickname': 1,
#                 'latitude': 1,
#                 'longitude': 1,
#                 'city': 1,
#                 'region': 1,
#                 'country_name': 1
#             })
#         ]

#         return jsonify(ExistingTorRelaysData), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500