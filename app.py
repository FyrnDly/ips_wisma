import os
import json
import numpy as np
from flask import Flask, request, render_template, jsonify, make_response
from dotenv import load_dotenv
from module.mysql import connect_db, get_room_id
from module.formula import calculate_distance, find_device_position, plot_beacons_and_devices, plot_no_devices
from datetime import datetime

load_dotenv()

# Flask app initialization
app = Flask(__name__)

# Get Config APP
APP_URL = os.getenv("APP_URL", "localhost")
APP_PORT = os.getenv("APP_PORT", 80)
APP_DEBUG = os.getenv("APP_PORT", True)

# Get Config
DB_Host = os.getenv("DB_Host", "localhost")
DB_User = os.getenv("DB_User", "root")
DB_Pass = os.getenv("DB_Password", None)
DB_Name = os.getenv("DB_Database", "test")

# Connect to Database
mydb = connect_db(DB_Host, DB_User, DB_Pass, DB_Name)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plot', methods=['GET'])
def plot():
    room_id = request.args.get('room_id', type=int)
    data, labels = get_room_id(mydb, room_id)

    # Gather unique devices with their names or MAC addresses
    devices = {}
    for beacon in data.values():
        for log in beacon['logs']:
            device_name = log.get('name', log['mac-address'])
            devices[log['mac-address']] = device_name

    # Calculate distances and find positions
    device_positions = {}
    if devices:
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
    # Plot the data and save the plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plot_filename = f'static/plots/{room_id}_{timestamp}.png'
    
    if device_positions:
        plot_beacons_and_devices(data, labels, device_positions, plot_filename)
    else:
        plot_no_devices(data, labels, plot_filename)
    
    response = make_response(render_template('index.html', plot_url=plot_filename, device_positions=device_positions))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/positions', methods=['GET'])
def get_positions():
    room_id = request.args.get('room_id', type=int)
    data, labels = get_room_id(mydb, room_id)

    # Gather unique devices with their names or MAC addresses
    devices = {}
    for beacon in data.values():
        for log in beacon['logs']:
            device_name = log.get('name', log['mac-address'])
            devices[log['mac-address']] = device_name

    # Calculate distances and find positions
    device_positions = {}
    if devices:
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
    
    # Plot the data and save the plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plot_filename = f'static/plots/{room_id}_{timestamp}.png'
    
    if device_positions:
        plot_beacons_and_devices(data, labels, device_positions, plot_filename)
    else:
        plot_no_devices(data, labels, plot_filename)

    # Create response
    response = {
        'room_id': room_id,
        'device_positions': device_positions,
        'plot_url': plot_filename
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=APP_PORT, port=APP_DEBUG, host=APP_URL)