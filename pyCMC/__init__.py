# -*- coding: utf-8 -*-
"""
Started on 19 June 2019
author: joepetrowski
author_email: joepetrowski@protonmail.com
license: Apache v2.0
"""

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

class CMC(object):

	# See: https://coinmarketcap.com/api/documentation/v1/
	def __init__(self, cmc_key):
		self.root_url = 'https://pro-api.coinmarketcap.com/v1/'
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

	def _convertparams(self, convert=None, convert_id=None, parameters={}):

		if convert:
			parameters['convert'] = convert.replace(' ', '')
		elif convert_id:
			parameters['convert_id'] = convert_id.replace(' ', '')

		return parameters
	
	def _sort_params(self, sort=None, sort_dir=None, cryptocurrencytype=None, parameters={}):

		valid_sort = ['name', 'symbol', 'date_added', 'market_cap', 'market_cap_strict', \
			'price', 'circulating_supply', 'total_supply', 'max_supply','num_market_pairs', \
			'volume_24h', 'percent_change_1h', 'percent_change_24h', 'percent_change_7d']
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

		return parameters
	
	def _intervals(self, interval, parameters={}):

		valid_intervals = [ \
			'yearly', 'monthly', 'weekly', 'daily', 'hourly', \
			'5m', '10m', '15m', '30m', '45m', \
			'1h', '2h', '3h', '6h', '12h', '24h', \
			'1d', '2d', '3d', '7d', '14d', '15d', '30d', '60d', '90d', '365d'
		]

		if interval in valid_intervals:
			parameters['interval'] = interval

		return parameters
	
	def _id_symbol(self, coinId=None, slug=None, symbol=None, parameters={}, required=True):

		if required and not coinId and not slug and not symbol:
			err = { 'error' : 'No parameters provided.' }
			return err
		
		if coinId:
			parameters['id'] = coinId.replace(' ', '')
		elif slug:
			parameters['slug'] = slug.replace(' ', '')
		elif symbol:
			parameters['symbol'] = symbol.replace(' ', '')
		
		return parameters
	
	# Returns a current list of all active cryptocurrencies supported by the
	# platform including a unique ID for each cryptocurrency.
	#
	# It is highly recommended to use this function and map your coins of interest
	# to their ID in all other function calls. Not all symbols are unique, so using
	# IDs will reduce the risk of error.
	#
	# Inputs
	# status    string, can be 'active' or 'inactive'.
	# start     int, currency, ordered by market cap, to start from.
	# limit     int, how many currencies to get data for.
	# symbol    string, can be a string of currency symbols (e.g. 'BTC,ETC,LTC').
	#           If `symbol` is provided, other parameters are ignored.
	def map(self, status='active', start=1, limit=10, symbol=None):

		if status != 'inactive' and status != 'active':
			status = 'active'

		if start < 1:
			start = 1

		if limit < 1:
			limit = 1
		elif limit > 5000:
			limit = 5000
		
		url = self.root_url + 'cryptocurrency/map'

		parameters = {
			'listing_status' : status,
			'start' : str(int(start)),
			'limit' : str(int(limit)),
		}

		# `symbol` overrides all other parameters
		if symbol:
			parameters = { 'symbol' : symbol.replace(' ', '') }
		
		data = self.__call__(url, parameters)
		
		return data

	# Returns all static metadata available for one or more cryptocurrencies. This information
	# includes details like logo, description, official website URL, social links, and links
	# to a cryptocurrency's technical documentation.
	#
	# Can only use one of the inputs, `coinid`, `slug`, or `symbol`.
	# Prioritizes `coinId` over `slug` over `symbol`.
	#
	# Inputs
	# coinId    string, coin ID. See `map()`.
	# slug      string, coin names (e.g. 'bitcoin,ethereum').
	# symbol    string, coin symbmols (e.g. 'BTC,ETH').
	def metadata(self, coinId=None, slug=None, symbol=None):
		
		url = self.root_url + 'cryptocurrency/info'

		parameters = self._id_symbol(coinId, slug, symbol, {}, True)
		if 'error' in parameters:
			return parameters

		data = self.__call__(url, parameters)

		return data

	# Returns listings (total supply, max supply, price, percent change, the info you would see
	# on coinmarketcap.com) for currencies.
	#
	# Prioritizes `convert` over `convert_id`.
	#
	# Inputs
	# start                 int, cryptocurrency by market cap to start from.
	# limit                 int, number of currencies to return.
	# convert               string, symbol(s) of currency to use as quote.
	# convert_id            string, ID(s) of currency to use as quote. See `map()`.
	# sort                  string, value to sort by (name, market cap, etc).
	#                       If your sort value is not valid, it will sort by market cap.
	#                       See the code for a list of valid sort items.
	# sort_dir              string, can be 'asc' or 'desc'.
	#                       If your sort direction is not valid, it will sort descending.
	# cryptocurrencytype    string, types to return, can be 'all', 'coins', or 'tokens'.
	#                       If your type is not valid, it will return all.
	def listings(self, start=1, limit=100, convert=None, convert_id=None, sort=None, sort_dir=None, cryptocurrencytype=None):
		
		if start < 1:
			start = 1

		if limit < 1:
			limit = 1
		elif limit > 5000:
			limit = 5000

		url = self.root_url + 'cryptocurrency/listings/latest'

		parameters = {
			'start' : str(int(start)),
			'limit' : str(int(limit)),
		}

		parameters = self._convertparams(convert, convert_id, parameters)
		
		parameters = self._sort_params(sort, sort_dir, cryptocurrencytype, parameters)

		data = self.__call__(url, parameters)
		
		return data
	
	# Same as `listings()` but for a historical date.
	#
	# Requires paid plan.
	#
	# `date` is a string and must be Unix or ISO 8601 format (e.g. '2018-02-24'). Only the _date_,
	# and not the _time_, will be considered.
	def historical_listings(self, date, start=1, limit=100, convert=None, convert_id=None, sort=None, sort_dir=None, cryptocurrencytype=None):
		
		assert( type(date) == str )

		if start < 1:
			start = 1

		if limit < 1:
			limit = 1
		elif limit > 5000:
			limit = 5000

		url = self.root_url + 'cryptocurrency/listings/latest'

		parameters = {
			'date' : date,
			'start' : str(int(start)),
			'limit' : str(int(limit)),
		}

		parameters = self._convertparams(convert, convert_id, parameters)
		
		parameters = self._sort_params(sort, sort_dir, cryptocurrencytype, parameters)

		data = self.__call__(url, parameters)
		
		return data

	# Get the latest market quote for 1 or more cryptocurrencies. Use the 'convert'
	# option to return market values in multiple fiat and cryptocurrency conversions
	# in the same call.
	#
	# Prioritizes `coinId` over `slug` over `symbol`.
	# Prioritizes `convert` over `convert_id`.
	#
	# Inputs
	# coinId        string, coin ID(s). See `map()`.
	# slug          string, coin name(s) (e.g. 'bitcoin,ethereum').
	# symbol        string, coin symbmol(s) (e.g. 'BTC,ETH').
	# convert       string, symbol(s) of currency to use as quote.
	# convert_id    string, ID(s) of currency to use as quote. See `map()`.
	def quotes(self, coinId=None, slug=None, symbol=None, convert=None, convert_id=None):

		url = self.root_url + 'cryptocurrency/quotes/latest'

		parameters = self._id_symbol(coinId, slug, symbol, {}, True)
		if 'error' in parameters:
			return parameters
		
		parameters = self._convertparams(convert, convert_id, parameters)
		
		data = self.__call__(url, parameters)
		
		return data

	# Historical quotes. A historic quote for every 'interval' period between your 'time_start'
	# and 'time_end' will be returned.
	#
	# Requires paid plan.
	#
	# Inputs
	# coinId    	string, coin ID(s). See `map()`.
	# symbol        string, coin symbmol(s) (e.g. 'BTC,ETH').
	# time_start    string, Unix or ISO 8601 timestamp for when to start collecting data.
	#				Optional, if not provided, will work backwards from `time_end`.
	# time_end      string, Unix or ISO 8601 timestamp for when to end collecting data.
	#				Optional, if not provided, will work forwards from `time_start`.
	#				If neither are provided, `time_end` will default to the current time.
	# count			int, the number of interval periods for which to collect data.
	# interval		string, the time interval between quotes. See docs for valid values:
	#				https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyQuotesHistorical
	# convert		string, symbol(s) of currency to use as quote.
	# convert_id    string, ID(s) of currency to use as quote. See `map()`.
	#
	# WARNING: Completely untested, I don't have a paid plan.
	def historical_quotes(
		self,
		coinId=None,
		symbol=None,
		time_start=None,
		time_end=None,
		count=10,
		interval=None,
		convert=None,
		convert_id=None
	):

		parameters = self._id_symbol(coinId, None, symbol, {}, True)
		if 'error' in parameters:
			return parameters
		
		if time_start:
			assert( type(time_start) == str )
			parameters['time_start'] = time_start
		
		if time_end:
			assert( type(time_end) == str )
			parameters['time_end'] = time_end
		
		if count < 1:
			count = 1
		elif count > 10_000:
			count = 10_000
		
		parameters['count'] = str(int(count))

		if interval:
			assert( type(interval) == str )
			parameters = self._intervals(interval, parameters)

		parameters = self._convertparams(convert, convert_id, parameters)
		
		url = self.root_url + 'cryptocurrency/quotes/historical'

		data = self.__call__(url, parameters)

		return data

	# Market pairs: Lists all active market pairs that CoinMarketCap tracks for a given cryptocurrency
	# or fiat currency. The latest price and volume information is returned for each market. Use the
	# "convert" option to return market values in multiple fiat and cryptocurrency conversions in the
	# same call.
	#
	# Requires paid plan.
	#
	# Inputs
	# coinID		string, a cryptocurrency or fiat currency to get market pairs for. Only 1. (e.g. '1')
	# slug			string, a cryptocurrency or fiat currency to get market pairs for. Only 1. (e.g. 'bitcoin')
	# symbol		string, a cryptocurrency or fiat currency to get market pairs for. Only 1. (e.g. 'BTC')
	# start			int, optionally set the start to a different index in the pagination.
	# limit			int, optionally specify the number of results to return. 
	# convert		string, optionally convert the market pairs to a quote for up to 120 currencies. (e.g. 'BTC,USD')
	# convert_id    string, optionally convert the market pairs to a quote for up to 120 currencies. (e.g. '1,2781')
	#
	# WARNING: Completely untested, I don't have a paid plan.
	def market_pairs(self, coinId=None, slug=None, symbol=None, start=1, limit=100, convert=None, convert_id=None):

		url = self.root_url + 'cryptocurrency/market-pairs/latest'

		if not coinId and not slug and not symbol:
			err = { 'error' : 'No parameters provided.' }
			return err
		
		if not isinstance(start, int):
			err = { 'error' : 'Start must be an integer.' }
			return err

		if not isinstance(limit, int):
			err = { 'error' : 'Limit must be an integer.' }
			return err
		
		parameters = self._id_symbol(coinId, slug, symbol, {}, True)
		if 'error' in parameters:
			return parameters
		
		if start < 1:
			start = 1
		
		parameters['start'] = str(start)
		
		if limit < 1:
			limit = 1
		elif limit > 5000:
			limit = 5000
		
		parameters['limit'] = str(limit)

		parameters = self._convertparams(convert, convert_id, parameters)

		data = self.__call__(url, parameters)

		return data

	# Return the latest OHLCV (Open, High, Low, Close, Volume) market values for one or more
	# cryptocurrencies for the current UTC day. Since the current UTC day is still active these
	# values are updated frequently. 
	#
	# Inputs
	# coinID		string, one or more coin IDs for which to get data. See `map()`. (e.g. '1,4,5')
	# symbol		string, one or more symbols for which to get data. (e.g. 'BTC,ETH,LTC')
	# convert		string, optionally convert the data to a quote for up to 120 currencies. (e.g. 'BTC,USD')
	# convert_id    string, optionally convert the data to a quote for up to 120 currencies. (e.g. '1,2781')
	#
	# WARNING: Completely untested, I don't have a paid plan.
	def ohlcv_latest(self, coinId=None, symbol=None, convert=None, convert_id=None):

		url = self.root_url + 'cryptocurrency/ohlcv/latest'

		parameters = self._id_symbol(coinId, None, symbol, {}, True)
		parameters = self._convertparams(convert, convert_id, parameters)

		data = self.__call__(url, parameters)

		return data

	# Placeholder: Historical OHLCV
	#
	# Requires paid plan.

	# Placeholder: ALL EXCHANGE ENDPOINTS
	#
	# Requires paid plan.

	# Get the latest quote of aggregate market metrics. Use the 'convert' option
	# to return market values in multiple fiat and cryptocurrency conversions
	# in the same call.
	#
	# Prioritizes `convert` over `convert_id`.
	#
	# Inputs
	# convert       string, symbol(s) of currency to get metrics for.
	# convert_id    string, ID(s) of currency to get metrics for. See `map()`.
	def global_metrics(self, convert=None, convert_id=None):

		url = self.root_url + 'global-metrics/quotes/latest'

		parameters = {}
		parameters = self._convertparams(convert, convert_id, parameters)
		
		data = self.__call__(url, parameters)
		
		return data
	
	# Placeholder: Historical aggregate metrics
	#
	# Requires paid plan.

	# Convert `amount` of `coinId` or `symbol` to `convert` or `convert_id`.
	# Paid subscribers can get a conversion from a historical date.
	#
	# Prioritizes `coinId` over `symbol`.
	# Prioritizes `convert` over `convert_id`.
	#
	# Inputs
	# amount        float or int, amount of base currency to convert.
	# coinId        string, ID of base coin to convert from (e.g. '2'). See `map()`.
	# symbol        string, symbol of base coin to convert from (e.g. 'ETH').
	# convert       string, symbols of coins to convert to (e.g. 'BTC,USD,EUR'). Free plan limited to one.
	# convert_id    string, ID of coins to convert to (e.g. '1,42,57'). Free plan limited to one.
	# time          string, optional, Unix or ISO 8601 timestamp (e.g. '2018-02-24'). Paid only.
	def convert_price(self, amount, coinId=None, symbol=None, convert=None, convert_id=None, time=None):

		url = self.root_url + 'tools/price-conversion'

		parameters = self._id_symbol(coinId, None, symbol, {}, True)
		if 'error' in parameters:
			return parameters

		if not isinstance(amount, (int, float)):
			err = { 'error' : 'Amount must be int or float.' }
			return err
		if amount < 1e-8:
			err = { 'error' : 'Amount must be greater than 1e-8.' }
			return err
		elif amount > 1e9:
			err = { 'error' : 'Amount must be less than 1e9.' }
			return err
		
		parameters['amount'] = str(amount)
				
		if not convert and not convert_id:
			err = { 'error' : 'Must specify a currency to convert to.' }
			return err
		
		parameters = self._convertparams(convert, convert_id, parameters)

		if time:
			parameters['time'] = time
		
		data = self.__call__(url, parameters)
		
		return data
