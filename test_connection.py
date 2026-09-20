import requests
from requests.auth import HTTPBasicAuth

# Config
USER = "kali"
PASS = "kali"
# This path is the most stable for 2026 releases
URL = "http://localhost:2501/devices/last-time/0/devices.json"

def test_connection():
    try:
        print(f"Polling 2026 API at {URL}...")
        
        # 2026 Kismet requires specific headers for API stability
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'KismetHeatmapTool/1.0'
        }
        
        r = requests.get(URL, auth=HTTPBasicAuth(USER, PASS), headers=headers, timeout=5)
        
        if r.status_code == 200:
            devices = r.json()
            print(f"SUCCESS! Found {len(devices)} devices nearby.")
            
            for d in devices[:3]:
                # 2026 JSON Path: kismet.device.base.macaddr
                mac = d.get('kismet.device.base.macaddr', 'Unknown')
                
                # Signal Path: kismet.device.base.signal/kismet.common.signal.last_signal
                sig_data = d.get('kismet.device.base.signal', {})
                sig = sig_data.get('kismet.common.signal.last_signal', -100)
                
                print(f"Device: {mac} | Signal: {sig} dBm")
        else:
            print(f"FAILED. Status Code: {r.status_code}")
            if r.status_code == 404:
                print("Tip: If you are using a very new build, try changing the URL to:")
                print("http://localhost:2501/devices/views/all/devices.json")
                
    except Exception as e:
        print(f"Error: {e}")

test_connection()
