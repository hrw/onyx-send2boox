#!/usr/bin/env python3

import boox
import configparser
import sys

config = configparser.ConfigParser()
config.read('config.ini')

if len(sys.argv) != 2:
    print('Please give verification code as argument.')
    sys.exit(-1)

code = sys.argv[1]

send2boox = boox.Boox(email=config['default']['email'], code=code)

config['default']['token'] = send2boox.token

with open('config.ini', 'w') as configfile:
    config.write(configfile)

send2boox.list_files()
