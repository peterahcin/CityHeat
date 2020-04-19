import pandas as pd
from paths.path_definition import all_cities, city_paths
from values import eff_dict, system_efficiencies
from preprocessing import heat_conversion_factors
from preprocessing import make_categorical_features

city_name = 'cerklje_na_gorenjskem'
paths = city_paths[city_name]


# read heating systems
kotlovnice_file_path = all_cities['root'] / paths['kotlovnice_raw']
kotlovnice = pd.read_excel(
    kotlovnice_file_path,
    # encoding='cp1250',
)


# read buildings
objekti_path = all_cities['root'] / paths['objekti_kotlovnice_raw']
objekti = pd.read_excel(objekti_path)

objekti.rename(
    columns={'_sid': 'STA_SID',
             '_ob_mid': 'OB_MID'},
    inplace=True
)


# age groups
age_groups = list(eff_dict.values())
# Add heating system efficiencies
efficiencies = list(eff_dict)


# keep last installation year and convert installation year to int
kotlovnice['INSTALLATION_YEAR'] = kotlovnice.leto_vgrad #.str.split().apply(lambda x: int(x.pop()))


objekti = objekti.join(
    kotlovnice[
        ['_kotl_id',
         'INSTALLATION_YEAR']
    ].set_index('_kotl_id'),
    on='_kotl_id'
)


# one hot encode fuels
fuel_cols = dict({
    'zemeljski plin': 'ZP',
    'ekstra lahko kurilno olje': 'ELKO',
    'kurilno olje': 'ELKO',
    'lesna biomasa': 'BIOMASS',
    # 'toplotna črpalka': 'HEAT_PUMP',
})
objekti = make_categorical_features(objekti, 'energent', fuel_cols)


# heat conversion factors
final = heat_conversion_factors(objekti.copy(), system_efficiencies)


to_keep = list(fuel_cols.values()) +\
          [
              'STA_SID',
              'INSTALLATION_YEAR'
          ]

# add fuel colums
to_keep += list(fuel_cols.values())

final = final[to_keep].copy()

# save result
final.to_csv(
    all_cities['root'] / paths['kotlovnice_cleaned'],
    index=False
)
