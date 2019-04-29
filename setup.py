import os
from setuptools import setup, find_packages


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def requirements():
    requirements_list = []

    with open('requirements.txt') as requirements:
        for install in requirements:
            requirements_list.append(install.strip())

    return requirements_list

setup(
    name="AlarmBot",
    version="0.0.1",
    author="Andrea Visinoni",
    author_email="andrea.visinoni@gmail.com",
    description=("Telegram Bot to warn about linux servers issues"),
    license="Apache",
    keywords="telegram bot linux server",
    url="https://github.com/GreatMaker/AlarmBot",
    packages=find_packages(exclude=['tests*']),
    long_description=read('README.md'),
    install_requires=requirements(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.5",
    ],
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'telegram_alarm_bot=main:main',
        ],
    },
)