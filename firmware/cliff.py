from machine import Pin
import micropython

class Cliff:
    def __init__(self, pin: int) -> None:
        # Inclusion of emergency Exception buffer as per https://docs.micropython.org/en/latest/reference/isr_rules.html#the-emergency-exception-buffer
        micropython.alloc_emergency_exception_buf(100)
        
        self.state = 0
        self.pin = Pin(pin, Pin.IN)
        self.pin.irq(self._cliff_interrupt, Pin.IRQ_FALLING or Pin.IRQ_RISING, hard=True)
        
    def _cliff_interrupt(self, pin) -> None:
        self.state = self.pin.value()
    
    def getStatus(self) -> bool:
        return bool(self.state)