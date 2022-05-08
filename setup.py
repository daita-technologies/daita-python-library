import pathlib
from setuptools import setup,find_packages

setup(
    name='daita',
    version='1.0.1',    
    description='Upload Data To Daita Service',
    url='https://github.com/daita-technologies/daita-python-library',
    author='daita',
    author_email='contact@daita.tech',
    license='MIT License',
    packages=find_packages(),
    install_requires=['tqdm',
                    'requests'
                          ],
    entry_points ={
            'console_scripts': [
                'daita = daita.daita:main'
            ]
        },
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)