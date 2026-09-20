import requests
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# login info
KISMET_URL = "http://localhost:2501"
USER, PASS = "kali", "kali"

# set up plot
# Using layout="constrained" to stop the labels from cutting off
fig, ax = plt.subplots(figsize=(14, 8), layout="constrained")

num_devices = 5 # show top 5 signals

# Start bars at -90 so that typical signals (-60 to -80) are visible
bars = ax.barh(range(num_devices), [0]*num_devices, left=-90, color='blue')
ax.set_xlim(-90, -10)
ax.set_xlabel('Signal Strength (RSSI dBm)')
ax.set_yticks(range(num_devices))
ax.set_yticklabels(['Scanning ...'] * num_devices)

def get_top_devices():
    try: # to fetch devices seen in last 10 seconds
        # using the summery endpoing with field simplification for speed
        url = f"{KISMET_URL}/devices/views/all/devices.json"
        
        # 2026 version of Kismet supports basic auth or api keys
        response = requests.get(url, auth=(USER, PASS), timeout=2)
        devices = response.json()
        print(json.dumps(devices, indent=4) + "\n\n")
        
        # filter for devices that have actual signal data
        valid_devices = []
        for d in devices:
            base = d.get('kismet.device.base.signal', {})
            rssi = base.get('kismet.common.signal.last_signal', -100)
            if rssi != 0:  # filter out null/0 readings
                name=d.get('kismet.device.base.commonname', 'Unknown')
                mac = d.get('kismet.device.base.macaddr', 'Unknown')
                valid_devices.append({'name': f"{name}\n({mac})", "rssi": rssi})
        
        #sort devices by RSSI (closest to 0 is strongest)
        valid_devices.sort(key=lambda x: x['rssi'], reverse=True)
        
        # Take top 5 and reverse them so strongest is at the top of the chart
        top5 = valid_devices[:num_devices]
        return top5[::-1] 
        
    except Exception as e:
        print(f"Error: {e}")
        return []
        
def update(frame):
    top_devices = get_top_devices()
    
    # reset labels and bars
    labels = []
    for i in range(num_devices):
        if i < len(top_devices):
            d = top_devices[i]
            # Width is the distance from our left limit (-90) to the RSSI
            bars[i].set_width(d['rssi'] - (-90))
            labels.append(d['name'])
            
            # heatmap logic: closer = hotter
            if d['rssi'] > -45:
                bars[i].set_color('#ff0000') # red
            elif d['rssi'] > -60:
                bars[i].set_color('#ff9900') # orange
            else:
                bars[i].set_color('#0000ff') # blue
            
        else: 
            bars[i].set_width(0)
            labels.append("---")

    ax.set_yticklabels(labels)
    ax.set_title(f"Live Wifi Heatmap (Top {num_devices} Loudest Devices)") 
    
    return bars
    
 
#update every 500ms for "live" map
ani = animation.FuncAnimation(fig, update, interval=500, cache_frame_data=False)
plt.show()
