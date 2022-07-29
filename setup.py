import os
from setuptools import setup, find_packages

import daita

PATH_ROOT = os.path.dirname(__file__)


def load_description(path_dir=PATH_ROOT, filename="README.md"):
    # Load long description from README in the directory
    with open(os.path.join(path_dir, filename)) as f:
        long_description = f.read()
    return long_description


name = "daita"
description = "DAITA's official easy-to-use Python library."
long_description = load_description()
url = "https://github.com/daita-technologies/daita-python-library"
author = "DAITA Technologies"
author_email = "contact@daita.tech"
license = "MIT"

project_urls = {
    "Homepage": "https://daita.tech",
    "Web-App": "https://app.daita.tech",
    "GitHub": "https://github.com/daita-technologies",
    "Source": "https://github.com/daita-technologies/daita-python-library",
}

entry_points = {"console_scripts": ["daita = daita.daita:main"]}

classifiers = [
    "Development Status :: 1 - Planning",
    "License :: OSI Approved :: MIT License",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
]

python_requires = ">=3.8"
install_requires = ["tqdm", "requests", "python-dotenv"]

setup(
    name=name,
    version=daita.__version__,
    description=description,
    url=url,
    author=author,
    author_email=author_email,
    license=license,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['daita'],
    install_requires=install_requires,
    entry_points=entry_points,
    classifiers=classifiers,
    python_requires=python_requires,
    project_urls=project_urls,
    package_data={
        'daita': ['*', '.env.development']
    }
)
