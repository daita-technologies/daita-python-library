import signal
import time
from daita.footer import footer


class exception_handler:
    def __init__(self, function):
        self.function = function
        self.signal_received = False
        self.old_handler = signal.signal(signal.SIGINT, self.handler)

    def __call__(self):
        self.wrapper_function()

    def wrapper_function(self):
        try:
            self.function()
        except Exception as e:
            print(f"Error message: {str(e)}")
            footer()

    def handler(self, sig, frame):
        print("Please wait for the processing to be completed, thank you.")
        self.signal_received = (sig, frame)

    def __exit__(self):
        signal.signal(signal.SIGINT, self.old_handler)
        if self.signal_received:
            self.old_handler(*self.signal_received)


def retry_handler(max_retry, sleep_time):
    def decorator(function):
        def inner_function(*args, **kwargs):
            attempt = 0
            while attempt < max_retry:
                try:
                    return function(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                time.sleep(sleep_time * attempt)
            return function(*args, **kwargs)

        return inner_function

    return decorator
