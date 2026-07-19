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


import math

class ArmManager:
    ARM1_LENGTH = 43  # in mm
    ARM2_LENGTH = 38  # in mm

    def __init__(self, servoPin1: int, servoPin2: int, servoPin3: int) -> None:
        self.servo1 = Servo(servoPin1)  # base servo
        self.servo2 = Servo(servoPin2)  # joint servo
        self.servo3 = Servo(servoPin3)  # gripper servo

        self.servo3.setMiddle()
        self.gripping = False

    def _calculate2LinkArmInverseKinematics(self, x: int, y: int) -> tuple[int, int]:
        if x<0 or y<0:
            print("Target not within envelope")
            return None
        if (x**2 + y**2) > (self.ARM1_LENGTH + self.ARM2_LENGTH)**2:
            print("Target beyond maximum reach")
            return None
        if (x**2 + y**2) < (self.ARM1_LENGTH - self.ARM2_LENGTH)**2:
            print("Target too close to base")
            return None
        if (x**2 + y**2) == (self.ARM1_LENGTH + self.ARM2_LENGTH)**2:
            print("Arm fully extended")
        if (x**2 + y**2) == (self.ARM1_LENGTH - self.ARM2_LENGTH)**2:
            print("Arm fully folded")
        
        # Using formulas from https://www.firgelliauto.com/blogs/engineering-calculators/inverse-kinematics-calculator-2-link-and-3-link-robot-arms#simple-example and https://superglobalcalculator.com/calculators/robotics/inverse-kinematics/
        # Presumably elbow-up calculations
        theta2 = -math.acos((x**2 + y**2 - self.ARM1_LENGTH**2 - self.ARM2_LENGTH**2) / (2 * self.ARM1_LENGTH * self.ARM2_LENGTH))
        theta1 = math.atan2(y, x) - math.atan2(self.ARM2_LENGTH * math.sin(theta2), self.ARM1_LENGTH + self.ARM2_LENGTH * math.cos(theta2))
        
        # Include fix for servo zeroing difference in theta2
        return math.degrees(theta1), (math.degrees(theta2)+90)

    def moveTo(self, x: int, y: int) -> None:
        theta1, theta2 = self._calculate2LinkArmInverseKinematics(x, y)
        if not theta1 == None and not theta2 == None:
            self.servo1.setRotation(theta1)
            self.servo2.setRotation(theta2)

    def grip(self) -> None:
        if self.gripping:
            self.servo3.setMiddle()
            self.gripping = False
        else:
            self.servo3.setRotation(10)  # TODO: calibrate this value to properly close
            self.gripping = True

              
if __name__ == "__main__":
    import time
    from micropython import const
    
    # servos
    PIN_SERVO1 = const(20)
    PIN_SERVO2 = const(21)
    PIN_SERVO3 = const(22)

    arm = ArmManager(PIN_SERVO1, PIN_SERVO2, PIN_SERVO3)

    arm.grip()
    time.sleep(1)
    arm.moveTo(40, 40)
    time.sleep(1)
    arm.moveTo(80, 0)

    # servo1 = Servo(PIN_SERVO1)
    # servo2 = Servo(PIN_SERVO2)
    # servo3 = Servo(PIN_SERVO3)
    
    # servo1.setRotation(0)
    # time.sleep(1)
    # servo1.setRotation(180)
    # time.sleep(1)
    # servo1.setMiddle()
    # time.sleep(1)
    
    # servo2.setRotation(0)
    # time.sleep(1)
    # servo2.setRotation(180)
    # time.sleep(1)
    # servo2.setMiddle()
    # time.sleep(1)
    
    # servo3.setRotation(0)
    # time.sleep(1)
    # servo3.setRotation(180)
    # time.sleep(1)
    # servo3.setMiddle()
    # time.sleep(1)