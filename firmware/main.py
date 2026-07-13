import config
from connectivity import WifiManager, ProvisioningServer, WebSocketServer
from message_manager import MessageManager

from cliff import CliffManager
from max17043 import max1704x
from servo import Servo
from motor import MotorManager
from ws2812b import WS2812B
from ssd1306 import DisplayManager
from vl53l1x import DistanceManager
from temperature import Temperature

import asyncio
from machine import Pin, I2C

async def main():
    wifi_manager = WifiManager()

    i2c = I2C(0, scl=Pin(config.PIN_I2C_SCL),sda=Pin(config.PIN_I2C_SDA), freq=400000)
        
    display = DisplayManager(i2c)
    
    if not wifi_manager.is_configured() or not wifi_manager.connect_sta():
        server = ProvisioningServer(wifi_manager)
        print("Starting provisioning server...")
        display.updateStatus(wifi_status="ap", ip_addr=self.ap_if.ifconfig()[0])
        await server.start()  # prevent further setup by awaiting here until restart
    else:
        
        message_manager = MessageManager()
        
        server = WebSocketServer(wifi_manager, message_manager)
        print(f"Starting WebSocket server on ws://{wifi_manager.get_staip()}/")
        display.updateStatus(wifi_status="connected", ip_addr=wifi_manager.get_staip())
        
        serverTask = asyncio.create_task(server.start())
        
        cliffs = CliffManager(config.PIN_CLIFF1, config.PIN_CLIFF2, config.PIN_CLIFF3)
        
        servo1 = Servo(config.PIN_SERVO1)
        servo2 = Servo(config.PIN_SERVO2)
        servo3 = Servo(config.PIN_SERVO3)
        
        motors = MotorManager(
            config.PIN_MOTOR11, config.PIN_MOTOR12, config.PIN_ENCODER11, config.PIN_ENCODER12,
            config.PIN_MOTOR21, config.PIN_MOTOR22, config.PIN_ENCODER21, config.PIN_ENCODER22,
            config.PIN_MOTOR31, config.PIN_MOTOR32, config.PIN_ENCODER31, config.PIN_ENCODER32
        )
        
        led1 = WS2812B(config.PIN_LED1)
        led2 = WS2812B(config.PIN_LED2)
        
        temperature = Temperature()
        
        fuelgauge = max1704x(i2c)
        fuelgauge.quickStart()
        
        distance = DistanceManager(i2c)
        
        # Decoding messages to function callbacks
        message_manager.add_message(['motors', 'move'], motors.move_to)
        message_manager.add_message(['motors', 'rotate'], motors.rotate)
        message_manager.add_message(['motors', 'stop'], motors.stop)
        # TODO: add functions that are currently missing
        # message_manager.add_message(['servos', 'move'], )
        # message_manager.add_message(['servos', 'grip'], )
        message_manager.add_message(['leds', 'one'], led1.setFullColor)
        message_manager.add_message(['leds', 'two'], led2.setFullColor)
        
        # polling all sensors
        temperature_update = asyncio.create_task(temperature.polling(server.messageBroadcast))
        front_distance_update = asyncio.create_task(distance.polling(server.messageBroadcast))
        # compass_update = asyncio.create_task(?.polling(server.messageBroadcast))
        cliff_update = asyncio.create_task(cliffs.polling(server.messageBroadcast))
        battery_update = asyncio.create_task(fuelgauge.polling(server.messageBroadcast))
        motor_position_update = asyncio.create_task(motors.polling(server.messageBroadcast))
        
        await serverTask

asyncio.run(main())
