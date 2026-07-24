import os
import json
import time
import machine
import network
import asyncio
from microdot import Microdot, send_file
from microdot.websocket import with_websocket


class WifiManager:
    CONFIG_FILE = "wifi_config.json"
    AP_SSID = "HexaConfig"
    AP_PASSWORD = "12345678"

    def __init__(self):
        self.ssid = None
        self.password = None
        self.sta_if = network.WLAN(network.STA_IF)
        self.ap_if = network.WLAN(network.AP_IF)
        self.load_credentials()

    def load_credentials(self):
        try:
            with open(self.CONFIG_FILE, "r") as f:
                config = json.load(f)
                self.ssid = config.get("ssid")
                self.password = config.get("pwd")
        except (OSError, ValueError, KeyError):
            self.ssid = None
            self.password = None

    def save_credentials(self, ssid: str, password: str):
        config = {"ssid": ssid, "pwd": password}
        with open(self.CONFIG_FILE, "w") as f:
            json.dump(config, f)

    def is_configured(self) -> bool:
        return self.ssid is not None and self.password is not None
    
    def get_staip(self) -> str:
        if self.is_configured():
            return self.sta_if.ifconfig()[0]

    def connect_sta(self, max_attempts: int = 20) -> bool:
        self.sta_if.active(True)
        self.sta_if.connect(self.ssid, self.password)
        
        for _ in range(max_attempts):
            if self.sta_if.isconnected():
                print(f"Connected to WiFi. IP: {self.sta_if.ifconfig()[0]}")
                return True
            time.sleep(1)
        return False

    def start_ap(self):
        self.ap_if.config(essid=self.AP_SSID, password=self.AP_PASSWORD)
        self.ap_if.active(True)
        print(f"AP started. Connect to '{self.AP_SSID}' (PW: '{self.AP_PASSWORD}') and visit http://{self.ap_if.ifconfig()[0]}")


class ProvisioningServer:
    def __init__(self, wifi_manager: WifiManager):
        self.wifi_manager = wifi_manager
        self.app = Microdot()
        self._setup_routes()

    def _setup_routes(self):
        @self.app.route("/", methods=["GET", "POST"])
        async def handle_provisioning(request):
            if request.method == "POST":
                ssid = request.form.get("ssid")
                password = request.form.get("password")
                if ssid and password:
                    self.wifi_manager.save_credentials(ssid, password)
                    machine.reset()
                else:
                    return "Invalid credentials were entered", 400
            return send_file("provisioning.html")

    async def start(self):
        self.wifi_manager.start_ap()
        await self.app.start_server(port=80, debug=True)


class WebSocketServer:
    def __init__(self, wifi_manager: WifiManager, message_manager):
        self.wifi_manager = wifi_manager
        self.message_manager = message_manager
        self.app = Microdot()
        self.active_ws = set()
        self._setup_routes()
        
    async def messageBroadcast(self, message):
        for ws in self.active_ws.copy():
            try:
                await ws.send(message)
            except:
                print(f"Error sending to WS client {ws}")

    def _setup_routes(self):
        @self.app.route("/")
        @with_websocket
        async def handle_websocket(request, ws):
            print(f"WS client {request.client_addr[0]} connected")
            self.active_ws.add(ws)
            try:
                while True:
                    message = await ws.receive()
                    asyncio.create_task(self.message_manager.process_message(message))
                    
                    # print(f"Received: {message}")
                    # await ws.send(f"Echo: {message}")  # echo message
            except Exception as e:
                print(f"WebSocket error: {e}")
            finally:
                print(f"WS client {request.client_addr[0]} disconnected")
                self.active_ws.discard(ws)

    async def start(self):
        await self.app.start_server(port=80, debug=True)


if __name__ == "__main__":
    async def main():
        wifi_manager = WifiManager()
        
        if not wifi_manager.is_configured() or not wifi_manager.connect_sta():
            server = ProvisioningServer(wifi_manager)
            print("Starting provisioning server...")
            await server.start()
        else:
            server = WebSocketServer(wifi_manager, None)
            print(f"Starting WebSocket server on ws://{wifi_manager.get_staip()}/")
            # await server.start()
            serverTask = asyncio.create_task(server.start())
            await serverTask

    asyncio.run(main())
