from machine import Pin, PWM


class Motor:
    PWM_FREQUENCY = 50000
    MAX_SPEED = 100
    START_CYCLE = 40000
    MAX_CYCLE = 65535

    def __init__(self, pinA: int, pinB: int) -> None:
        self.pinA = Pin(pinA, Pin.OUT)
        self.pinB = Pin(pinB, Pin.OUT)

        self.motorA = PWM(self.pinA, freq=self.PWM_FREQUENCY)
        self.motorB = PWM(self.pinB, freq=self.PWM_FREQUENCY)

    @staticmethod
    def _map(value: int, fromLow: int, fromHigh: int, toLow: int, toHigh: int) -> int:
        return int((value - fromLow) * (toHigh - toLow) / (fromHigh - fromLow) + toLow)

    def setSpeed(self, speed: int) -> None:
        # Mapped value should always be positive
        mappedSpeed = self._map(abs(speed), 0, self.MAX_SPEED, self.START_CYCLE, self.MAX_CYCLE)

        # Slow Decay => modes explained: https://learn.adafruit.com/improve-brushed-dc-motor-performance/current-decay-mode
        if speed < 0:
            self.motorA.duty_u16(mappedSpeed)
            self.motorB.duty_u16(0)
        elif speed > 0:
            self.motorA.duty_u16(0)
            self.motorB.duty_u16(mappedSpeed)
        else:
            # both speed 0 means braking/stop
            self.motorA.duty_u16(0)
            self.motorB.duty_u16(0)

    def stop(self) -> None:
        self.setSpeed(0)
