from machine import Pin, I2C

# Motor pins
PIN_MOTOR1_1 = Pin(4, mode=Pin.OUT)
PIN_MOTOR1_2 = Pin(5, mode=Pin.OUT)
PIN_MOTOR2_1 = Pin(6, mode=Pin.OUT)
PIN_MOTOR2_2 = Pin(7, mode=Pin.OUT)
PIN_MOTOR3_1 = Pin(2, mode=Pin.OUT)
PIN_MOTOR3_2 = Pin(3, mode=Pin.OUT)

# I2C pins and object
PIN_SCL = Pin(12)
PIN_SDA = Pin(13)
OBJ_I2C = I2C(0, scl=PIN_SCL, sda=PIN_SDA, freq=400000)

# Servo pins
PIN_SERVO1 = Pin(15, mode=Pin.OUT)

# TODO: fix these assignments
# Random pins
PIN_8 = Pin(8)
PIN_9 = Pin(9)
PIN_10 = Pin(10)
PIN_11 = Pin(11)