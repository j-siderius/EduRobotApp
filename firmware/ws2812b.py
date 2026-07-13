from machine import Pin
from neopixel import NeoPixel

class WS2812B:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    
    def __init__(self, pin: int) -> None:
        self.pin = Pin(pin, Pin.OUT)
        self.ws2812b = NeoPixel(self.pin, 1)
        self.colors = [
            self.WHITE,
            self.BLACK,
            self.RED,
            self.GREEN,
            self.BLUE
            ]
        
    async def setFullColor(self, *args):
        """
        Set full LED color. Accepts either:
        - A single tuple/list: setFullColor((255, 0, 0))
        - Three separate values: setFullColor(255, 0, 0)
        """
        if len(args) == 1 and isinstance(args[0], (tuple, list)) and len(args[0]) == 3:
            r, g, b = args[0]
        elif len(args) == 3:
            r, g, b = args
            
        self.ws2812b.fill((r, g, b))
        self.ws2812b.write()                
        
    def blackout(self) -> None:
        self.setFullColor(self.BLACK)
        
    def getPixelColor(self, pixel: int) -> tuple[int, int, int]:
        return self.ws2812b[pixel]
    

if __name__ == "__main__":
    import time

    # leds
    PIN_LED1 = const(16)
    PIN_LED2 = const(17)

    led1 = WS2812B(PIN_LED1)
    led2 = WS2812B(PIN_LED2)

    led1.setFullColor(led1.WHITE)
    led2.setFullColor(led2.GREEN)

    time.sleep(2)

    led1.blackout()
    led2.blackout()
