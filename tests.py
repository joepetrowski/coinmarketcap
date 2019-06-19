#%% Test Module
from pyCMC import CMC

with open('./cmc_key.key', 'r') as f:
    cmc_key = f.readline().strip()

cmc = CMC(cmc_key)

# Map
map_data = cmc.map()

if 'error' not in map_data.keys():
    print('Map works!')
else:
    print(map_data)

# Metadata
meta_data = cmc.metadata(slug='bitcoin,ethereum,litecoin')

if 'error' not in meta_data.keys():
    print('Metadata works!')
else:
    print(meta_data)

# Listings
listings = cmc.listings(start=1, limit=5, convert='USD', convert_id=None, sort='market_cap')

if 'error' not in listings.keys():
    print('Listings works!')
else:
    print(listings)
