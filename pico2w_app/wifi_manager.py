import network
import utime

from credential_manager import wifi_credential_manager

class WifiManager:
    def __init__(self) -> None:
        self.wlan_sta = network.WLAN(network.STA_IF)
        self.wlan_ap = network.WLAN(network.AP_IF)
        self.ap_ssid = "RoboConfig"
        self.ap_password = "12345678"
        self.max_connection_attempts = 10
    
    def start_ap(self, ssid: str="RoboConfig", password: str="12345678") -> tuple[str, str, str, str]:
        try: 
            if not ssid:
                ssid = self.ap_ssid
            if not password:
                password = self.ap_password
                
            self.wlan_ap.config(essid=ssid, password=password)
            
            self.wlan_sta.active(False)
            self.wlan_ap.active(True)
            
            print(f"wifi_manager: WiFi AP started with SSID {ssid} and Password {password}, connect to {self.wlan_ap.ifconfig()[0]}")
            
            return self.wlan_ap.ifconfig()
        
        except Exception as e:
            print(f"wifi_manager: Start AP failed with Exception {e}")
            return "", "", "", ""
    
    def stop_ap(self) -> bool:
        try:
            self.wlan_ap.active(False)
            return True
        
        except Exception as e:
            print(f"wifi_manager: Stop AP failed with Exception {e}")
            return False
    
    def connect_to_saved_ap(self) -> bool:
        try:
            ssid, password = wifi_credential_manager.load_credentials()
            
            if ssid == "" or password == "":
                print(f"wifi_manager: No credentials were saved")
                return False
            
            self.wlan_ap.active(False)
            self.wlan_sta.active(True)
            self.wlan_sta.connect(ssid, password)
            
            connection_attempts = 0
            print(f"wifi_manager: Attempting connection to saved AP ", end='')
            while connection_attempts < self.max_connection_attempts:
                if self.wlan_sta.isconnected():
                    print("\nwifi_manager: Connected to the saved AP")
                    return True
                
                print('.', end='')
                utime.sleep(1)
                connection_attempts += 1
                
            print(f"\nwifi_manager: Could not connect to the saved AP")
            self.wlan_sta.active(False)
            return False
        
        except Exception as e:
            print(f"wifi_manager: Connect to saved AP failed with Exception {e}")
            return False
    
    def is_connected(self) -> bool:
        return self.wlan_sta.isconnected()
    