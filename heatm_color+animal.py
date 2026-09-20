import requests
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# login info
KISMET_URL = "http://localhost:2501"
USER, PASS = "kali", "kali"
BASELINE_MAC = "D2:3B:96:17:86:43"

# --- COLOR-ANIMAL-NUMBER REGISTRY ---
device_registry = {} 
color_map = {
    "Red": "#FF0000", "Blue": "#0000FF", "Green": "#008000", 
    "Gold": "#DAA520", "Orange": "#FFA500", "Purple": "#800080", 
    "Pink": "#FF1493", "Cyan": "#00CED1", "Brown": "#8B4513", "Gray": "#696969"
}
animals = ["Panda", "Tiger", "Falcon", "Shark", "Fox", "Owl", "Rabbit", "Deer", "Wolf", "Lynx"]

def get_unique_id(mac, kismet_name):
    # If the device already has a real name, use it and default to Black text
    if kismet_name != "Unknown":
        return {"label": kismet_name, "color": "#000000"} # Black for known names
    
    # Otherwise, assign a unique Color-Animal-Number
    if mac not in device_registry:
        count = len(device_registry)
        c_name = list(color_map.keys())[count % len(color_map)]
        a_name = animals[(count // len(color_map)) % len(animals)]
        u_num = (count % 50) + 1
        
        device_registry[mac] = {
            "label": f"{c_name} {a_name} {u_num}",
            "color": color_map[c_name]
        }
    return device_registry[mac]

# set up plot
fig, ax = plt.subplots(figsize=(14, 8), layout="constrained")
num_devices = 5 
bars = ax.barh(range(num_devices), [0]*num_devices, left=-90)
ax.set_xlim(-90, -10)
ax.set_xlabel('Signal Strength (RSSI dBm)')
ax.set_yticks(range(num_devices))
ax.set_yticklabels([]) # Custom drawing in update()

def get_top_devices():
    try:
        response = requests.get(f"{KISMET_URL}/devices/views/all/devices.json", auth=(USER, PASS), timeout=2)
        devices = response.json()
        
        valid_devices = []
        my_phone = None
        
        for d in devices:
            base = d.get('kismet.device.base.signal', {})
            rssi = base.get('kismet.common.signal.last_signal', -100)
            
            if rssi != 0:
                mac = d.get('kismet.device.base.macaddr', 'Unknown')
                k_name = d.get('kismet.device.base.commonname', 'Unknown')
                
                # Pass BOTH mac and kismet name to the generator
                info = get_unique_id(mac, k_name) 
                
                device_data = {
                    'display': f"{info['label']}\n({mac})", 
                    'rssi': rssi, 
                    'mac': mac, 
                    'text_color': info['color']
                }
                
                if mac.upper() == BASELINE_MAC:
                    my_phone = device_data
                else:
                    valid_devices.append(device_data)
        
        valid_devices.sort(key=lambda x: x['rssi'], reverse=True)
        final_list = (([my_phone] if my_phone else []) + valid_devices)[:num_devices]
        return final_list[::-1]
    except Exception as e:
        print(f"Error: {e}")
        return []

def update(frame):
    for txt in list(ax.texts):
        txt.remove()
        
    top_devices = get_top_devices()
    
    for i in range(num_devices):
        if i < len(top_devices):
            d = top_devices[i]
            bars[i].set_width(d['rssi'] - (-90))
            
            # Bar color (Heatmap)
            if d['rssi'] > -45: bars[i].set_color('#ff0000')
            elif d['rssi'] > -60: bars[i].set_color('#ff9900')
            else: bars[i].set_color('#0000ff')
            
            # Label color (Unique ID Color or Black for known names)
            ax.text(-91, i, d['display'], va='center', ha='right', 
                    color=d['text_color'], fontweight='bold', fontsize=10)
            
            if d.get('mac', '').upper() == BASELINE_MAC:
                bars[i].set_edgecolor('black')
                bars[i].set_linewidth(2)
            else:
                bars[i].set_linewidth(0)
        else:
            bars[i].set_width(0)
            
    return bars

ani = animation.FuncAnimation(fig, update, interval=500, cache_frame_data=False)
plt.show()
