import argparse
from daita.utils import exception_handler
from daita.dashboard import dashboard
from daita.footer import footer

parser = argparse.ArgumentParser(
    description="Upload images via DAITA's official easy-to-use Python library."
)
parser.add_argument("--dir", type=str, help="The root directory path for the images.")
parser.add_argument(
    "--daita_token", type=str, help="User access token for the DAITA platform."
)
args = parser.parse_args()
dir = args.dir
daita_token = args.daita_token


@exception_handler
def main():
    dashboard(daita_token=daita_token, dir=dir)
