'''Installation scrip run by pip'''
from setuptools import setup, find_packages

setup(
    name='competitive_programming_tools',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'beautifulsoup4',
        'colorama',
        'click',
    ],
    entry_points={
        'console_scripts': [
            'cpt = competitive_programming_tools:main',
        ],
    },
)
