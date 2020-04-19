import pandas as pd
from pathlib import Path
from paths.path_definition import all_cities, city_paths

city_name = 'ljubljana'
paths = city_paths[city_name]


# read district heating data
sheet1 = '2017_01-06'
sheet2 = '2017_07-12'

# file is big so read first sheet1 January to June
df1 = pd.read_excel(
    Path('C:/Users/petera/Documents/Envirodual/data/ljubljana/district_heat/district_heat.xlsx'),
    usecols=['Količina.3', 'Ulica', 'HŠ'],
    sheet_name=sheet1)

# read sheet2 July to December
df2 = pd.read_excel(
    Path('C:/Users/petera/Documents/Envirodual/data/ljubljana/district_heat/district_heat.xlsx'),
    usecols=['Količina.3', 'Ulica', 'HŠ'],
    sheet_name=sheet2)

df = pd.concat([df1, df2])


df.rename(columns={'Količina.3': 'DISTRICT_HEAT_dh'}, inplace=True)
df.DISTRICT_HEAT_dh.fillna(0, inplace=True)
df['ADDRESS'] = df.Ulica.apply(lambda x: str(x) + ' ') + df.HŠ
d = df.groupby('ADDRESS')['DISTRICT_HEAT_dh'].sum()
d = pd.DataFrame({'ADDRESS': d.index, 'DISTRICT_HEAT_dh': d.values})
d = d[d.DISTRICT_HEAT_dh > 0]


# read addresses
addresses_path = all_cities['root'] / all_cities['addresses_all']
addresses = pd.read_csv(
    addresses_path,
    encoding='cp1250',
)

addresses = addresses[addresses.OB_UIME == city_name.capitalize()]


# remove symbols from addresses
from preprocessing import clean_string_column, to_remove

addresses['ADDRESS'] = addresses.ADDRESS.str.upper()

addresses = clean_string_column(addresses, to_remove, 'ADDRESS')

df = df.groupby('ADDRESS')['DISTRICT_HEAT_dh'].sum().reset_index()
df.ADDRESS = df.ADDRESS.str.upper()
df = clean_string_column(df, to_remove, 'ADDRESS')

# correct a few address peculiarities
# df.ADDRESS = df.ADDRESS.str.replace('FRROZMANA-STANETA', 'FRANCAROZMANA-STANETA')

# join dataframe
final = df.join(addresses.set_index('ADDRESS'), on='ADDRESS', how='left')

unassigned = final[final.STA_SID.isna()]
unassigned = unassigned[unassigned.ADDRESS.str.findall(r'(\d+)').apply(lambda x: len(x) > 0)]

print(f'Unassigned entries: {round(unassigned.shape[0]/df.shape[0]*100, 2)}%')
# TODO ljubljana: 0.23%

# drop unassigned
final = final[final.STA_SID.notna()]
final = final[final.DISTRICT_HEAT_dh > 0]


# sum values for all addresses per STA_SID
tmp = final.groupby('STA_SID')['DISTRICT_HEAT_dh'].sum()
final = pd.DataFrame(
    {'STA_SID': tmp.index,
     'DISTRICT_HEAT_dh': tmp.values})


final.DISTRICT_HEAT_dh = final.DISTRICT_HEAT_dh.apply(lambda x: x*1000)
final = final.astype('int')

# save result
file_path = all_cities['root'] / paths['city_folder'] / paths['district_heat_cleaned']
final.to_csv(
    file_path,
    columns=['DISTRICT_HEAT_dh', 'STA_SID'],
    index=False,
)
