import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.optimize import minimize

def calculate_distance(rssi, tx_power=-85, n=2):
    return 10 ** ((tx_power - rssi) / (10 * n))

def objective(params, A, B, C, D, d_a, d_b, d_c, d_d):
    x, y = params
    return ((x - A[0])**2 + (y - A[1])**2 - d_a**2)**2 + \
           ((x - B[0])**2 + (y - B[1])**2 - d_b**2)**2 + \
           ((x - C[0])**2 + (y - C[1])**2 - d_c**2)**2 + \
           ((x - D[0])**2 + (y - D[1])**2 - d_d**2)**2

def find_device_position(beacons, labels, distances, initial_guess):
    result = minimize(objective, initial_guess, args=(
        beacons[labels[0]]['pos'], beacons[labels[1]]['pos'],
        beacons[labels[2]]['pos'], beacons[labels[3]]['pos'],
        distances[labels[0]], distances[labels[1]], distances[labels[2]], distances[labels[3]]))
    return result.x

def plot_beacons_and_devices(beacons, labels, device_positions, filename):
    fig, ax = plt.subplots(figsize=(16,9))
    colors = ['r', 'g', 'b', 'y']
    color_index = 0

    for label in labels:
        beacon = beacons[label]
        ax.plot(*beacon['pos'], colors[color_index]+'o', label=f'Beacon {label}')
        ax.annotate(label, beacon['pos'], textcoords="offset points", xytext=(0,10), ha='center')
        for distance in device_positions.values():
            ax.add_patch(plt.Circle(beacon['pos'], distance[label], color=colors[color_index], fill=False))
        color_index = (color_index + 1) % len(colors)

    for mac, position in device_positions.items():
        ax.plot(position['x'], position['y'], 'kx', label=f'{position["name"]}')
        ax.annotate(f'{position["name"]}', (position['x'], position['y']), textcoords="offset points", xytext=(0,10), ha='center')

    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.grid(True)
    plt.axis('equal')
    
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def plot_no_devices(beacons, labels, filename):
    fig, ax = plt.subplots(figsize=(16,9))
    colors = ['r', 'g', 'b', 'y']
    color_index = 0

    for label in labels:
        beacon = beacons[label]
        ax.plot(*beacon['pos'], colors[color_index]+'o', label=f'Beacon {label}')
        ax.annotate(label, beacon['pos'], textcoords="offset points", xytext=(0,10), ha='center')

    ax.text(0.5, 0.5, 'No devices detected', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=20, color='red')
    
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.grid(True)
    plt.axis('equal')
    
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()