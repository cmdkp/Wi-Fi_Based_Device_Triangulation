import requests
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# login info
KISMET_URL = "http://localhost:2501"
USER, PASS = "kali", "kali"
BASELINE_MAC = "D2:3B:96:17:86:43"


device_registry = {} # Stores {MAC: "Emoji Number"}
emoji_pool = ["😂", "😭", "😎", "👻", "🤖", "🦊", "🍕", "🚀", "💎", "🔥", "🌈", "👽"]
next_id_number = 1

def get_unique_id(mac):
    global next_id_number
    if mac not in device_registry:
        # Cycle through emojis and pair with a number up to 50
        emoji = emoji_pool[len(device_registry) % len(emoji_pool)]
        device_registry[mac] = f"{emoji} {next_id_number}"
        next_id_number = (next_id_number % 50) + 1
    return device_registry[mac]

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
        url = f"{KISMET_URL}/devices/views/all/devices.json"
        response = requests.get(url, auth=(USER, PASS), timeout=2)
        devices = response.json()
        
        valid_devices = []
        my_phone = None
        
        for d in devices:
            base = d.get('kismet.device.base.signal', {})
            rssi = base.get('kismet.common.signal.last_signal', -100)
            
            if rssi != 0:
                mac = d.get('kismet.device.base.macaddr', 'Unknown')
                unique_id = get_unique_id(mac) # Get or Create the Emoji ID
                
                name = d.get('kismet.device.base.commonname', 'Unknown')
                # Use the Emoji ID in the label instead of just the MAC
                display_name = f"{unique_id}\n{name}"
                
                device_data = {'name': display_name, 'rssi': rssi, 'mac': mac}
                
                if mac.upper() == BASELINE_MAC:
                    my_phone = device_data
                else:
                    valid_devices.append(device_data)
        
        valid_devices.sort(key=lambda x: x['rssi'], reverse=True)
        
        final_list = []
        if my_phone:
            final_list.append(my_phone)
            final_list.extend(valid_devices[:num_devices-1])
        else:
            final_list = valid_devices[:num_devices]
            
        return final_list[::-1]
        
    except Exception as e:
        print(f"Error: {e}")
        return []
        
def update(frame):
    top_devices = get_top_devices()
    labels = []
    for i in range(num_devices):
        if i < len(top_devices):
            d = top_devices[i]
            bars[i].set_width(d['rssi'] - (-90))
            labels.append(d['name'])
            
            if d.get('mac', '').upper() == BASELINE_MAC:
                bars[i].set_color('#800080') # Baseline is Purple
            elif d['rssi'] > -45:
                bars[i].set_color('#ff0000') 
            elif d['rssi'] > -60:
                bars[i].set_color('#ff9900') 
            else:
                bars[i].set_color('#0000ff') 
        else: 
            bars[i].set_width(0)
            labels.append("---")

    ax.set_yticklabels(labels)
    ax.set_title(f"Live Wifi Heatmap | Tracked: {len(device_registry)} devices") 
    return bars

ani = animation.FuncAnimation(fig, update, interval=500, cache_frame_data=False)
plt.show()
