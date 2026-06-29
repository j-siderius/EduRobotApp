from machine import Pin
from neopixel import NeoPixel

class WS2812B:
    NUMBER_LEDS = 8
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    
    def __init__(self, pin: int) -> None:
        self.pin = Pin(pin, Pin.OUT)
        self.ws2812b = NeoPixel(self.pin, self.NUMBER_LEDS)
        
    def setFullColor(self, color: tuple[int, int, int]) -> None:
        self.ws2812b.fill(color)
        self.ws2812b.write()
        
    def blackout(self) -> None:
        self.setFullColor(self.BLACK)
    
    def setPixelColor(self, pixel: int, color: tuple[int, int, int]) -> None:
        self.ws2812b[pixel] = color
        self.ws2812b.write()
        
    def getPixelColor(self, pixel: int) -> tuple[int, int, int]:
        return self.ws2812b[pixel]