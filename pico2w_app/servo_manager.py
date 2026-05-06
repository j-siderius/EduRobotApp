from machine import Pin, PWM
from pinconfig import *

PWM_FREQUENCY = 50
MIN_PULSE_WIDTH = 500
MAX_PULSE_WIDTH = 2500
MIN_DUTY_CYCLE = int((MIN_PULSE_WIDTH / 20000) * 100)
MAX_DUTY_CYCLE = int((MAX_PULSE_WIDTH / 20000) * 100)
ABSMAX_DUTY_CYCLE = 65535

servo1 = PWM(PIN_SERVO1, freq=PWM_FREQUENCY)
# TODO: Fix servoes list with all actual servos once configured
servos = [servo1, servo1, servo1]


def _map(value: int, fromLow: int, fromHigh: int, toLow: int, toHigh: int) -> float:
    return (value - fromLow) * (toHigh - toLow) / (fromHigh - fromLow) + toLow


def command_servo(variables: tuple) -> bool:
    # /servos/servo/<servo nr 1-3>/<degrees 0-180>
    print(f"command_servo: Servo runs with variables {variables}")

    if len(variables) == 2 and type(variables[0]) == int and type(variables[1]) == int:
        servo_nr = variables[0]
        servo_position = variables[1]

        if servo_nr in [1, 2, 3]:

            if 0 >= servo_position >= 180:

                try:
                    mapped_duty_cycle = int(_map(
                        servo_position, 0, 180, MIN_DUTY_CYCLE, MAX_DUTY_CYCLE) * (ABSMAX_DUTY_CYCLE/100))
                    servos[servo_nr].duty_u16(mapped_duty_cycle)
                    return True

                except Exception as e:
                    print(
                        f"command_servo: The servo could not be set, Exeception {e}")
                    return False
            else:
                print(
                    f"command_servo: The given servo position was not between 0 and 180, but {servo_position}")
                return False
        else:
            print(
                f"command_servo: The given servo nr was not 1, 2 or 3, but {servo_nr}")
            return False
    else:
        print(
            f"command_servo: The given variables were not as expected. This function expects [<servo nr 1-3>, <degrees 0-180>] and got {variables}")
        return False


def command_move(variables: tuple) -> bool:
    # /servos/move/<x-coordinate 0-??>/<y-coordinate 0-??>
    print(f"command_move: Servos move with variables {variables}")

    # TODO: Implement this function!
    print(f"command_move: This function is currently not implemented!")
    return False


def command_status(variables: tuple) -> bool | dict:
    # /servos/status > degrees1, 2, 3
    print(f"command_status: Status called with variables {variables}")

    if len(variables) == 0:
        try:

            status = {}
            for servo in servos:
                status[servo] = servo.duty_u16()
            return status

        except Exception as e:
            print(
                f"command_status: The servo status could not be fetched, Exception {e}")
            return False
    else:
        print(f"command_status: The given variables were not expected")
        return False
