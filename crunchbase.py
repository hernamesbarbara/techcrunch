import numpy as np
import pandas as pd
import requests
import ujson as json

class Api(object):
    def __init__(self):
        self.setup()

    def setup(self):
        f = open('./crunchbase_secrets.json')
        secrets = json.loads(f.read())
        self.API_KEY = secrets['api_key']
        self.USERNAME = secrets['username']
        self.BASE_URI = 'http://api.crunchbase.com/v/1'
        self.SEARCH_PATH = '/search.js'

    def auth(self,payload):
        api_key = {'api_key': self.API_KEY}
        payload.update(api_key)
        return payload

    def execute(self, endpoint, payload={}):
        url = self.BASE_URI+endpoint
        payload = self.auth(payload)
        return requests.get(url, params=payload)

    def search(self, query={}):
        if not query: return False
        endpoint = self.SEARCH_PATH
        res = self.execute(endpoint, query)
        return self.respond_with(res)

    def respond_with(self, res):
        if not res: return False
        if res.status_code == 200:
            res = json.loads(res.text)
        else:
            res = {'status': res.status_code, 'text': res.text}
        return res



api = Api()
payload = {'query': 'on deck'}
res = api.search(payload)
res = res['results']

keys = list(set([key for record in res for key in record]))






