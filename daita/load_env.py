from dotenv import load_dotenv
from pathlib import Path
import os

pwd = os.path.dirname(os.path.abspath(__file__))
envfile = os.path.join(pwd, ".env")
dotenv_path = Path(envfile)
load_dotenv()
