import pandas as pd
from pathlib import Path
from path_definition import all_cities
from preprocessing import share_unassigned, to_remove, drop_if_contains, heat_conversion_factors
from values import system_efficiencies
import numpy as np

# PATHS
# folder_path = Path('Data/Geotermalna_energija/')
# file_name = 'toplotne_crpalke_ekosklad_energija.csv'

# read STA_SID identifiers
addresses = pd.read_csv(all_cities['root'] / all_cities['addresses_all'],
                        encoding='cp1250')

# read heat pumps
cols = ['Kolicina',
        'Leto_izplačila_spodbude',
        'Naslov',
        'Kraj',
        'Obcina',
        'Vrsta_ukrepa',
        'Qusable (kWh)',
        'Kolicina_energije_toplotne_crpalke (kWh)']


geothermal_path = all_cities['root'] / all_cities['geothermal_raw']
df = pd.read_csv(
    geothermal_path,
    usecols=cols,
    encoding='cp1250',
    sep=';',
    decimal=','
)
df.rename(
    columns={'Kolicina': 'GEOTHERMAL_kW',
             'Leto_izplačila_spodbude': 'INSTALLATION_YEAR',
             'Qusable (kWh)': 'GEOTHERMAL_kWh'},
    inplace=True
)

# collect types of heat pumps
df['Vrsta_ukrepa'] = df['Vrsta_ukrepa'].str.split().apply(lambda x: x[-3] + x[-2] + x[-1])

# create new columns for each type of geothermal heat pump
for c in df.Vrsta_ukrepa.unique():
        df[c.upper()] = 0
        df.loc[df.Vrsta_ukrepa == c, c.upper()] = 1


# modify address to match addresses and df
def clean_string_column(df, signs_to_remove, column):
    for s in signs_to_remove:
        df[column] = df[column].str.replace(s, '')
    return df


# modify address to match addresses in heat pumps
addresses['Obcina'] = addresses.OB_UIME.str.upper()
addresses['Naslov_'] = addresses.ADDRESS.str.upper()

addresses = clean_string_column(
    addresses,
    to_remove,
    column='Naslov_'
)


df['Naslov_'] = df.Naslov.str.upper()
df = clean_string_column(
    df,
    to_remove,
    column='Naslov_'
)


# generate final table
final = df.join(
    addresses.set_index(['Obcina', 'Naslov_']),
    on=['Obcina', 'Naslov_'],
    how='inner'
)


# remove last word from address and repeat
df['Naslov'].apply(lambda x: x.rpartition(',')[0])


# to resolve - most addresses are wrong, but not all
ind = set(df.index).difference(set(final.index))
unassigned = df.loc[ind]


# add entries with wrong municipality - address in eko_sklad matches single address in slovenia, but other municipality
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
final = final.append(tmp, sort=False)


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

df = drop_if_contains(df, 'Naslov', strings_to_drop)


# collect unassigned entries
ind = set(df.index).difference(set(final.index))
unassigned = df.loc[ind]


# assign addresses without last word in address in case word is a municipality and add to final table
for i in range(4):
    unassigned['Naslov'] = unassigned['Naslov'].apply(lambda x: x.rpartition(' ')[0])
    unassigned['Naslov_'] = unassigned['Naslov'].str.upper()
    unassigned = clean_string_column(unassigned, to_remove, column='Naslov_')

    tmp = unassigned.join(
        addresses.set_index(['Obcina', 'Naslov_']),
        on=['Obcina', 'Naslov_'],
        how='inner'
    )
    final = final.append(tmp, sort=False)


# to resolve - most addresses are wrong, but not all
share_unassigned(df, final)
# TODO improve 10.55% unassigned


# aggregate technologies to fit other sources
final['HEAT_PUMP_GROUND'] = final[['VODA-VODA', 'ZEMLJA-VODA']].max(axis=1)
final.rename(columns={'VODA(DIREKTNIUPARJALNIK)': 'GEOTHERMAL'}, inplace=True)

# heat conversion factors
final = heat_conversion_factors(final.copy(), system_efficiencies)


# keep only latest entry per STA_SID
final.reset_index(inplace=True)
ind = final.groupby('STA_SID')['INSTALLATION_YEAR'].idxmax()
final = final.loc[ind.values]


to_keep = [
           'INSTALLATION_YEAR',
           'HEAT_PUMP_GROUND',
           'GEOTHERMAL',
           'STA_SID',
           # 'OB_MID'
           ]
final = final[to_keep]

# save result
file_path = all_cities['root'] / all_cities['geothermal_cleaned']
final.to_csv(
    file_path,
    index=False,
)
print(f'\nFile saved to: {file_path}\n')
