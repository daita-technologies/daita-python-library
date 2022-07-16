import argparse
from dashboard import dashboard
parser = argparse.ArgumentParser(description='Optional app description')
parser.add_argument('--dir', type=str,
                    help='A required integer positional argument')
parser.add_argument('--daita_token', type=str,
                    help='A required integer positional argument')
args = parser.parse_args()
dir = args.dir
daita_token = args.daita_token


def main():
    dashboard(
        daita_token=daita_token, dir=dir
    )
    pass


if __name__ == "__main__":
    main()
