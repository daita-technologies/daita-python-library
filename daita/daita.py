from daita.utils import exception_handler
from daita.dashboard import dashboard
from daita.footer import footer
import argparse

parser = argparse.ArgumentParser(description="Optional app description")
parser.add_argument("--dir", type=str, help="A required integer positional argument")
parser.add_argument(
    "--daita_token", type=str, help="A required integer positional argument"
)
args = parser.parse_args()
dir = args.dir
daita_token = args.daita_token


@exception_handler
def main():
    dashboard(daita_token=daita_token, dir=dir)
