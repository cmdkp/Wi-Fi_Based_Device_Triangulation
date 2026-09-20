import requests
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# --- CONFIG ---
KISMET_URL = "http://localhost:2501"
USER, PASS = "kali", "kali"  # Using your config

# Setup the Plot
fig, ax = plt.subplots(figsize=(10, 5))
# We will show the top 5 strongest signals
num_devices = 5
bars = ax.barh(range(num_devices), [-100]*num_devices, color='blue')
ax.set_xlim(-100, -20)
ax.set_xlabel('Signal Strength (RSSI dBm)')
ax.set_yticks(range(num_devices))
ax.set_yticklabels(['Scanning...'] * num_devices)

def get_top_devices():
    try:
        # Fetch devices seen in the last 10 seconds
        # Using the summary endpoint with field simplification for speed
        url = f"{KISMET_URL}/devices/views/all/devices.json"
        
        # 2026 Kismet supports basic auth or API keys
        response = requests.get(url, auth=(USER, PASS), timeout=2)
        devices = response.json()
        print(devices)
        
        # Filter for devices that have actual signal data
        valid_devices = []
        for d in devices:
            base = d.get('kismet.device.base.signal', {})
            rssi = base.get('kismet.common.signal.last_signal', -100)
            if rssi != 0: # Filter out null/0 readings
                name = d.get('kismet.device.base.commonname', 'Unknown')
                mac = d.get('kismet.device.base.macaddr', 'Unknown')
                valid_devices.append({'name': f"{name}\n({mac})", 'rssi': rssi})
        
        # Sort by RSSI (closest to 0 is strongest)
        valid_devices.sort(key=lambda x: x['rssi'], reverse=True)
        return valid_devices[:num_devices]
    except Exception as e:
        print(f"Error: {e}")
        return []

def update(frame):
    top_devices = get_top_devices()
    
    # Reset labels and bars
    labels = []
    for i in range(num_devices):
        if i < len(top_devices):
            d = top_devices[i]
            bars[i].set_width(d['rssi'])
            labels.append(d['name'])
            
            # Heatmap Logic: Closer = Hotter
            if d['rssi'] > -45:
                bars[i].set_color('#ff0000') # Hot Red
            elif d['rssi'] > -60:
                bars[i].set_color('#ff9900') # Orange
            else:
                bars[i].set_color('#0000ff') # Cold Blue
        else:
            bars[i].set_width(-100)
            labels.append("---")
            
    ax.set_yticklabels(labels)
    ax.set_title(f"Live WiFi Heatmap (Top {num_devices} Loudest Devices)")
    return bars

# Update every 500ms for that "live" feel
ani = animation.FuncAnimation(fig, update, interval=500, cache_frame_data=False)
plt.tight_layout()
plt.show()
