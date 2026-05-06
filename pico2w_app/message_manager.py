import re

class MessageManager:
    def __init__(self) -> None:
        self.message_regex = re.compile("/| ")
        self.isdigit_regex = re.compile(r'^-?[0-9]+$')
        self.message_callbacks = list()

    def add_message(self, message_format: list[str], callback_function) -> bool:
        try:
            self.message_callbacks.append(
                {"format": message_format, "callback": callback_function})

            print(
                f"message_manager: callback {callback_function.__name__} successfully added with message format {message_format}")
            return True
        except Exception as e:
            print(
                f"message_manager: Failed to add callback function with Exception {e}")
            return False

    def process_message(self, message: str) -> bool:
        split_message = message.split('/')[1:]
        commands, variables = list(), list()
        for item in split_message:
            if self.isdigit_regex.match(item):
                variables.append(item)
            else:
                commands.append(item)

        for message_callback in self.message_callbacks:
            if message_callback['format'] == commands:
                message_callback['callback'](variables)
                return True
        print(
            f"message_manager: No callback was found for the incoming message with commands {commands} and variables {variables}")
        return False


# Run test cases if this file is run as main
if __name__ == "__main__":

    message_manager = MessageManager()

    def test_function(variables: tuple) -> None:
        print(f"message_manager: Test function called with variables {variables}")
        
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
