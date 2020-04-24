import pandas as pd
# mostly assume root of project is the current path where module is run so module imports should mostly follow that
# import dir.file
# import dir.dir.file.func
# etc...
from utils.preprocessing import add_fuel_from_measured_sources, calculate_fuel_from_conversion_factors, make_sum_table
from utils.preprocessing import total_fuel_consumption, fuel_consumption_by_type, fuels_by_share, add_system_info
from paths.path_definition import all_cities, city_paths
# try to avoid any implicit calls to user code in module imports
# Any module setup should go to __init__.py
# while values.py should contain the callable units
# consider what happens when a naked statment is left in value.values at the top level
# like:
# a=open('some_nonexsistant_file.csv')
#
# as soon as you do an import fuel_columns from values.values the above line still executes when the interpreter is
# trying to do loading of all dependecies. So this is not a runtime error but a "link time" problem. These are harder to
# troubleshoot by nature implicit and harder to think about.

from values.values import fuel_columns, na_fuel_efficiency, class_labels, class_borders, system_info_columns
import numpy as np
import pickle
import warnings
warnings.filterwarnings('ignore')


# load sector area use codes
# Why a pickle? There is no benefit and makes this unnecessarily complex.
use_codes_path = all_cities['root'] / 'values/use_codes_dict.pkl'
with open(use_codes_path, 'rb') as f:
    use_codes = pickle.load(f)

# I assume this is how you switch between cities. Try and use program arguments for this.
city_name = 'kranj'
paths = city_paths[city_name]

# Sections like these are ok but this should really be moved to a separate module like data_load or something similar
# Generally I'd try to unify the loading and having each source separated per code unit (class, function)
# Try and find common things that you can express as reusable units
# def read_source(path, **kwargs):
#     try:
#         return pd.read_csv(
#             path,
#             kwargs
#         )
#     except:
#         return pd.DataFrame()
#     finally:
#         pass
#
# SOURCES = [
#     all_cities['root'] / paths['REN_cleaned'], {'index_col': 'STA_SID'},
#     all_cities['root'] / paths['addresses_all'], {'encoding', 'cp1250'}
# ]
#
# for source_descriptor in SOURCES:
#     source = read_source(source_descriptor[0], source_descriptor[1])
# Generally the benefit in the above would be the common exception handling for all sources. Just as an example.
# You can do post processing and data correction in later steps. Generally follow DRY. Not only in python.


######################
# LOAD DATA SOURCES  #
######################

# REN register nepremicnin
file_path_REN = all_cities['root'] / paths['REN_cleaned']
REN = pd.read_csv(
    file_path_REN,
    index_col='STA_SID'
)

# addresses
addresses = pd.read_csv(
    all_cities['root'] / all_cities['addresses_all'],
    encoding='cp1250',
)

# gas consumption
try:
    dtype = {'ZP': 'int', 'STA_SID': 'int'}
    file_path_gas = all_cities['root'] / paths['gas_cleaned']
    gas = pd.read_csv(
        file_path_gas,
        usecols=['ZP', 'STA_SID'],
        dtype=dtype,
        index_col='STA_SID'
    )
    gas.rename(columns={'ZP': 'ZP'}, inplace=True)
except KeyError as ke:
    print(f'Key error: {ke}. Could not find cleaned file.')
    print('Setting: gas = pd.DataFrame()')
    gas = pd.DataFrame()
finally:
    gas.name = 'Dobava plina'


# plinski prikljucki
try:
    file_path_active_gas = all_cities['root'] / paths['active_gas_cleaned']
    active_gas = pd.read_csv(
        file_path_active_gas,
        index_col='STA_SID'
    )
except KeyError as ke:
    print(f'Key error: {ke}. Could not find cleaned file.')
    print('Setting: active_gas = pd.DataFrame()')
    active_gas = pd.DataFrame()
finally:
    active_gas.name = 'Plinski prikljucki'


# district heating


# skupne kotlovnice
file_path_kotlovnice = all_cities['root'] / paths['kotlovnice_cleaned']
kotlovnice = pd.read_csv(
    file_path_kotlovnice,
    index_col='STA_SID'
)
kotlovnice.name = 'Skupne kotlovnice'


# public buildings
file_path_public = all_cities['root'] / paths['public_cleaned']
public = pd.read_csv(
    file_path_public,
    index_col='STA_SID'
)
public.name = 'Javne stavbe'

# eko_sklad
file_path_eko_sklad = all_cities['root'] / all_cities['eko_sklad_cleaned']
eko_sklad = pd.read_csv(
    file_path_eko_sklad,
    index_col='STA_SID',
)
eko_sklad.name = 'Eko sklad'


# energetske izkaznice
file_path_energetske_izkaznice = all_cities['root'] / all_cities['energetske_izkaznice_cleaned']
audits = pd.read_csv(
    file_path_energetske_izkaznice,
    encoding='cp1250',
    index_col='STA_SID',
)
audits.name = 'Energetske izkaznice'


# evidim
file_path_evidim = all_cities['root'] / paths['evidim_cleaned']
evidim = pd.read_csv(
    file_path_evidim,
    encoding='cp1250',
    index_col='STA_SID',
    sep=','
)
evidim.name = 'Evidim'


# geothermal
file_path_geothermal = all_cities['root'] / all_cities['geothermal_cleaned']
geothermal = pd.read_csv(
    file_path_geothermal,
    index_col='STA_SID'
)
geothermal.name = 'Eko sklad crpalke'


