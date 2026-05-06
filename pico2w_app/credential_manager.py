import json

_CONFIG_STORAGE = "wifi_config.json"

class CredentialManager:
    def __init__(self) -> None:
        self.configfile = _CONFIG_STORAGE

    def save_credentials(self, ssid: str, password: str) -> bool:
        try:
            with open(self.configfile, "w") as f:
                config = {
                    "ssid": ssid,
                    "pwd": password
                }
                json.dump(config, f)
            return True
        
        except Exception as e:
            print(f"credential_manager: Saving credentials failed with Exception {e}")
            return False
        
    def load_credentials(self) -> tuple[str, str]:
        try:
            with open(self.configfile) as f:
                c = json.load(f)
                ssid = c['ssid']
                password = c['pwd']                
                return ssid, password
        
        except Exception as e:
            print(f"credential_manager: Loading credentials failed with Exception {e}")
            return "", ""
        
    def clear_credentials(self) -> bool:
        try:
            with open(self.configfile, "w") as f:
                json.dump("{}", f)
            return True
        
        except Exception as e:
            print(f"credential_manager: Clearning credentials failed with Exception {e}")
            return False
        
wifi_credential_manager = CredentialManager()