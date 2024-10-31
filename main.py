import os
import json
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from module.mysql import connect_db, execute_query, read_query
from module.formula import calculate_distance, find_device_position, plot_beacons_and_devices

load_dotenv()

# Get Config
DB_Host = os.getenv("DB_Host", "localhost")
DB_User = os.getenv("DB_User", "root")
DB_Pass = os.getenv("DB_Password", None)
DB_Name = os.getenv("DB_Database", "test")

# Connect to Database
mydb = connect_db(DB_Host, DB_User, DB_Pass, DB_Name)

# Get Data Beacon
room_id = 1  # Get data based room id
query = f"""SELECT dv.name as name, dr.x as x, dr.y as y, log.data as data 
            FROM rooms as rm
            LEFT JOIN data_rooms as dr ON dr.room_id = rm.id
            LEFT JOIN devices as dv ON dr.mac_address = dv.mac_address
            LEFT JOIN (SELECT log.data_room_id, log.data, log.created_at 
                       FROM logs as log 
                       WHERE (log.data_room_id, log.created_at) IN 
                             (SELECT data_room_id, MAX(created_at) 
                              FROM logs 
                              GROUP BY data_room_id)) as log ON log.data_room_id = dr.id
            WHERE rm.id = {room_id}"""

# Preprocessing Data
data_raw = read_query(mydb, query)
data, labels = {}, []
for item in data_raw:
    data[item[0]] = {
        "pos": (item[1], item[2]),
        "logs": json.loads(item[3])
    }
    labels.append(item[0])

# Gather unique devices with their names or MAC addresses
devices = {}
for beacon in data.values():
    for log in beacon['logs']:
        device_name = log.get('name', log['mac-address'])
        devices[log['mac-address']] = device_name

# Calculate distances and find positions
device_positions = {}
initial_guess = np.mean([data[labels[0]]['pos'], data[labels[1]]['pos'], data[labels[2]]['pos'], data[labels[3]]['pos']], axis=0)
for mac, name in devices.items():
    distances = {}
    for beacon_name, beacon_data in data.items():
        for log in beacon_data['logs']:
            if log['mac-address'] == mac:
                distances[beacon_name] = calculate_distance(log['RSSI'])
                break
    device_position = find_device_position(data, labels, distances, initial_guess)
    device_positions[mac] = {
        'x': device_position[0],
        'y': device_position[1],
        'name': name,
        **{label: distances[label] for label in labels}
    }

# Result Position
for device in device_positions:
    print(f"{device_positions[device]['name']} : ({device_positions[device]['x']}, {device_positions[device]['y']})")
# Store Result Plot Position
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f'static/plots/{room_id}_{timestamp}.png'
plot_beacons_and_devices(data, labels, device_positions, filename)