import pandas as pd
from pathlib import Path
from paths.path_definition import all_cities

PATH_ROOT = 'C:/Users/petera/Documents/Energy_Atlas_code/'
PATH_REN = 'Data/All_cities/REN_all_cities/'
file_name_naslovi = 'REN_SLO_stavba_naslovi_20191228.csv'
PATH_ADDRESSES = 'Data/All_cities/Naslovi/'
file_name_streets = 'SI.GURS.RPE.PUB.UL_VSE.csv'
file_name_house_numbers = 'SI.GURS.RPE.PUB.HS.csv'
file_name_municipalities = 'imena_obcin.csv'

all_streets_path = Path(PATH_ROOT) / PATH_ADDRESSES / file_name_streets
types_dict = {'UL_MID': int, 'UL_UIME': str, 'NA_MID': int, 'OB_MID': int}
streets = pd.read_csv(
    all_streets_path,
    dtype=types_dict,
    usecols=['UL_MID', 'UL_UIME', 'NA_MID', 'OB_MID'],
    sep=';'
)

all_house_numbers_path = Path(PATH_ROOT) / PATH_ADDRESSES / file_name_house_numbers
house_number_cols = ['Y_C', 'X_C', 'HS_MID', 'UL_MID', 'HS', 'LABELA']
house_numbers = pd.read_csv(
    all_house_numbers_path,
    usecols=house_number_cols,
    sep=';'
)

city_streets_path = Path(PATH_ROOT) / PATH_REN / file_name_naslovi
addresses = pd.read_csv(city_streets_path, sep=';')

municipalities_ = Path(PATH_ROOT) / PATH_ADDRESSES / file_name_municipalities
municipalities = pd.read_csv(
    municipalities_,
    encoding='cp1250',
    sep=','
)

stavbe_ = all_cities['root'] / all_cities['stavbe']
stavbe = pd.read_csv(stavbe_, sep=';')

# Delete duplicate STA_SID.
''' 
    In some cases more than one address is assigned to the same STA_SID.
    Since there is otherwise no way to distinguish between these building parts,
    we delete them.
'''
# naslovi.drop_duplicates(subset='STA_SID', keep='first', inplace=True)
# add house numbers
addresses = addresses.set_index('HS_MID').join(house_numbers.set_index('HS_MID'), on='HS_MID')
# add street names
addresses = addresses.set_index('UL_MID').join(streets.set_index('UL_MID'), on='UL_MID')
# add municipality names
addresses = addresses.join(municipalities.set_index('OB_MID'), on='OB_MID', how='outer')
# drop empty entries
addresses = addresses[addresses.HS > 0]
# drop zeros in house numbers
addresses.HS = addresses.HS.astype('int').astype('str')
# create addresses
addresses['ADDRESS'] = addresses.UL_UIME + ' ' + addresses.LABELA
# add KO_SIFKO and STEV
addresses = addresses.join(stavbe[['STA_SID', 'KO_SIFKO', 'STEV']].set_index('STA_SID'), on='STA_SID', how='left')

# convert round numbers to int
for c in ['X_C', 'Y_C', 'OB_MID', 'NA_MID']:
    addresses[c] = addresses[c].astype(int)

# save result
file_path = all_cities['root'] / all_cities['addresses_all']
addresses.to_csv(
    file_path,
    index=False,
    encoding='cp1250'
)
