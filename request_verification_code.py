#!/usr/bin/env python3

import boox
import configparser
import logging

logging.basicConfig(level=logging.NOTSET)

config = configparser.ConfigParser()
config.read('config.ini')

send2boox = boox.Boox(skip_init=True)

send2boox.request_verification_code(config['default']['email'])

print("Code for token requested. Check email.")
