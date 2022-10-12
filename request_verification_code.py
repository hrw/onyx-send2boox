#!/usr/bin/env python3

#  SPDX-License-Identifier: MIT

import boox

config = boox.read_config()
send2boox = boox.Boox(skip_init=True)

send2boox.request_verification_code(config['default']['email'])

print("Code for token requested. Check email.")
