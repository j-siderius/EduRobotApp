from machine import Pin, ADC
import asyncio

# QRE1113 IR reflectance sensor

class Cliff:
    def __init__(self, pin: int, threshold: int = 8000) -> None:
        self.state = 0
        self.adc = ADC(Pin(pin))
        self.threshold = threshold
    
    def getRawValue(self) -> int:
        return self.adc.read_u16()

    def getValue(self) -> bool:
        return 1 if self.adc.read_u16() > self.threshold else 0
        
    def setThreshold(self, threshold: int):
        self.threshold = threshold
        
    def calibrate(self, color: str) -> int:
        if color == "WHITE":
            self.threshold = self.adc.read_u16 + 2000
        elif color == "BLACK":
            self.threshold = self.adc.read_u16 - 2000
        else:
            print("Unkown calibration color")
        return self.threshold
    
class CliffManager:
    def __init__(self, cliff1_pin, cliff2_pin, cliff3_pin):
        self.cliff1 = Cliff(cliff1_pin)
        self.cliff2 = Cliff(cliff2_pin)
        self.cliff3 = Cliff(cliff3_pin)
        
    def getCliffValues(self):
        return self.cliff1.getValue(), self.cliff2.getValue(), self.cliff3.getValue()
    
    async def polling(self, websocket_message_broadcast):
        while True:
            await asyncio.sleep(1/20)  # update rate at 20Hz
            cliffValues = self.getCliffValues()
            await websocket_message_broadcast(f"/cliff/{cliffValues[0]}/{cliffValues[1]}/{cliffValues[1]}")
         

if __name__ == "__main__":
    import time

    # cliff
    PIN_CLIFF1 = const(28)
    PIN_CLIFF2 = const(26)
    PIN_CLIFF3 = const(27)

    cliffs = CliffManager(PIN_CLIFF1, PIN_CLIFF2, PIN_CLIFF3)
    while True:
        print(f"Cliffs LtR: {cliffs.getCliffValues()}")
        time.sleep(0.1)