# vodna dovoljenja
file_path_vodna_dovoljenja = all_cities['root'] / paths['vodna_dovoljenja_cleaned']
vodna_dovoljenja = pd.read_csv(
    file_path_vodna_dovoljenja,
    index_col='STA_SID'
)
vodna_dovoljenja.name = 'Vodna dovoljenja'

# temperature deficit
file_path_temp_deficit = all_cities['root'] / all_cities['temperature_deficit_cleaned']
temp_deficit = pd.read_csv(
    file_path_temp_deficit,
    encoding='cp1250',
    index_col='STA_SID'
)


# predicted heat consumption
heat_path = all_cities['root'] / paths['predicted_heat_total']
heat = pd.read_csv(
    heat_path,
    index_col='STA_SID'
)


# add addresses
addresses.drop_duplicates(subset='STA_SID', inplace=True)
REN = REN.join(addresses.set_index('STA_SID')[['ADDRESS', 'NA_MID']], how='left')
# REN = REN[list(['ADDRESS']) + list(REN.columns)]

# assemble building info, predicted heat consumption and temperature deficit
final = REN.join(heat[['PREDICTED_HEAT_m2', 'PREDICTED_HEAT_kWh']])
final = final.join(temp_deficit, how='left')
final.loc[final.TEMP_DEFICIT.isna(), 'TEMP_DEFICIT'] = final.TEMP_DEFICIT.median()


############################
# ADD HEATING SYSTEM INFO  #
############################

# add evidim heating system info
system_info_sources = [evidim, kotlovnice, vodna_dovoljenja, eko_sklad, geothermal]
for df_source in system_info_sources:
    add_system_info(
        final,
        df_source,
        system_info_columns
    )


#########################
# ADD FUEL CONSUMPTION  #
#########################

# calculate consumption from conversion factors and insert values from unmeasured sources
# sort sources by reliability - most reliable comes last
unmeasured_sources = [evidim, active_gas, kotlovnice, vodna_dovoljenja, eko_sklad, geothermal, audits]
for df_source in unmeasured_sources:
    calculate_fuel_from_conversion_factors(
        final,
        df_source,
        df_source.name,
        fuel_columns
    )


# insert fuel consumption values from measured sources
measured_sources = [public, gas]
for df_source in measured_sources:
    add_fuel_from_measured_sources(
        final,
        df_source,
        df_source.name,
        fuel_columns
    )


# where no data source available calculate NA_FUEL from predicted heat consumption
na_heat_to_fuel_conversion = 1/list(na_fuel_efficiency.keys())[0]
final.loc[final.DATA_SOURCE.isna(), 'NA_FUEL'] = final.PREDICTED_HEAT_kWh * na_heat_to_fuel_conversion
final.DATA_SOURCE.fillna('Ni vira', inplace=True)


# calculate fuel consumption per m2 - where NETO_TLORIS==0 insert 0
final['FINAL_ENERGY_m2'] = final[fuel_columns].sum(axis=1) / final['NETO_TLORIS']
final.replace(np.inf, 0, inplace=True)

to_int = [
    'OB_MID',
    'NA_MID',
    'LETO_IZG_STA',
    'LETO_OBN_STREHE',
    'LETO_OBN_FASADE',
    'TEMP_DEFICIT',
    'PREDICTED_HEAT_m2',
    'PREDICTED_HEAT_kWh',
    'ELKO',
    'ZP',
    'UNP',
    'BIOMASS',
    'PELETI',
    'SEKANCI',
    'POLENA',
    'NARAVNI_LES',
    'HEAT_PUMP_AIR',
    'HEAT_PUMP_GROUND',
    'SOLAR_THERMAL',
    'GEOTHERMAL',
    'DISTRICT_HEAT',
    'COAL',
    'NA_FUEL',
    'FINAL_ENERGY_m2'
]
final[to_int] = final[to_int].fillna(0)
final[to_int] = final[to_int].astype('int')


# adjust PREDICTED_HEAT_m2 with measured values
final.loc[final.PREDICTED_HEAT_m2 > final.FINAL_ENERGY_m2, 'PREDICTED_HEAT_m2'] = final.FINAL_ENERGY_m2 * 0.92

# add energy class variables
for i, j in zip(['PREDICTED_HEAT_m2', 'FINAL_ENERGY_m2'], ['USEFUL_ENERGY_CLASS', 'FINAL_ENERGY_CLASS']):
    for l, b in zip(class_labels, class_borders):
        final.loc[final[i].between(b[0], b[1], inclusive=True), j] = l


# select only buildings with >0 consumption
final = final[final[fuel_columns].sum(axis=1) > 0]


# add energy audit numbers
final = final.join(audits.card_number, how='left')


# make sum table
# load sectors / drop last entry in use_codes - unheated areas
sectors = list(use_codes)[:-1]
sum_table = make_sum_table(final, fuel_columns, sectors)


print('\nData source availability as % of buildings: \n')
print(round(final.DATA_SOURCE.value_counts(normalize=True)*100, 2))

print('\n', pd.DataFrame(
    {'Total MWh': round(fuel_consumption_by_type(sum_table).sort_values(ascending=False) / 1000).astype('int'),
     '[%]': round(fuels_by_share(sum_table).sort_values(ascending=False), 1)})
)

print('\nTotal consumption in MWh: ', int(total_fuel_consumption(sum_table) / 1000))


# remove nan
final.fillna('', inplace=True)


# save results
save_final_path = all_cities['root'] / all_cities['results'] / (city_name + '_whole.csv')
final.to_csv(
    save_final_path,
)


save_sum_table_path = all_cities['root'] / all_cities['results'] / (city_name + '_sum_table.csv')
sum_table.to_csv(
    save_sum_table_path,
)
