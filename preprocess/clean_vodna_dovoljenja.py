from paths.path_definition import all_cities, city_paths
from preprocessing import address_to_sta_sid, heat_conversion_factors
import pandas as pd
from values import system_efficiencies


city_name = 'kranj'
paths = city_paths[city_name]


file_path = all_cities['root'] / paths['vodna_dovoljenja_raw']
df = pd.read_excel(
    file_path,
    usecols=['NASLOV', 'STEVILKA'],
)
df['INSTALLATION_YEAR'] = df.STEVILKA.str.replace('/', ' ').str.split().apply(lambda x: x[-1])

# read addresses
addresses_path = all_cities['root'] / all_cities['addresses_all']
addresses = pd.read_csv(
    addresses_path,
    encoding='cp1250',
)
addresses = addresses[addresses.OB_UIME.str.lower() == city_name.replace('_', ' ')]


# read out municipality
df.dropna(subset=['NASLOV'], inplace=True)
df['MUNICIPALITY'] = df.NASLOV.apply(lambda x: x.rpartition(',')[2])
df['ADDRESS'] = df.NASLOV.apply(lambda x: x.rpartition(',')[0])


# assign STA_SID building identifier
addresses['ADDRESS'] = addresses.ADDRESS.str.upper()
df_, unassigned = address_to_sta_sid(df, addresses, 'ADDRESS')
print(f'Unassigned entries: {round(unassigned.shape[0]/df_.shape[0]*100, 2)}%')


# drop entries without building identifier
df_ = df_[df_.STA_SID.notna()]
df_['HEAT_PUMP_GROUND'] = 1

# drop duplicate entries
final = df_[['STA_SID', 'INSTALLATION_YEAR', 'HEAT_PUMP_GROUND']].drop_duplicates()
final = final.astype('int')


# heat conversion factors
final = heat_conversion_factors(final.copy(), system_efficiencies)


# save result
file_path = all_cities['root'] / paths['vodna_dovoljenja_cleaned']
final.to_csv(
    file_path,
    columns=['STA_SID', 'INSTALLATION_YEAR', 'HEAT_PUMP_GROUND'],
    index=False,
)
