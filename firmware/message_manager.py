# import re
# 
# 
# class MessageManager:
#     def __init__(self) -> None:
#         self.isint_regex = re.compile(r'^-?[0-9]+$')
#         self.message_callbacks = list()
# 
#     def add_message(self, message_format: list[str], callback_function) -> bool:
#         try:
#             self.message_callbacks.append(
#                 {"format": message_format, "callback": callback_function})
#             return True
#         except Exception as e:
#             print(f"Failed to add callback function with Exception {e}")
#             return False
# 
#     def process_message(self, message: str) -> bool:
#         split_message = message.split('/')[1:]
#         commands, variables = list(), list()
#         for item in split_message:
#             if self.isint_regex.match(item):
#                 variables.append(item)
#             else:
#                 commands.append(item)
# 
#         for message_callback in self.message_callbacks:
#             if message_callback['format'] == commands:
#                 message_callback['callback'](variables)
#                 return True
#         print(f"No callback found for {commands}")
#         return False

import re, asyncio

class MessageManager:
    def __init__(self) -> None:
        # Regex to match integers and floats (including negative)
        self.number_regex = re.compile(r'^-?\d+(\.\d+)?$')
        self.message_callbacks = list()

    def add_message(self, message_format: list[str], callback_function) -> bool:
        try:
            self.message_callbacks.append(
                {"format": message_format, "callback": callback_function})
            return True
        except Exception as e:
            print(f"Failed to add callback function with Exception {e}")
            return False

    def _to_number(self, s: str):
        """Convert string to int or float."""
        return float(s) if '.' in s else int(s)

    async def process_message(self, message: str) -> bool:
        split_message = message.split('/')[1:]
        commands, variables = list(), list()

        for item in split_message:
            if self.number_regex.match(item):
                variables.append(self._to_number(item))
            else:
                commands.append(item)

        print(f"process_message {commands}, {variables}")

        for message_callback in self.message_callbacks:
            if message_callback['format'] == commands:
                # Unpack the variables list as separate arguments
                await message_callback['callback'](*variables)
                return True
        print(f"No callback found for {commands}")
        return False


if __name__ == "__main__":
    # Test functionality
    message_manager = MessageManager()

    def test_function(variables: tuple) -> None:
        print(f"Message manager Test function called with variables {variables}")
        
    message_manager.add_message(['tests','test'], test_function)

    # Testing functionality
    examples = [
        "/motors/motor/1/-40",  # /motors/motor/<motor nr 1-3>/<speed -100-100>
        "/motors/motor/2/100",
        "/motors/motor/3/0",
        # /motors/move/<direction in degrees -180-180>/<distance in cm 0-inf>
        "/motors/move/40/50",
        "/motors/move/-65/-20",
        "/motors/rotate/120",  # /motors/rotate/<degrees -180-180>
        "/motors/rotate/-90",
        "/motors/stop",  # /motors/stop > boolean
        "/sensors/front_distance",  # /sensors/front_distance > distance in cm
        "/sensors/motor_encoder/1",  # /sensors/motor_encoder/<motor nr 1-3>
        "/sensors/motor_encoder/2",
        "/sensors/motor_encoder/3",
        "/sensors/compass",  # /sensors/compass > heading in degrees
        "/sensors/color",  # /sensors/color > color as r,g,b
        "/servos/servo/1/60",  # /servos/servo/<servo nr 1-3>/<degrees 0-180>
        "/servos/servo/2/30",
        "/servos/servo/3/0",
        "/servos/move/100/50",  # /servos/move/<x-coordinate 0-??>/<y-coordinate 0-??>
        "/servos/move/0/25",
        "/servos/status",  # /servos/status > degrees1, 2, 3
        "/battery/status",  # /battery/status > charge, voltage, temperature??
        "/controller/status",  # /controller/status > load, memory, temperature??
        "/tests/test",  # TESTING ONLY
        "/tests/test/1/2/3"
    ]
    
    for message in examples:
        message_manager.process_message(message)
