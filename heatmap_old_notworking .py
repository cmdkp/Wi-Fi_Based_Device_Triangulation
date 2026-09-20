import requests
from requests.auth import HTTPBasicAuth
import time
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIG ---
USER, PASS = "kali", "kali"
URL = "http://localhost:2501/devices/last-time/0/devices.json"

# 3m x 2m Room (0.5m steps = 6 columns, 4 rows)
rows, cols = 4, 6 
grid = np.full((rows, cols), -100.0)

def get_best_signal():
    try:
        # Use a timeout of 1s to keep the script snappy
        r = requests.get(URL, auth=HTTPBasicAuth(USER, PASS), timeout=1)
        if r.status_code == 200:
            devices = r.json()
            # Extract last_signal from all active devices
            sigs = [d.get('kismet.device.base.signal', {}).get('kismet.common.signal.last_signal', -50) for d in devices]
            valid = [s for s in sigs if s > -50]
            return max(valid) if valid else -50
        return -50
    except:
        return -50

# --- SETUP PLOT ---
plt.ion()
fig, ax = plt.subplots(figsize=(7, 5))
# interpolation='gaussian' makes the blocks blend like a real cloud
im = ax.imshow(grid, cmap='magma', vmin=-85, vmax=-50, origin='lower', interpolation='gaussian')
plt.colorbar(im, label='Signal Intensity')

print(f"STARTING 3x2m SCAN ({rows*cols} points total)")

try:
    for x in range(cols):
        y_range = range(rows) if x % 2 == 0 else range(rows - 1, -1, -1)
        for y in y_range:
            plt.title(f"Position: {x*0.5}m, {y*0.5}m | Scanning...")
            
            # FAST SENSITIVITY: 2 quick samples instead of 3 long ones
            s1 = get_best_signal()
            time.sleep(0.5)
            s2 = get_best_signal()
            
            grid[y, x] = (s1 + s2) / 2
            
            # Refresh Visuals
            im.set_data(grid)
            plt.draw()
            plt.pause(0.1)
            
    print("DONE! Saving map to room_scan.png")
    plt.savefig('room_scan.png')
    plt.ioff()
    plt.show()

except KeyboardInterrupt:
    plt.show()
