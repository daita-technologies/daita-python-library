from daita.dashboard import dashboard
from daita.footer import footer
import argparse
import signal

parser = argparse.ArgumentParser(description="Optional app description")
parser.add_argument("--dir", type=str, help="A required integer positional argument")
parser.add_argument(
    "--daita_token", type=str, help="A required integer positional argument"
)
args = parser.parse_args()
dir = args.dir
daita_token = args.daita_token


class exception_handler:
    def __init__(self,function):
        self.function = function
        self.signal_received = False
        self.old_handler = signal.signal(signal.SIGINT, self.handler)
    
    def __call__(self):
        self.wrapper_function()

    def wrapper_function(self):
        try:
            self.function()
        except Exception as e:
            footer()

    def handler(self, sig, frame):
        print("Please wait for the processing to be completed, thank you.")
        self.signal_received = (sig, frame)

    def __exit__(self):
        signal.signal(signal.SIGINT, self.old_handler)
        if self.signal_received:
            self.old_handler(*self.signal_received)            

@exception_handler
def main():
    dashboard(daita_token=daita_token, dir=dir)
