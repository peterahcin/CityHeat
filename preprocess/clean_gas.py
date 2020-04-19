import pandas as pd
from paths.path_definition import all_cities, city_paths

# city_name = 'ljubljana'
city_name = 'kranj'
paths = city_paths[city_name]
# cols = ['ZP', 'ADDRESS']#, 'HS']
cols = ['poraba kWh 2019', 'Naslov']

dtypes = {cols[0]: 'int', cols[1]: 'str'}
gas_path = all_cities['root'] / paths['gas_raw']
df = pd.read_excel(
    gas_path,
    usecols=cols,
    dtype=dtypes,
    # encoding='cp1250',
    # sep=','
)

df.rename(
    columns={cols[0]: 'ZP', cols[1]: 'ADDRESS'},
    inplace=True
)

# gas_path = Path('C:/Users/petera/Documents/Envirodual/data/ljubljana/gas/ljubljana_plin_2018.csv')
# gas = pd.read_csv(gas_path, thousands=',')
# gas.DOD.fillna('', inplace=True)
# df = gas.dropna(subset=['HS'])
# df.HS = df.HS.astype('int')
# df['ADDRESS'] = df.Ulica + df.HS.astype('str')
# df.HOUSEHOLDS.fillna(0, inplace=True)
# df.COMMERCIAL.fillna(0, inplace=True)
# df.Industrija.fillna(0, inplace=True)
# df['ZP'] = df.HOUSEHOLDS.astype('int') + df.COMMERCIAL.astype('int') + df.Industrija.astype('int')
# a=df.groupby('ADDRESS')['ZP'].sum()
# df = pd.DataFrame({'ADDRESS': a.index, 'ZP': a.values})
# df.to_csv('ljubljana_gas_2018.csv', columns=['ADDRESS', 'ZP'])

df.ZP.fillna(0, inplace=True)
df.dropna(subset=['ADDRESS'], inplace=True)
# df.ADDRESS = df.ADDRESS.apply(lambda x: x + ' ') + df.HS
# df = df[df.ZP_gas > 0]

df_c = df.copy()
addresses_path = all_cities['root'] / all_cities['addresses_all']
addresses = pd.read_csv(
    addresses_path,
    encoding='cp1250',
)

addresses = addresses[addresses.OB_UIME == city_name.capitalize()]


# remove symobols from addresses
def clean_string_column(df, signs_to_remove, column):
    df_ = df.copy()
    for s in signs_to_remove:
        df_[column] = df_[column].str.replace(s, '')
    return df_


addresses['ADDRESS'] = addresses.ADDRESS.str.upper()
to_remove = [r'C\.',
             r'UL\.',
             ' NH ',
             ' ',
             '/',
             ',',
             'ULICA',
             'CESTA',
             'NOVASTAVBA',
             'NOVOGRADNJA',
             r'\(',
             r'\)',
             '.']

addresses = clean_string_column(addresses, to_remove, 'ADDRESS')

df = df.groupby('ADDRESS')['ZP'].sum().reset_index()
df.ADDRESS = df.ADDRESS.str.upper()
df = clean_string_column(df, to_remove, 'ADDRESS')

# correct a few address peculiarities
df.ADDRESS = df.ADDRESS.str.replace('FRROZMANA-STANETA', 'FRANCAROZMANA-STANETA')

# join dataframe
final = df.join(addresses.set_index('ADDRESS'), on='ADDRESS', how='left')

unassigned = final[final.STA_SID.isna()]
unassigned = unassigned[unassigned.ADDRESS.str.findall(r'(\d+)').apply(lambda x: len(x) > 0)]

print(f'Unassigned entries: {round(unassigned.shape[0]/df.shape[0]*100, 2)}%')
# TODO unassigned: kranj: 3.4%, ljubljana: 0.23%

# drop unassigned
final = final[final.STA_SID.notna()]
final = final[final.ZP > 0]

# sum values for all addresses per STA_SID
tmp = final.groupby('STA_SID')['ZP'].sum().astype(int)
final = pd.DataFrame(
    {'STA_SID': tmp.index,
     'ZP': tmp.values})


final = final.astype('int')


# save result
file_path = all_cities['root'] / paths['gas_cleaned']
final.to_csv(
    file_path,
    columns=['ZP', 'STA_SID'],
    index=False,
)

