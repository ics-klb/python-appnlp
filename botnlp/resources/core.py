# -*- coding: utf-8 -*-
from string import punctuation

class CoreResponse(object):

    _request = {}
    _output = {}

    def __init__(self, jsquery, **kwargs):
        self._request = jsquery

        self.query = self._request['query'] if 'query' in self._request else ''
        self.rules = self._request['rules'] if 'rules' in self._request else 'all'
        self.isgram = int(self._request['gram']) > 0 if u'gram' in self._request else True
        self.isdubl = int(self._request['dubl']) > 0 if u'dubl' in self._request else False
        self.isexpand = int(self._request['expand']) > 0 if u'expand' in self._request else False

    def clean_punctuation(self, content):

        return ''.join(c for c in content if c not in punctuation)

    def prepare(self):

        return self.query, self.rules, self.isgram, self.isdubl, self.isexpand


    def get_query(self):
        return self._request

    def get_output(self)->dict:
        return self._output


    def set_output_key(self, key, value):
        self._output[key] = value
        return self


    def set_output(self, content:dict):
        self._output = content
        return self
