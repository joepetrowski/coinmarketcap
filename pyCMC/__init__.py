# -*- coding: utf-8 -*-
"""
Started on 19 June 2019
@author: joepetrowski
"""

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

class CMC(object):

    def __init__(self, cmc_key):
        self.root_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/'
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': cmc_key,
        }

    def __call__(self, url, parameters={}):
        session = Session()
        session.headers.update(self.headers)

        try:
            response = session.get(url, params=parameters)
            data = json.loads(response.text)
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            data = {
                'error' : e,
            }
        
        return data
    
    # Returns a current list of all active cryptocurrencies 
    # supported by the platform including a unique id for
    # each cryptocurrency.
    #
    # `symbol` can be a string of currency symbols (e.g. 'BTC,ETC,LTC').
    # If `symbol` is provided, other parameters are ignored.
    def map(self, status='active', start=1, limit=10, symbol=None):

        if status != 'inactive' and status != 'active':
            status = 'active'

        if start < 1:
            start = 1

        if limit < 1:
            limit = 1
        elif limit > 5000:
            limit = 5000
        
        url = self.root_url + 'map'

        parameters = {
            'status' : status,
            'start' : start,
            'limit' : limit,
        }

        if not symbol:
            parameters = {
                'symbol' : symbol,
            }
        
        data = self.__call__(url, parameters)
        
        return data

    # Returns all static metadata available for one or more cryptocurrencies.
    # This information includes details like logo, description, official
    # website URL, social links, and links to a cryptocurrency's technical
    # documentation.
    #
    # Can only use one of the inputs, `coinid`, `slug`, or `symbol`.
    # They can all be a string-list, e.g. `coinid='1,12,42'`.
    def metadata(self, coinid=None, slug=None, symbol=None):

        if not coinid and not slug and not symbol:
            err = {
                'error' : 'No parameters provided.',
            }
            return err
        
        url = self.root_url + 'info'

        if coinid:
            parameters = { 'id' :  coinid }
        elif slug:
            parameters = { 'slug' :  slug }
        elif coinid:
            parameters = { 'symbol' :  symbol }

        data = self.__call__(url, parameters)

        return data

    # Returns listings for currencies.
    #
    # Return value is a dictionary with primary field 'data',
    # which contains a list of up to `limit` listings, and another
    # field, 'status'.
    #
    # start                 int, starting value
    # limit                 int, number of currencies to return
    # convert               string, symbol of currency to use as quote
    # convert_id            string, id of currency to use as quote
    # sort                  string, value to sort by (name, market cap, etc)
    # sort_dir              string, can be 'asc' or 'desc'
    # cryptocurrencytype    string, types to return, can be 'all', 'coins', or 'tokens'
    def listings(self, start=1, limit=100, convert='USD', convert_id=None, sort=None, sort_dir=None, cryptocurrencytype=None):
        
        if start < 1:
            start = 1

        if limit < 1:
            limit = 1
        elif limit > 5000:
            limit = 5000

        url = self.root_url + 'listings/latest'

        parameters = {
            'start' : start,
            'limit' : limit,
            'convert' : convert,
        }

        if convert_id:
            del parameters['convert']
            parameters['convert_id'] = convert_id
        
        valid_sort = ['name', 'symbol', 'date_added', 'market_cap', \
            'market_cap_strict','price', 'circulating_supply', 'total_supply', \
            'max_supply','num_market_pairs', 'volume_24h', 'percent_change_1h', \
            'percent_change_24h', 'percent_change_7d']
        if sort:
            if sort not in valid_sort:
                sort = 'market_cap'
            parameters['sort'] = sort
        
        valid_sort_dir = ['asc', 'desc']
        if sort_dir:
            if sort_dir not in valid_sort_dir:
                sort_dir = 'desc'
            parameters['sort_dir'] = sort_dir
        
        valid_types = ['all', 'coins', 'tokens']
        if cryptocurrencytype:
            if cryptocurrencytype not in valid_types:
                cryptocurrencytype = 'all'
            parameters['cryptocurrencytype'] = cryptocurrencytype

        data = self.__call__(url, parameters)
        
        return data
    