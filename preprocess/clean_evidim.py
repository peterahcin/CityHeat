import pandas as pd
from paths.path_definition import all_cities, city_paths
from values import system_efficiencies
from preprocessing import heat_conversion_factors
import warnings
warnings.filterwarnings('ignore')

city_name = 'kranj'
paths = city_paths[city_name]


# read STA_SID identifiers
sta_sid_path = all_cities['root'] / all_cities['stavbe']
sta_sid = pd.read_csv(
    sta_sid_path,
    usecols=['STA_SID', 'KO_SIFKO', 'STEV'],
    sep=';'
)


# read file
COLS_EVIDIM = ['Šifra kurilne naprave',
               'Naziv namen naprave',
               'Naziv vrsta naprave',
               'Moc kurilne naprave',
               'Leto vgradnje',
               'Naziv vrsta goriva']

evidim_path = all_cities['root'] / paths['evidim_raw']
if str(evidim_path)[-3:].__eq__('csv'):
    evidim = pd.read_csv(evidim_path,
                         usecols=COLS_EVIDIM,
                         encoding='cp1250',
                         sep=';'
                         )
else:
    evidim = pd.read_excel(evidim_path,
                           usecols=COLS_EVIDIM,
                           encoding='cp1250',
                           sep=','
                           )


# biomass = ['Sekanci  - naprava z visokim izkoristkom',
#            'Naravni les v vseh oblikah (drva, Ĺľagovina, kosi, odrezki, lubje, storĹľi)',
#            'Naravni les v vseh oblikah (drva, žagovina, kosi, odrezki, lubje, storži)',
#            'Peleti - naprava z visokim izkoristkom',
#            'Polena - naprava z visokim izkoristkom']


sekanci = ['Sekanci  - naprava z visokim izkoristkom']


peleti = ['Peleti - naprava z visokim izkoristkom']


polena = ['Polena - naprava z visokim izkoristkom']


naravni_les = ['Naravni les v vseh oblikah (drva, Ĺľagovina, kosi, odrezki, lubje, storĹľi)',
               'Naravni les v vseh oblikah (drva, žagovina, kosi, odrezki, lubje, storži)']


UNP = ['UtekoÄŤinjeni naftni plin - UNP',
       'Utekočinjeni naftni plin - UNP']


ZP = ['Zemeljski plin']


ELKO = ['Lahko kurilno olje - ELKO']


fuels = dict({'ELKO': ELKO,
              'PELETI': peleti,
              'SEKANCI': sekanci,
              'POLENA': polena,
              'NARAVNI_LES': naravni_les,
              'UNP': UNP,
              'ZP': ZP})

# make fuel columns
for c, v in fuels.items():
    evidim[c] = 0
    evidim.loc[evidim['Naziv vrsta goriva'].isin(v), c] = 1

# clean table
evidim.dropna(inplace=True)

# space heating and hot water
space_heating_and_hot_water = ['Ogrevanje in priprava sanitarne vode']

# space heating
space_heating = ['Ogrevanje', 'Ogrevanje zraka']

# only hot water
only_hot_water = ['Priprava sanitarne vode']

# fireplace, furnace
fireplace_and_furnace = ['Lokalna kurilna naprava - kaminska peč',
                         'Centralna kurilna naprava - etažni kamin',
                         'Lokalna kurilna naprava - štedilnik',
                         'Centralna kurilna naprava - etažni štedilnik',
                         'Lokalna kurilna naprava - lončena peč',
                         'Lokalna kurilna naprava - kmečka peč',
                         'Lokalna kurilna naprava - odprti kamin']

# Where system not for heating purposes assign energy carrier as 'Other_fuel'
other_system = ['Drugo']


# make dummy columns for SYSTEMS
COLS = ['Naziv namen naprave',
        'Naziv namen naprave',
        'Naziv namen naprave',
        'Naziv vrsta naprave',
        'Naziv namen naprave']

CATS = (space_heating_and_hot_water,
        space_heating,
        only_hot_water,
        fireplace_and_furnace,
        other_system)

SYSTEMS = ['HEATING_AND_WATER',
           'HEATING',
           'HOT_WATER',
           'FIREPLACE_FURNACE',
           'OTHER']

for col, cat, s in zip(COLS, CATS, SYSTEMS):
    evidim[s] = 0
    evidim.loc[evidim[col].isin(cat), s] = 1


# System age 1950 if older than 1950
evidim['Leto vgradnje'].replace('Pred 1950', 1950, inplace=True)


# Where system age unknown assign median age
def replace_value_with_group_median(df, value_to_replace, col1, col2):
    '''
    replaces value_to_replace in col1 with median as grouped by col2
    '''
    df_copy = df.copy()
    groups = df_copy[df_copy[col1] == value_to_replace][col2].unique()
    for g in groups:
        m = df_copy[(df_copy[col2] == g) & (df_copy[col1] != value_to_replace)][col1].median()
        df_copy.loc[(df_copy[col2] == g) & (df_copy[col1] == value_to_replace), col1] = m
    return df_copy


evidim = replace_value_with_group_median(
    evidim,
    value_to_replace='Neznano',
    col1='Leto vgradnje',
    col2='Naziv vrsta goriva'
)

evidim['INSTALLATION_YEAR'] = evidim['Leto vgradnje'].astype('int32')


# Assign STA_SID according to KO_SIFKO and STEV
evidim['KO_SIFKO'] = evidim['Šifra kurilne naprave'].str.split('-').apply(lambda x: x[0]).astype('int32')
evidim['STEV'] = evidim['Šifra kurilne naprave'].str.split('-').apply(lambda x: x[1]).astype('int32')

evidim.drop(
    columns=[
        'Šifra kurilne naprave',
        # 'Naziv namen naprave',
        # 'Naziv vrsta naprave',
        'Naziv vrsta goriva'],
    inplace=True
)


# filter out latest installations
def filter_latest_installation(df, system, index_cols=['KO_SIFKO', 'STEV'], date_col='INSTALLATION_YEAR'):
    df_copy = df.copy()
    idx = df_copy[df_copy[system] == 1].groupby(index_cols)[date_col].idxmax()

    return df_copy.loc[idx]


# compile table of filtered latest installed systems
evidim_cleaned = pd.DataFrame(columns=evidim.columns)
for i in SYSTEMS:
    evidim_cleaned = evidim_cleaned.merge(
        filter_latest_installation(evidim, i),
        how='outer'
    )

# add STA_SID to evidim
final = evidim_cleaned.join(
    sta_sid.set_index(['KO_SIFKO', 'STEV']),
    on=['KO_SIFKO', 'STEV'],
    how='inner'
)


final.rename(
    columns={'Moc kurilne naprave': 'kW_m2_stevilo'},
    inplace=True
)


to_keep = [
    'Naziv namen naprave',
    'Naziv vrsta naprave',
    'kW_m2_stevilo',
    'INSTALLATION_YEAR',
    'STA_SID',
    'ELKO',
    # 'BIOMASS',
    'PELETI',
    'SEKANCI',
    'POLENA',
    'NARAVNI_LES',
    'UNP',
    'ZP',
    # 'HEATING_AND_WATER',
    # 'HEATING',
    # 'HOT_WATER',
    # 'FIREPLACE_FURNACE',
    # 'OTHER'
    ]


# heat conversion factors
final = heat_conversion_factors(final.copy(), system_efficiencies)


# save result
save_file = all_cities['root'] / paths['evidim_cleaned']
final.to_csv(
    save_file,
    columns=to_keep,
    encoding='cp1250',
    index=False
)
print('Cleaned EVIDIM with success.')
