from machine import PWM
from pinconfig import *

PWM_FREQUENCY = 50000
MIN_DUTY_CYCLE = 0
MIN_START_CYCLE = 40000  # Find this out specifically for the chosen motors
MAX_DUTY_CYCLE = 65535

motor1_1 = PWM(PIN_MOTOR1_1, freq=PWM_FREQUENCY)
motor1_2 = PWM(PIN_MOTOR1_2, freq=PWM_FREQUENCY)
motor2_1 = PWM(PIN_MOTOR2_1, freq=PWM_FREQUENCY)
motor2_2 = PWM(PIN_MOTOR2_2, freq=PWM_FREQUENCY)
motor3_1 = PWM(PIN_MOTOR3_1, freq=PWM_FREQUENCY)
motor3_2 = PWM(PIN_MOTOR3_2, freq=PWM_FREQUENCY)
motors = [[motor1_1, motor1_2], [motor2_1, motor2_2], [motor3_1, motor3_2]]


def _map(value: int, fromLow: int, fromHigh: int, toLow: int, toHigh: int) -> int:
    return int((value - fromLow) * (toHigh - toLow) / (fromHigh - fromLow) + toLow)


def command_motor(variables: tuple) -> bool:
    # /motors/motor/<motor nr 1-3>/<speed -100-100>
    print(f"command_motor: Motor runs with variables {variables}")

    if len(variables) == 2 and type(variables[0]) == int and type(variables[1]) == int:
        motor_nr = variables[0]
        motor_speed = variables[1]

        if motor_nr in [1, 2, 3]:

            if 100 >= motor_speed >= -100:
                try:
                    mapped_motor_speed = _map(variables[1], -100, 100, MIN_START_CYCLE, MAX_DUTY_CYCLE)
                    
                    if motor_speed < 0:
                        # Slow Decay => modes explained: https://learn.adafruit.com/improve-brushed-dc-motor-performance/current-decay-mode
                        motors[motor_nr][0].duty_u16(mapped_motor_speed)
                        motors[motor_nr][1].duty_u16(MIN_DUTY_CYCLE)

                    else:
                        motors[motor_nr][0].duty_u16(MIN_DUTY_CYCLE)
                        motors[motor_nr][1].duty_u16(mapped_motor_speed)
                    return True

                except Exception as e:
                    print(
                        f"command_motor: The motor could not be set, Exception {e}")
                    return False
            else:
                print(
                    f"command_motor: The given speed was not between -100 and 100, but {motor_speed}")
                return False
        else:
            print(
                f"command_motor: The given motor nr was not 1, 2 or 3, but {motor_nr}")
            return False
    else:
        print(
            f"command_motor: The given variables were not as expected. This function expects [<motor nr>, <speed>] and got {variables}")
        return False


def command_stop(variables: tuple) -> bool:
    # /motors/stop > boolean
    print(f"command_stop: Motor stop with variables {variables}")

    if len(variables) == 0:
        try:
            motor1_1.duty_u16(MIN_DUTY_CYCLE)
            motor1_2.duty_u16(MIN_DUTY_CYCLE)
            motor2_1.duty_u16(MIN_DUTY_CYCLE)
            motor2_2.duty_u16(MIN_DUTY_CYCLE)
            motor3_1.duty_u16(MIN_DUTY_CYCLE)
            motor3_2.duty_u16(MIN_DUTY_CYCLE)
            return True

        except Exception as e:
            print(
                f"command_stop: The motor could not be stopped, Exception {e}")
            return False
    else:
        print(f"command_stop: The given variables were not expected")
    return False


def command_move(variables: tuple) -> bool:
    # /motors/move/<direction in degrees -180-180>/<distance in cm 0-inf>
    print(f"command_move: Motor stop with variables {variables}")

    # TODO: Implement this function!
    print(f"command_move: This function is currently not implemented!")
    return False


def command_rotate(variables: tuple) -> bool:
    # /motors/rotate/<degrees -180-180>
    print(f"command_rotate: Motor stop with variables {variables}")

    # TODO: Implement this function!
    print(f"command_rotate: This function is currently not implemented!")
    return False

# TODO: place test functions somewhere
# from motor_manager import command_motor, command_stop
# message_manager.add_message(['motors', 'move'], command_motor)
# message_manager.add_message(['motors', 'stop'], command_stop)
