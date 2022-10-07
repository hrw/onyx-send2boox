#  SPDX-License-Identifier: MIT

import json
import locale
import logging
import os
import oss2
import requests
import uuid


class Boox:

    def __init__(self, token=None, email=None, code=None, skip_init=False):

        if skip_init:
            self.token = False
        else:
            if token:
                self.token = token
            elif email and code:
                self.token = False
                self.login_with_email(email, code)

            self.userid = self.api_call('users/me')['data']['uid']

            self.api_call('users/getDevice')
            self.api_call('im/getSig', params={"user": self.userid})

            onyx_cloud = self.api_call('config/buckets')['data']['onyx-cloud']

            self.bucket_name = onyx_cloud['bucket']
            self.endpoint = onyx_cloud['aliEndpoint']

    def login_with_email(self, email, code):

        self.token = self.api_call('users/signupByPhoneOrEmail',
                                   data={'mobi': email,
                                         'code': code})['data']['token']

    def api_call(self, api_url, method='GET', headers={}, data={}, params={}):

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        if data:
            headers['Content-Type'] = 'application/json;charset=utf-8'
            method = 'POST'

        r = requests.request(method, f'https://eur.boox.com/api/1/{api_url}',
                             headers=headers,
                             params=params,
                             data=json.dumps(data))

        logging.info(json.dumps(r.json(), indent=4))
        logging.info('')

        return r.json()

    def list_files(self, limit=24, offset=0):
        # I would expect LC_ALL to be set but it may not be
        locale.setlocale(locale.LC_ALL, locale.getlocale()[0])
        files = self.api_call('push/message',
                              params={"where": '{' f'"limit": {limit}, '
                                      f'"offset": {offset}, '
                                      '"parent": 0}'})['list']

        print("        ID               |    Size    | Name")
        print("-------------------------|------------|"
              "-------------------------------------------------------")

        for entry in files:
            data = entry['data']['args']
            format = data['formats'][0]
            print(f"{data['_id']} | "
                  f"{int(data['storage'][format]['oss']['size']):>10n} | "
                  f"{data['name']}")

    def send_file(self, filename):
        stss_data = self.api_call('config/stss')['data']

        self.access_key_id = stss_data['AccessKeyId']
        self.access_key_secret = stss_data['AccessKeySecret']
        self.security_token = stss_data['SecurityToken']

        auth = oss2.Auth(self.access_key_id, self.access_key_secret)

        bucket = oss2.Bucket(auth, self.endpoint, self.bucket_name)

        tmp, extension = os.path.splitext(filename)
        remotename = f'{self.userid}/push/{uuid.uuid4()}.{extension}'

        token_headers = {'x-oss-security-token': self.security_token}

        oss2.resumable_upload(bucket, remotename, filename,
                              headers=token_headers)

        filename = os.path.basename(filename)

        self.api_call('push/saveAndPush',
                      headers={
                          'Content-Type': 'application/json;charset=utf-8',
                      },
                      data={
                          "data": {
                              "bucket": self.bucket_name,
                              'name': filename,
                              'parent': None,
                              'resourceDisplayName': filename,
                              "resourceKey": remotename,
                              "resourceType": "txt",
                              "title": filename}
                      })

    def request_verification_code(self, email):
        self.api_call('users/sendMobileCode', data={"mobi": email})
