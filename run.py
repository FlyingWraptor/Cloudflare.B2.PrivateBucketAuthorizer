#!/usr/bin/python3

import requests
import base64
import json
import os

### Constants ###
B2_APIBASE = 'https://api.backblazeb2.com'
B2F_TOKENLIFETIME = 7 * 24 * 60 * 60
CF_APIBASE = 'https://api.cloudflare.com/client/v4/'


### Configuraton ###
with open('./config.json', 'r') as config:
    CONFIG = json.loads(config.read())


### Templates ###
with open('./worker.js', 'r') as template:
    if os.path.isfile('./response_additions.js'):
        with open('./response_additions.js', 'r') as additions:
            TEMPLATE = template.read().replace('//<<ResponseAdditions>>', additions.read())
    else:
        TEMPLATE = template.read().replace('//<<ResponseAdditions>>', '')


# Retrieve worker content template (with correct values)
def parse_response(response, name):
    if CONFIG['debug']:
        print(name + ' RESPONSE:')
        print(response.status_code)
        print(response.headers)
        print(response.content)
        print()

    return json.loads(response.content.decode("UTF-8"))


# Authorize the account with the provided config credentials
def b2_authorize_account():
    auth_credentials = bytes(CONFIG['b2']['credentials']['id'] + ':' + CONFIG['b2']['credentials']['key'], 'UTF-8')
    authorization = 'Basic ' + base64.b64encode(auth_credentials).decode('UTF-8')
    response = requests.get(B2_APIBASE + '/b2api/v2/b2_authorize_account',
        headers = {'Authorization': authorization})

    return parse_response(response, 'b2_authorize_account')


# Retrieve download authorization (for a week) using an authorization token and the specified api url
def b2_authorize_downloads(api_url, authorization_token):
    body = {
        'bucketId': CONFIG['b2']['bucket']['id'],
        'fileNamePrefix': CONFIG['b2']['bucket']['prefix'],
        'validDurationInSeconds': B2F_TOKENLIFETIME
    }
    response = requests.post(api_url + '/b2api/v2/b2_get_download_authorization',
        json = body,
        headers = { 'Authorization': authorization_token })

    return parse_response(response, 'b2_authorize_downloads')


# Format the TEMPLATE using the config B2F settings & using the authorizationheader
def b2_worker_contents(authorization_header):
    bucket_config = CONFIG['b2']['bucket']

    return TEMPLATE.replace('<<B2Hostname>>', bucket_config['hostname']).replace('<<B2BucketName>>', bucket_config['name']).replace('<<AuthorizationHeader>>', authorization_header)


# Upload a new worker using a dow
def cf_upload_worker(b2_download_token):
    headers = {
        'X-Auth-Email': CONFIG['cloudflare']['email'],
        'X-Auth-Key': CONFIG['cloudflare']['appkey'],
        'Content-Type': 'application/javascript'
    }
    response = requests.put(
        '{}accounts/{}/workers/scripts/{}'
            .format(CF_APIBASE, CONFIG['cloudflare']['accountid'], CONFIG['cloudflare']['workername']),
        headers = headers,
        data = b2_worker_contents(b2_download_token))

    return parse_response(response, 'cf_upload_worker')


# C-like main function
def main():
    account_response = b2_authorize_account()
    download_response = b2_authorize_downloads(account_response['apiUrl'],
        account_response['authorizationToken'])

    cf_response = cf_upload_worker(download_response['authorizationToken'])


# Run the program
if __name__ == '__main__':
    main()
