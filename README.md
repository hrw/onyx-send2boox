# What it is?

Python code to handle files Onyx Boox e-book reader via Send2Boox service.


# Usage

## How to get token

First you need to have a token:

1. Edit "config.ini" file and add your e-mail address there.
2. Run "request_verification_code.py" script to request e-mail with verification code.
3. Check mail -- you should get e-mail from "【ONYX BOOX】 <info@mail.boox.com>"
   with 6 digit code inside.
4. Run "obtain_token.py 6_digit_code" script -- it will login to send2boox
   service and store token into "config.ini" file.

## Sending files to e-reader

Run "send_file.py FILENAME1 FILENAME2" script. It uses token from "config.ini"
and pushes file to cloud used by Onyx. Later (or if run without arguments) it
lists some files from your send2boox account.


# Contribute

If you want to contribute then feel free to fork, edit and send back pull
requests, open issues etc.


# To do

- add error checking
- handle more API calls
