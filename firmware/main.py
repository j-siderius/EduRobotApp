import config

import utime
from machine import Pin, I2C

from motor import Motor
from servo import Servo
from encoder import Encoder
from ws2812b import WS2812B
from qmc5883l import QMC5883L
from ssd1306 import SSD1306_I2C

led = Pin(config.PIN_LED_BUILTIN, Pin.OUT)
led.on()
utime.sleep(1)
led.off()
utime.sleep(1)

# i2c = I2C(0, scl=Pin(config.PIN_I2C_SCL),
#           sda=Pin(config.PIN_I2C_SDA), freq=400000)
# print("I2C devices:", i2c.scan())

# compass = QMC5883L(i2c)
# print("Compass:", compass.read_scaled())

# oled = SSD1306_I2C(width=128, height=64, i2c=i2c)
# oled.fill(0)
# oled.text("Hello World test", 0, 0)
# oled.text("World Hello test", 0, 10)
# oled.text("Line 3 test 1234", 0, 20)
# oled.text("Line 4 test 4567", 0, 30)
# oled.text("Line 5 test 7890", 0, 40)
# oled.text("Line 6 test 0000", 0, 50)
# oled.show()

# encoder1 = Encoder(config.PIN_ENCODER11, config.PIN_ENCODER12)
# encoder2 = Encoder(config.PIN_ENCODER21, config.PIN_ENCODER22)
# encoder3 = Encoder(config.PIN_ENCODER31, config.PIN_ENCODER32)

# motor1 = Motor(config.PIN_MOTOR11, config.PIN_MOTOR12)
# motor2 = Motor(config.PIN_MOTOR21, config.PIN_MOTOR22)
# motor3 = Motor(config.PIN_MOTOR31, config.PIN_MOTOR32)

# print("Encoder 1:", encoder1.getCount())
# motor1.setSpeed(10)
# utime.sleep(1)
# motor1.stop()
# utime.sleep(1)
# print("Encoder 1 change:", encoder1.getCountSinceLastCount())
# print("Encoder 2:", encoder2.getCount())
# motor2.setSpeed(10)
# utime.sleep(1)
# motor2.stop()
# utime.sleep(1)
# print("Encoder 2 change:", encoder2.getCountSinceLastCount())
# print("Encoder 2:", encoder3.getCount())
# motor3.setSpeed(10)
# utime.sleep(1)
# motor3.stop()
# utime.sleep(1)
# print("Encoder 3 change:", encoder3.getCountSinceLastCount())

# servo = Servo(config.PIN_SERVO2)

# servo.setRotation(0)
# utime.sleep(1)
# servo.setRotation(60)
# utime.sleep(1)
# servo.setRotation(120)
# utime.sleep(1)
# servo.setMiddle()

# leds = WS2812B(config.PIN_LED)

# leds.setFullColor(leds.WHITE)
# print(leds.getPixelColor(1))
# utime.sleep(1)
# leds.blackout()

