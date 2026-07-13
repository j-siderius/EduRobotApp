from machine import ADC
import asyncio

class Temperature:
    def __init__(self):
        self.temp = ADC(ADC.CORE_TEMP)
        
    def getTemperature(self):
        return 27 - ((self.temp.read_u16() * (3.3 / 65535.0)) - 0.706)/0.001721
    
    async def polling(self, websocket_message_broadcast):
        while True:
            await asyncio.sleep(1/1)  # update rate at 1Hz
            await websocket_message_broadcast(f"/temperature/{self.getTemperature()}")
            