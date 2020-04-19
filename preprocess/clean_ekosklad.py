import pandas as pd
from paths.path_definition import all_cities
import numpy as np
from preprocessing import clean_string_column, to_remove, drop_if_contains, heat_conversion_factors, list_unique_values
from values import system_efficiencies


# PATHS
eko_sklad_folder = all_cities['root'] / all_cities['eko_sklad_folder']
file_name_base = 'Eko_sklad_'

# read STA_SID identifiers
addresses_path = all_cities['root'] / all_cities['addresses_all']
addresses = pd.read_csv(
    addresses_path,
    encoding='cp1250',
)


COLS_EKO_SKLAD = ['Naslov',
                  'Obcina',
                  'OpisaNamena',
                  'OpisKolicine',
                  'Velikost',
                  'Enota']

# list measures to be included in final table
HEAT_PUMP = ['vgradnja toplotne črpalke za pripravo sanitarne tople vode in/ali centralno ogrevanje stanovanjske stavbe',
             'vgradnja toplotne črpalke za centralno ogrevanje starejše stanovanjske stavbe',
             'vgradnja toplotne črpalke za centralno ogrevanje stanovanjske stavbe',
             'vgradnja toplotne črpalke za centralno ogrevanje stavbe']

BIOMASS = ['vgradnja kurilne naprave za centralno ogrevanje stanovanjske stavbe na lesno biomaso',
           'za ogrevanje na lesno biomaso',
           'vgradnja toplovodne kurilne naprave za centralno ogrevanje stanovanjske stavbe na lesno biomaso',
           'nova kurilna naprava na lesno biomaso, ki bo priklopljena na centralno ogrevanje',
           'novo kurilno napravo na lesno biomaso, ki zagotavlja toploto centralnemu sistemu ogrevanja',
           'zamenjava stare kurilne naprave na trda goriva z novo kurilno napravo na lesno biomaso, '
           'ki bo priklopljena na centralno ogrevanje',
           'vgradnja kurilne naprave na lesno biomaso za centralno ogrevanje stavbe']

GAS = ['vgradnja plinskega kondenzacijskega kotla za centralno ogrevanje starejše stanovanjske stavbe ']

SOLAR_THERMAL = ['vgradnja solarnega ogrevalnega sistema v stanovanjski stavbi']

BIOMASS_SECONDARY = ['novo enosobno kurilno napravo na lesno biomaso, namenjeno zlasti ogrevanju prostora, '
                     'v katerega je postavljena,'
                     'zamenjava stare kurilne naprave na trda goriva z novo enosobno kurilno napravo na lesno biomaso, '
                     'namenjeno zlasti ogrevanju prostora, v katerega je postavljena']

INSULATION = ['zamenjava zunanjega stavbnega pohištva pri obnovi stanovanjske stavbe',
              'toplotna izolacija fasade pri obnovi eno ali dvostanovanjske stavbe',
              'toplotna izolacija strehe oziroma podstrešja pri obnovi eno ali dvostanovanjske stavbe',
              'vgradnja lesenega zunanjega stavbnega pohištva pri obnovi stanovanjske stavbe',
              'toplotna izolacija fasade pri obnovi večstanovanjske stavbe',
              'toplotna izolacija strehe oziroma podstrešja pri obnovi večstanovanjske stavbe',
              'zamenjava zunanjega stavbnega pohištva v skupnih prostorih',
              'toplotna izolacija fasade pri obnovi stanovanjske stavbe'
              'za zamenjavo zunanjega stavbnega pohištva',
              'celovita obnova starejše eno- ali dvostanovanjske stavbe']

EFFICIENCY_INCREASE = ['vgradnja prezračevanja z vračanjem toplote odpadnega zraka v stanovanjski stavbi',
                       'vgradnja termostatskih ventilov in hidravlično uravnoteženje ogrevalnih sistemov',
                       'sistem delive stroškov za toploto',
                       'vgradnja prezračevanja z vračanjem toplote odpadnega zraka v starejši stanovanjski stavbi',
                       'optimizacija sistema ogrevanja']

measures = dict({'HEAT_PUMP_AIR': HEAT_PUMP,
                 'BIOMASS': BIOMASS,
                 'ZP': GAS,
                 'SOLAR_THERMAL': SOLAR_THERMAL,
                 'BIOMASS_SECONDARY': BIOMASS_SECONDARY}) #,
                 # 'INSULATION_eko_sklad': INSULATION,
                 # 'EFFICIENCY_INCREASE_eko_sklad': EFFICIENCY_INCREASE})

