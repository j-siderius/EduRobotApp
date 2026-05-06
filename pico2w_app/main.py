import asyncio

from wifi_manager import WifiManager
from captive_portal import start_captive_portal
from websocket_server import start_websocket_server


wifi_manager = WifiManager()

print(f"main: Starting WiFi configuration")

if wifi_manager.connect_to_saved_ap():
    asyncio.run(start_websocket_server())  
else:
    wifi_manager.start_ap()
    asyncio.run(start_captive_portal())