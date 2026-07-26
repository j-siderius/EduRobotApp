from machine import Pin, PWM      
import micropython
import math, time, asyncio


class Motor:
    PWM_FREQUENCY = 50000
    MAX_SPEED = 1
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


class Encoder:        
    def __init__(self, pinA: int, pinB: int) -> None:
        # Inclusion of emergency Exception buffer as per https://docs.micropython.org/en/latest/reference/isr_rules.html#the-emergency-exception-buffer
        micropython.alloc_emergency_exception_buf(100)

        self._count = 0
        self._previousCount = 0

        self.pinA = Pin(pinA, Pin.IN)
        self.pinB = Pin(pinB, Pin.IN)
        self.pinA.irq(self._encoder_interrupt, Pin.IRQ_FALLING or Pin.IRQ_RISING, hard=True)

    def _encoder_interrupt(self, pin) -> None:
        if self.pinA.value() == self.pinB.value():
            self._count += 1
        else:
            self._count -= 1

    def getCount(self) -> int:
        return self._count

    def getCountSinceLastCount(self) -> int:
        difference = self._count - self._previousCount
        self._previousCount = self._count
        return difference


class MotorManager:
    # wheel variables
    PULSES_PER_ROTATION = 7
    GEAR_RATIO = 21  # TODO: double-check these gear ratio values
    WHEEL_DIAMETER = 38.1 * 2  # in mm, return values also in mm
    BETWEEN_WHEEL_DISTANCE = 155  # in mm, between middle of omniwheels
    CIRCUMCIRCLE_RADIUS = ( BETWEEN_WHEEL_DISTANCE * math.sqrt(3) ) / 3
    
    def __init__(self, mot11, mot12, enc11, enc12, mot21, mot22, enc21, enc22, mot31, mot32, enc31, enc32):
        self.motors = [
            Motor(mot11, mot12),
            Motor(mot21, mot22),
            Motor(mot31, mot32)
            ]
        self.encoders = [
            Encoder(enc11, enc12),
            Encoder(enc21, enc22),
            Encoder(enc31, enc32)
            ]
        
        self.xPosition = 0
        self.yPosition = 0
    
    def _calculateMotorForces(self, angle: int, speed: float = 1.0):
        # angle = direction of intended travel in degrees, speed = <0.0 to 1.0>        
        # carthesian force calculation
        F_x = math.sin(math.radians(angle))
        F_y = math.cos(math.radians(angle))
        # print(f"{F_x=}, {F_y=}")
        
        # vector force calculation
        F_A = (1/3) * F_x + (math.sqrt(3)/3) * F_y
        F_B = (1/3) * F_x - (math.sqrt(3)/3) * F_y
        F_C = -(2/3) * F_x
        # print(f"{F_A=}, {F_B=}, {F_C=}")
        
        # relative scaling
        F_range = max(F_A, F_B, F_C) - min(F_A, F_B, F_C)
        F_Ar = F_A/F_range
        F_Br = F_B/F_range
        F_Cr = F_C/F_range
        F_rmax = max(abs(F_Ar), abs(F_Br), abs(F_Cr))
        F_rdiff = 1-F_rmax
        # print(f"{F_Ar=}, {F_Br=}, {F_Cr=},")
        # print(f"{F_range=}, {F_rmax=}, {F_rdiff=}")
        
        # scaling to match motor range -1 to 1
        F_As = 0 if abs(F_Ar) < 1e-7 else (F_Ar + F_rdiff if F_Ar > 0 else F_Ar - F_rdiff)
        F_Bs = 0 if abs(F_Br) < 1e-7 else (F_Br + F_rdiff if F_Br > 0 else F_Br - F_rdiff)
        F_Cs = 0 if abs(F_Cr) < 1e-7 else (F_Cr + F_rdiff if F_Cr > 0 else F_Cr - F_rdiff)
        # print(f"{F_As=}, {F_Bs=}, {F_Cs=}")
        
        # applying speed
        F_At = F_As * speed
        F_Bt = F_Bs * speed
        F_Ct = F_Cs * speed
        
        return F_At, F_Bt, F_Ct
    
    async def _moveMotor(self, motor, encoder, speed: float, distance: float):
        start = encoder.getCount()
        goal = (self.PULSES_PER_ROTATION * self.GEAR_RATIO) * (distance / self.WHEEL_DIAMETER)
        motor.setSpeed(speed)
        if speed > 0:
            while (encoder.getCount() - start) < goal:
                await asyncio.sleep_ms(1)
        else:
            while (encoder.getCount() - start) > goal:
                await asyncio.sleep_ms(1)
        motor.stop()
    
    async def move_to(self, x: int, y: int, speed: float = 0.5):
        self.xPosition += x
        self.yPosition += y
        
        # convert x,y to angle, distance
        distance = math.sqrt(( x**2 ) + ( y**2 ))
        angleDegrees = math.degrees(math.atan2(x, y)) % 360
        
        forces = self._calculateMotorForces(angleDegrees, 0.5)
        distances = [distance * f for f in forces]

        await asyncio.gather(
                self._moveMotor(self.motors[0], self.encoders[0], forces[0], distances[0]),
                self._moveMotor(self.motors[1], self.encoders[1], forces[1], distances[1]),
                self._moveMotor(self.motors[2], self.encoders[2], forces[2], distances[2])
            )
    
    async def rotate(self, angle_degrees: int, speed: float = 0.5):
        rotationDistance = (math.pi * self.CIRCUMCIRCLE_RADIUS) * ( angle_degrees / 360 )
        
        actualSpeed = speed if angle_degrees > 0 else -speed
        absRotationDistance = abs(rotationDistance)
        
        await asyncio.gather(
                self._moveMotor(self.motors[0], self.encoders[0], actualSpeed, absRotationDistance),
                self._moveMotor(self.motors[1], self.encoders[1], actualSpeed, absRotationDistance),
                self._moveMotor(self.motors[2], self.encoders[2], actualSpeed, absRotationDistance)
            )
        
    async def stop(self):
        for motor in self.motors:
            motor.stop()
        
    def getPosition(self) -> tuple[int, int]:
        return self.xPosition, self.yPosition
    
    async def polling(self, websocket_message_broadcast):
        while True:
            await asyncio.sleep(1/1)  # update rate at 1Hz
            await websocket_message_broadcast(f"/motors/position/{self.xPosition}/{self.yPosition}")
    

if __name__ == "__main__":
    import time
    
    # motor 1
    PIN_ENCODER11 = const(12)
    PIN_ENCODER12 = const(13)
    PIN_MOTOR11 = const(14)
    PIN_MOTOR12 = const(15)

    # motor 2
    PIN_ENCODER21 = const(8)
    PIN_ENCODER22 = const(9)
    PIN_MOTOR21 = const(10)
    PIN_MOTOR22 = const(11)

    # motor 3
    PIN_ENCODER31 = const(2)
    PIN_ENCODER32 = const(3)
    PIN_MOTOR31 = const(6)
    PIN_MOTOR32 = const(7)
    
    motorManager = MotorManager(
        PIN_MOTOR11, PIN_MOTOR12, PIN_ENCODER11, PIN_ENCODER12,
        PIN_MOTOR21, PIN_MOTOR22, PIN_ENCODER21, PIN_ENCODER22,
        PIN_MOTOR31, PIN_MOTOR32, PIN_ENCODER31, PIN_ENCODER32
    )
    
    asyncio.run(motorManager.move_to(100, 100, 0.75))
    time.sleep(1)
    asyncio.run(motorManager.rotate(90, 0.5))
    
    print(motorManager.getPosition())
