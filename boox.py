
import json
import logging
import os
import oss2
import random
import requests
import string

logging.basicConfig(level=logging.NOTSET)
requests_log = logging.getLogger("urllib3")
requests_log.setLevel(logging.NOTSET)
requests_log.propagate = True


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

        self.token = self.api_call('/users/signupByPhoneOrEmail',
                                   data={'mobi': email,
                                         'code': code})['data']['token']

    def api_call(self, api_url, method='GET', headers={}, data={}, params={}):
        print()
        print(data)
        print(headers)
        print(params)
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

        for entry in files:
            print(f"{entry['data']['args']['name']}")

    def send_file(self, filename):
        stss_data = self.api_call('config/stss')['data']

        self.access_key_id = stss_data['AccessKeyId']
        self.access_key_secret = stss_data['AccessKeySecret']
        self.security_token = stss_data['SecurityToken']

        auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        # auth = oss2.StsAuth(access_key_id, access_key_secret, security_token)

        bucket = oss2.Bucket(auth, self.endpoint, self.bucket_name)

        filename = '/tmp/local-test-name.txt'
        remotename = f'{self.userid}/push/remote-name.txt'
        content = oss2.to_bytes(''.join(random.choice(string.ascii_lowercase)
                                        for i in range(1024)))

        with open(filename, 'wb') as fileobj:
            fileobj.write(content)

        oss2.resumable_upload(bucket, remotename, filename,
                              headers={'x-oss-security-token':
                                       self.security_token})

        os.remove(filename)

        filename = filename.replace('/tmp/', '')

        self.api_call('push/saveAndPush', method='POST',
                      headers={
                          'Origin': 'https://eur.boox.com',
                          'Referer': 'https://eur.boox.com',
                      },
                      data=json.dumps({
                          "bucket": self.bucket_name,
                          'name': filename,
                          'parent': 'null',
                          'resourceDisplayName': filename,
                          "resourceKey": remotename,
                          "resourceType": "txt",
                          "title": filename
                      }, indent=4))
