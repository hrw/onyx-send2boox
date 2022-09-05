#!/usr/bin/env python3

import configparser
import boox

config = configparser.ConfigParser()
config.read('config.ini')

send2boox = boox.Boox(token=config['default']['token'])

send2boox.send_file()

# send2boox.list_files()
