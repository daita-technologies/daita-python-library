from daita.dashboard import dashboard
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


class KeyboardInterrupt:
    def __enter__(self):
        self.signal_received = False
        self.old_handler = signal.signal(signal.SIGINT, self.handler)

    def handler(self, sig, frame):
        print("Please wait for the processing to be completed, thank you.")
        self.signal_received = (sig, frame)

    def __exit__(self):
        signal.signal(signal.SIGINT, self.old_handler)
        if self.signal_received:
            self.old_handler(*self.signal_received)


def main():
    with KeyboardInterrupt():
        dashboard(daita_token=daita_token, dir=dir)
        pass
