# DataProcessing ToolChain

## Usage:

    python DataProcessing.py

Choose Log Files to convert, converted files are then uploaded to Marple.

## Basic Idea for full Toolchain:

![alt text](Docs/Toolchain.png)

## Install

Install Python Requirements:

    pip install -r requirements.txt


requirements.txt is created using pipreqs or pip freeze > requirements.txt

## Marple API Key

For Marple Stuff .env File is needed with API Key!

    SECRET_ACCESS_TOKEN = "Key goes here"


# Docs

Kvaser CANlib SDK: https://kvaser.com/developer/canlib-sdk/

canlib - a Python wrapper for Kvaser CANlib: https://pycanlib.readthedocs.io

Marple API: https://docs.marpledata.com/docs/for-developers/python

Marple Python: https://pypi.org/project/marpledata/

Cooles dings: https://github.com/emotionrennteam/log-storage-client

https://git-scm.com/book/en/v2/Git-Tools-Submodules