#!/usr/bin/env python3

#  SPDX-License-Identifier: MIT

import boox
import sys

if len(sys.argv) < 2:
    print("Give some Ids of files to remove")
    sys.exit(-1)

config = boox.read_config()
send2boox = boox.Boox(token=config['default']['token'], show_log=True)

files_to_remove = sys.argv[1:]
send2boox.delete_files(files_to_remove)

send2boox.list_files()
