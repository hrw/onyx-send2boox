#!/usr/bin/env python3

#  SPDX-License-Identifier: MIT

import boox
import sys

config = boox.read_config()
send2boox = boox.Boox(config,skip_init=False)
send2boox.list_book_notes()