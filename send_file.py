#!/usr/bin/env python3

#  SPDX-License-Identifier: MIT

import boox
import sys

config = boox.read_config()
send2boox = boox.Boox(config)

if len(sys.argv) >= 2:
    for file_to_send in sys.argv[1:]:
        send2boox.send_file(file_to_send)

send2boox.list_files()
