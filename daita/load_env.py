from dotenv import load_dotenv
from pathlib import Path
import os

pwd = os.path.dirname(os.path.abspath(__file__))
envfile = os.path.join(pwd, ".env.development")
dotenv_path = Path(envfile)
load_dotenv(dotenv_path=dotenv_path)
<<<<<<< HEAD
=======
print(os.environ["DAITA_TOKEN"])
>>>>>>> 7c7f2eb925721b410763da809e8baec411f35b62
