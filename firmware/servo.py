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
        
        
if __name__ == "__main__":
    import time
    
    # servos
    PIN_SERVO1 = const(20)
    PIN_SERVO2 = const(21)
    PIN_SERVO3 = const(22)


    servo1 = Servo(PIN_SERVO1)
    servo2 = Servo(PIN_SERVO2)
    servo3 = Servo(PIN_SERVO3)
    
    servo1.setRotation(0)
    time.sleep(1)
    servo1.setRotation(180)
    time.sleep(1)
    servo1.setMiddle()
    time.sleep(1)
    
    servo2.setRotation(0)
    time.sleep(1)
    servo2.setRotation(180)
    time.sleep(1)
    servo2.setMiddle()
    time.sleep(1)
    
    servo3.setRotation(0)
    time.sleep(1)
    servo3.setRotation(180)
    time.sleep(1)
    servo3.setMiddle()
    time.sleep(1)