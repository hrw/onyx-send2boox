#!/usr/bin/env python3

import configparser
import boox
import sys

config = configparser.ConfigParser()
config.read('config.ini')

send2boox = boox.Boox(token=config['default']['token'])

if len(sys.argv) == 2:
    file_to_send = sys.argv[1]
    send2boox.send_file(file_to_send)

send2boox.list_files()
