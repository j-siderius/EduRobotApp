#################### PINS ####################
from micropython import const

# uart
PIN_UART_TX = const(0)
PIN_UART_RX = const(1)

# i2c
PIN_I2C_SDA = const(4)
PIN_I2C_SCL = const(5)

# spi
PIN_SPI_MISO = const(16)
PIN_SPI_MOSI = const(19)
PIN_SPI_CLK = const(18)
PIN_SPI_CS1 = const(17)
PIN_SPI_CS2 = const(28)

# header
PIN_HEADER1 = const(18)
PIN_HEADER2 = const(19)
PIN_AHEADER1 = const(26)
PIN_AHEADER2 = const(27)

# cliff
PIN_CLIFF1 = const(28)
PIN_CLIFF2 = const(26)
PIN_CLIFF3 = const(27)

# servos
PIN_SERVO1 = const(20)
PIN_SERVO2 = const(21)
PIN_SERVO3 = const(22)

# leds
PIN_LED1 = const(16)
PIN_LED2 = const(17)
PIN_LED_BUILTIN = const("LED")  # Built-in LED via wireless module

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