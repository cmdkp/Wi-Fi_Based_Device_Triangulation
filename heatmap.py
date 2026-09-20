import requests
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

# --- CONFIG ---
KISMET_URL = "http://localhost:2501"
USER, PASS = "kali", "kali"

# Setup Polar Plot
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(8, 8))
ax.set_ylim(-100, -20)  # RSSI range: -100 (weak) to -20 (strong)
ax.set_theta_zero_location("N")
ax.set_yticklabels([]) # Hide the radial numbers for a cleaner look

# Store device positions to prevent flickering
device_angles = {} 

def get_all_devices():
    try:
        # Fetch all devices from the Kismet 'all' view
        url = f"{KISMET_URL}/devices/views/all/devices.json"
        response = requests.get(url, auth=(USER, PASS), timeout=0.5)
        devices = response.json()
        
        active_list = []
        for d in devices:
            # Extract signal and identity
            base_sig = d.get('kismet.device.base.signal', {})
            rssi = base_sig.get('kismet.common.signal.last_signal', -100)
            
            # Filter out dead signals or noise
            if rssi > -100 and rssi != 0:
                mac = d.get('kismet.device.base.macaddr', 'Unknown')
                name = d.get('kismet.device.base.commonname', 'Unknown')
                active_list.append({'mac': mac, 'name': name, 'rssi': rssi})
        
        # Sort by strength (Top 10)
        active_list.sort(key=lambda x: x['rssi'], reverse=True)
        return active_list[:10]
    except Exception as e:
        return []

def update(frame):
    ax.clear()
    ax.set_ylim(-100, -20)
    ax.set_theta_zero_location("N")
    ax.set_title("Kismet Live RF Proximity Radar\n(Center = Strongest/Closest)", pad=20)

    top_devices = get_all_devices()
    
    for d in top_devices:
        # Assign a fixed angle to each MAC so they don't jump around the circle
        if d['mac'] not in device_angles:
            device_angles[d['mac']] = np.random.uniform(0, 2 * np.pi)
        
        angle = device_angles[d['mac']]
        rssi = d['rssi']
        
        # Determine color based on "heat"
        if rssi > -45:
            color = 'red'    # Dangerously close
        elif rssi > -65:
            color = 'orange' # Nearby
        else:
            color = 'blue'   # Distant
            
        # Plot the "blob"
        ax.scatter(angle, rssi, c=color, s=200, alpha=0.7, edgecolors='white')
        
        # Label the blob with Device Name/MAC
        label = f"{d['name']}\n{rssi}dBm"
        ax.text(angle, rssi + 5, label, fontsize=8, ha='center', va='bottom')

# Update every 200ms
ani = FuncAnimation(fig, update, interval=200, cache_frame_data=False)
plt.show()
