import requests
import json
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# login info
KISMET_URL = "http://localhost:2501"
USER, PASS = "kali", "kali"

# set up plot
fig, ax = plt.subplots(figsize=(14, 8), layout="constrained")
num_devices = 5

bars = ax.barh(range(num_devices), [0]*num_devices, left=-90, color='blue')
ax.set_xlim(-90, -10)
ax.set_xlabel('Signal Strength (RSSI dBm)')
ax.set_yticks(range(num_devices))
ax.set_yticklabels(['Scanning ...'] * num_devices)

def get_top_devices():
    try:
        # Get Kismet's current server time
        sys_url = f"{KISMET_URL}/system/status.json"
        sys_resp = requests.get(sys_url, auth=(USER, PASS), timeout=2)
        # Use a default if the field is missing
        kismet_time = sys_resp.json().get('kismet.system.timestamp.start_sec', time.time())

        url = f"{KISMET_URL}/devices/views/all/devices.json"
        response = requests.get(url, auth=(USER, PASS), timeout=2)
        devices = response.json()
        
        valid_devices = []
        total_clients = 0 
        
        for d in devices:
            # 1. Broaden Type Filter: Ignore APs, but keep everything else
            dev_type = str(d.get('kismet.device.base.type', '')).lower()
            if "ap" in dev_type or "bridge" in dev_type:
                continue
            
            # 2. Freshness Check
            last_time = d.get('kismet.device.base.last_time', 0)
            if kismet_time - last_time > 15: # Bumped to 15s for stability
                continue

            # 3. Flexible Signal Fetching
            # Checks multiple common field locations for the signal
            signal_data = d.get('kismet.device.base.signal', {})
            rssi = signal_data.get('kismet.common.signal.last_signal', 
                   signal_data.get('last_signal', -100))
            
            if rssi < 0 and rssi > -95: 
                total_clients += 1
                name = d.get('kismet.device.base.commonname', 
                       d.get('kismet.device.base.macaddr', 'Unknown'))
                mac = d.get('kismet.device.base.macaddr', '??:??')
                valid_devices.append({'name': f"{name}\n({mac})", "rssi": rssi})
        
        valid_devices.sort(key=lambda x: x['rssi'], reverse=True)
        return valid_devices[:num_devices][::-1], total_clients 
        
    except Exception as e:
        # This will tell you if the API actually failed (e.g., 401 Unauthorized)
        print(f"API Error: {e}")
        return [], 0
        
def update(frame):
    top_devices, total_count = get_top_devices()
    labels = []
    
    for i in range(num_devices):
        if i < len(top_devices):
            d = top_devices[i]
            bars[i].set_width(d['rssi'] - (-90))
            labels.append(d['name'])
            
            if d['rssi'] > -25:
                bars[i].set_color('#ff0000') 
            elif d['rssi'] > -40:
                bars[i].set_color('#ff9900') 
            else:
                bars[i].set_color('#0000ff') 
        else: 
            bars[i].set_width(0)
            labels.append("---")

    ax.set_yticklabels(labels)
    ax.set_title(f"WiFi Heatmap | Active Clients Found: {total_count}") 
    return bars

ani = animation.FuncAnimation(fig, update, interval=500, cache_frame_data=False)
plt.show()
