import json
import logging
import os
import oss2
import requests
import uuid


class Boox:

    def __init__(self, token='', email='', code=''):

        if token:
            self.token = token
        elif email and code:
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
        headers["Authorization"] = f"Bearer {self.token}"
        r = requests.request(method, f'https://eur.boox.com/api/1/{api_url}',
                             headers=headers,
                             params=params,
                             data=data)

        logging.info(json.dumps(r.json(), indent=4))
        logging.info('')

        return r.json()

    def list_files(self, limit=24, offset=0):
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
                  f"{data['storage'][format]['oss']['size']:>10} | "
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

        self.api_call('push/saveAndPush', method='POST',
                      headers={
                          'Content-Type': 'application/json;charset=utf-8',
                      },
                      data=json.dumps({
                          "data": {
                              "bucket": self.bucket_name,
                              'name': filename,
                              'parent': None,
                              'resourceDisplayName': filename,
                              "resourceKey": remotename,
                              "resourceType": "txt",
                              "title": filename}
                      }))