# create dataframe from eko sklad tables
eko_sklad = pd.DataFrame()
years = [2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
for year in years:

    file_name = file_name_base + str(year) + '.csv'
    file_path = eko_sklad_folder / file_name

    df = pd.read_csv(
        file_path,
        usecols=COLS_EKO_SKLAD,
        encoding='cp1250',
        low_memory=False,
        decimal=',',
        sep=';'
    )
    df['INSTALLATION_YEAR'] = year
    eko_sklad = pd.concat([eko_sklad, df])


# one hot encode eko_sklad measures in columns
for c, v in measures.items():
    eko_sklad[c] = 0
    eko_sklad.loc[eko_sklad['OpisaNamena'].isin(v), c] = 1

# drop unnecessary columns
eko_sklad.drop(
    columns=eko_sklad.columns[[3, 5]],
    axis=1,
    inplace=True
)
eko_sklad.rename(
    columns={'Velikost': 'kW_m2_stevilo',
             'OpisaNamena': 'Naziv vrsta naprave'},
    inplace=True
)

eko_sklad['kW_m2_stevilo'] = eko_sklad['kW_m2_stevilo'].astype('float').map('{:,.1f}'.format)

# drop entries referring to irrelevant measures
eko_sklad = eko_sklad[eko_sklad[measures.keys()].sum(axis=1) > 0]
print(eko_sklad.shape)
# drop duplicates
eko_sklad.drop_duplicates(inplace=True)

# set unique index
eko_sklad.reset_index(drop='index', inplace=True) #set_index(np.linspace(0, len(eko_sklad)-1, len(eko_sklad)), inplace=True)


# drop entries without address
eko_sklad.dropna(
    subset=['Naslov'],
    inplace=True
)

strings_to_drop = ['gradbeno dovoljenje', 'N.H.', ' NH']
eko_sklad = drop_if_contains(
    eko_sklad,
    'Naslov',
    strings_to_drop
)

eko_sklad['Naslov_'] = eko_sklad.Naslov.str.upper()
eko_sklad = clean_string_column(
    eko_sklad,
    to_remove,
    column='Naslov_'
)

# create Obcina column that matches the eko_sklad Obcina
addresses['Obcina'] = addresses.OB_UIME.str.upper()


# modify address to match addresses and eko_sklad
addresses['Naslov_'] = addresses.ADDRESS.str.upper()
addresses = clean_string_column(
    addresses,
    to_remove,
    column='Naslov_'
)


# create eko_sklad_address
eko_sklad_address = eko_sklad.join(
    addresses.set_index(['Obcina', 'Naslov_']),
    on=['Obcina', 'Naslov_'],
    how='inner'
)


# remove last word from address in case its a municipality
eko_sklad['Naslov'].apply(lambda x: x.rpartition(',')[0])


# to resolve - most addresses are wrong, but not all
ind = set(eko_sklad.index).difference(set(eko_sklad_address.index))
unassigned = eko_sklad.loc[ind]


# add entries with wrong municipality
# - listed address matches single address in slovenia, but other municipality
tmp = unassigned.drop(
    'Obcina',
    axis=1
).join(
    addresses.set_index(['Naslov_']),
    on=['Naslov_'],
    how='left'
)

tmp = tmp.drop_duplicates(
    subset=['Naslov_'],
    keep=False
).dropna(
    subset=['Obcina']
)

# add tmp final table
eko_sklad_address = eko_sklad_address.append(tmp, sort=False)

# to resolve - most addresses are wrong, but not all
strings_to_drop = ['NOVOGRADNJA',
                   'novogradnja',
                   ' N. H.',
                   'BH',
                   'NŠ',
                   'HŠ',
                   'BŠ',
                   'B.Š.',
                   'N.H']

eko_sklad = drop_if_contains(eko_sklad, 'Naslov', strings_to_drop)

# collect unassigned entries
ind = set(eko_sklad.index).difference(set(eko_sklad_address.index))
unassigned = eko_sklad.loc[ind]

# assign addresses without last word in address in case word is a municipality and add to final table
unassigned['Naslov_'] = unassigned['Naslov'].str.upper()
for i in range(4):
    unassigned['Naslov_'] = unassigned['Naslov_'].apply(lambda x: x.rpartition(' ')[0])
    unassigned = clean_string_column(unassigned, to_remove, column='Naslov_')

    tmp = unassigned.join(
        addresses.set_index(['Obcina', 'Naslov_']),
        on=['Obcina', 'Naslov_'],
        how='inner'
    )
    eko_sklad_address = eko_sklad_address.append(tmp, sort=False)


# collect unassigned entries
ind = set(eko_sklad.index).difference(set(eko_sklad_address.index))
unassigned = eko_sklad.loc[ind]
print(f'Unassigned entries: {round(unassigned.shape[0]/eko_sklad.shape[0]*100, 2)}%')
# TODO improve 6.95%

# heat conversion factors
eko_sklad_address = heat_conversion_factors(eko_sklad_address.copy(), system_efficiencies)


to_keep = [
           'kW_m2_stevilo',
           'Naziv vrsta naprave',
           'INSTALLATION_YEAR',
           'HEAT_PUMP_AIR',
           'BIOMASS',
           'ZP',
           # 'BIOMASS_SECONDARY',
           'SOLAR_THERMAL'
]

# average heat conversion factors per STA_SID - average means we assume if 2 systems per STA_SID each contributes 50%
fuel_cols = to_keep[3:]
final = eko_sklad_address.groupby('STA_SID')[fuel_cols].mean()


# add list of system info
tmp = eko_sklad_address.copy()
for col in ['kW_m2_stevilo', 'Naziv vrsta naprave', 'INSTALLATION_YEAR']:
    final[col] = list_unique_values(tmp, col, groupby='STA_SID')


# save result
file_path = all_cities['root'] / all_cities['eko_sklad_cleaned']
final.to_csv(
    file_path,
)

print(f'\nFile saved to: {file_path}\n')
