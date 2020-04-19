import pandas as pd
from paths.path_definition import all_cities, city_paths
from values import system_efficiencies
from preprocessing import heat_conversion_factors
import warnings
warnings.filterwarnings('ignore')

city_name = 'cerklje_na_gorenjskem'
paths = city_paths[city_name]


# read plinski prikljucki
active_path = all_cities['root'] / paths['gas_active_raw']
active = pd.read_excel(
    active_path,
)


inactive_path = all_cities['root'] / paths['gas_inactive_raw']
inactive = pd.read_excel(
    inactive_path,
)


# read STA_SID identifiers
# sta_sid_path = all_cities['root'] / all_cities['stavbe']
# sta_sid = pd.read_csv(
#     sta_sid_path,
#     usecols=['STA_SID', 'KO_SIFKO', 'STEV'],
#     sep=';'
# )


active.rename(columns={'_sid': 'STA_SID'}, inplace=True)
# drop entries without STA_SID
active.dropna(subset=['STA_SID'], inplace=True)
# TODO some entries can be identified by the parcel number
active.drop_duplicates(inplace=True)

# indicate gas - ZP is the fuel to calcuate heat conversion factor
active['ZP'] = 1
# add INSTALLATION_YEAR to assign heat conversion factors - assume 2000 to get average system efficiency
active['INSTALLATION_YEAR'] = 2000
# heat conversion factors
active = heat_conversion_factors(active.copy(), system_efficiencies)


to_keep = ['STA_SID', 'ZP', 'INSTALLATION_YEAR']


# save result
file_path = all_cities['root'] / paths['active_gas_cleaned']
active.to_csv(
    file_path,
    columns=to_keep,
    index=False
)

print(f'\nFile saved to: {file_path}\n')