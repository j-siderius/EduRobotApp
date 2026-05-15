from machine import Pin, PWM

class Servo:
    PWM_FREQUENCY = 50
    MIN_PULSE = 500
    MAX_PULSE = 2500
    MAX_ANGLE = 180
    
    def __init__(self, pin: int) -> None:
        self.pin = Pin(pin, Pin.OUT)
        
        self.servo = PWM(self.pin, freq=self.PWM_FREQUENCY)
        
    @staticmethod
    def _map(value: int, fromLow: int, fromHigh: int, toLow: int, toHigh: int) -> int:
        return int((value - fromLow) * (toHigh - toLow) / (fromHigh - fromLow) + toLow)

    def setRotation(self, angle: int) -> None:
        mappedAngle = self._map(angle, 0, self.MAX_ANGLE, self.MIN_PULSE, self.MAX_PULSE)
        
        self.servo.duty_ns(mappedAngle*1000)
    
    def setMiddle(self) -> None:
        self.setRotation(90)