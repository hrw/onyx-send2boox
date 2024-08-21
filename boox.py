#  SPDX-License-Identifier: MIT

import configparser
import json
import locale
import logging
import os
import oss2
import requests
import uuid


def read_config(filename="config.ini"):
    config = configparser.ConfigParser()
    config.read(filename)

    return config


class Boox:

    def __init__(self, config, code=None, skip_init=False,
                 show_log=False):

        if show_log:
            logging.basicConfig(level=logging.NOTSET)

        if config['default']['cloud']:
            self.cloud = config['default']['cloud']
        else:
            self.cloud = 'eur.boox.com'

        if skip_init:
            self.set_token_and_cookie_to_false()
        else:
            if config['default']['token']:
                self.token = config['default']['token']
            elif config['default']['email'] and code:
                self.set_token_and_cookie_to_false()
                self.login_with_email(config['default']['email'], code)

            self.userid = self.api_call('users/me')['data']['uid']

            self.api_call('users/getDevice')
            self.api_call('im/getSig', params={"user": self.userid})

            onyx_cloud = self.api_call('config/buckets')['data']['onyx-cloud']

            self.bucket_name = onyx_cloud['bucket']
            self.endpoint = onyx_cloud['aliEndpoint']
            # Share session for other API calls like neocloud
            self.cookie = {"SyncGatewaySession": self.api_call('users/syncToken')['data']['session_id']} 

    def set_token_and_cookie_to_false(self):
        # This allows to use Boox class without token and cookie
        self.token = False
        self.cookie = False

    def login_with_email(self, email, code):

        self.token = self.api_call('users/signupByPhoneOrEmail',
                                   data={'mobi': email,
                                         'code': code})['data']['token']
        self.cookie = {"SyncGatewaySession": self.api_call('users/syncToken')['data']['session_id']}        

    def api_call(self, api_url, method='GET', headers={}, data={}, params={}):

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        if data:
            headers['Content-Type'] = 'application/json;charset=utf-8'
            method = 'POST'
        
        r = requests.request(method, f'https://{self.cloud}/api/1/{api_url}',
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

    def delete_files(self, ids):
        self.api_call('push/message/batchDelete', data={"ids": ids})
