from machine import Pin
import micropython


class Encoder:
    def __init__(self, pinA: int, pinB: int) -> None:
        # Inclusion of emergency Exception buffer as per https://docs.micropython.org/en/latest/reference/isr_rules.html#the-emergency-exception-buffer
        micropython.alloc_emergency_exception_buf(100)

        self.count = 0
        self.previousCount = 0

        self.pinA = Pin(pinA, Pin.IN)
        self.pinB = Pin(pinB, Pin.IN)
        self.pinA.irq(self._encoder_interrupt,
                      Pin.IRQ_FALLING or Pin.IRQ_RISING, hard=True)

    def _encoder_interrupt(self, pin) -> None:
        if self.pinA.value() == self.pinB.value():
            self.count += 1
        else:
            self.count -= 1

    def getCount(self) -> int:
        return self.count

    def getCountSinceLastCount(self) -> int:
        difference = self.count - self.previousCount
        self.previousCount = self.count
        return difference
