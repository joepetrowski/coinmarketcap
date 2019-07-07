#%% Test Module
from pyCMC import CMC

def test_results(returnVal, tname):
	if 'status' in returnVal.keys():
		if returnVal['status']['error_code'] == 0:
			print('{} works!'.format(tname))
		else:
			print('Error message: {}'.format(returnVal['status']['error_message']))
	else:
		print(returnVal)

with open('./cmc_key.key', 'r') as f:
	cmc_key = f.readline().strip()

cmc = CMC(cmc_key)

# Map
map_data = cmc.map()
test_results(map_data, 'Map')

# Metadata
meta_data = cmc.metadata(slug='bitcoin,ethereum,litecoin')
test_results(meta_data, 'Metadata')

# Listings
listings = cmc.listings(start=1, limit=5, convert='EUR', convert_id=None, sort='market_cap')
test_results(listings, 'Listings')

# Quotes
quotes = cmc.quotes(coinId=None, slug='ethereum')
test_results(quotes, 'Quotes')

# Global Metrics
metrics = cmc.global_metrics()
test_results(metrics, 'Metrics')

# Convert Price
convert = cmc.convert_price(2, coinId=None, symbol='ETH', convert='USD')
test_results(convert, 'Convert')

# These should return errors before calling the API
print('\nThe remaining functions should all return errors.\n')

# Listings
err_listings = cmc.listings(start=1, limit='10', convert='EUR', convert_id=None, sort='market_cap')
test_results(err_listings, 'Error Listings')

# Quotes
err_quotes = cmc.quotes(coinId=None, slug=None)
test_results(err_quotes, 'Error Quotes')

# Convert Price
err_convert = cmc.convert_price(1.5e9, coinId=None, symbol='ETH', convert='USD')
test_results(err_convert, 'Convert')
