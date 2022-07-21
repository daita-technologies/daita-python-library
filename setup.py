import pathlib
from setuptools import setup,find_packages

setup(
    name='daita',
    version='0.0.1',    
    description='DAITA\'s official easy-to-use Python library',
    url='https://github.com/daita-technologies/daita-python-library',
    author='DAITA Technologies',
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
        'License :: OSI Approved :: MIT License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)