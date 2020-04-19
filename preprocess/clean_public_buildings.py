import pandas as pd
from paths.path_definition import city_paths
from paths.path_definition import all_cities
from preprocessing import make_categorical_features

city_name = 'kranj'
paths = city_paths[city_name]

HEAT_COL = 'raba toplotne energije [kWh] 2018' #'raba_energije_TE_[kWh]'
HEAT_COL_SECONDARY = 'raba toplotne energije [kWh] 2017'
cols = [
    # 'uporabna_povrsina',
    # 'neto_povrsina',
    'energenti',
    'energijsko število TE [kWh/m2]',
    # 'raba toplotne energije [kWh] 2016',
    'raba toplotne energije [kWh] 2017',
    HEAT_COL_SECONDARY,
    HEAT_COL,
    'sta_sid']

dtypes = {
    # 'uporabna_povrsina': 'int',
    # 'neto_povrsina': 'int',
    'energenti': 'str',
    'energijsko število TE [kWh/m2]': 'int',
    HEAT_COL: 'float',
    'sta_sid': 'int'}

public_path = all_cities['root'] / paths['public']
public = pd.read_csv(
    public_path,
    usecols=cols,
    # dtype=dtypes,
    encoding='cp1250',
    sep=';',
    decimal=','
)

public.rename(
    columns={'sta_sid': 'STA_SID'},
    inplace=True
)

# collect latest heat values
public['HEAT'] = public[HEAT_COL]

# if nan in latest year, collect values from previous year
ind = public.index[public['HEAT'].isna()]
public.loc[ind, 'HEAT'] = public.loc[ind, HEAT_COL_SECONDARY]

# make categorical features
fuel_cols = dict({
    'električna energija, zemeljski plin': 'ZP',
    'ekstra lahko kurilno olje, električna energija': 'ELKO',
    'ekstra lahko kurilno olje, električna energija, toplotna črpalka': 'ELKO_HEAT_PUMP',
    'električna energija, toplotna črpalka, zemeljski plin': 'ZP_HEAT_PUMP',
    'daljinska toplota, električna energija': 'DISTRICT_HEAT',
    'električna energija, lesna biomasa': 'BIOMASS',
    'brez, električna energija': 'NA_FUEL',
    'električna energija, toplotna črpalka': 'HEAT_PUMP_GROUND',
    'električna energija, utekočinjen naftni plin': 'UNP'
})

public = make_categorical_features(public, 'energenti', fuel_cols)

# assign fuel consumption
for c in fuel_cols.values():
    public[c] = public[c] * public['HEAT']

# drop nan
public.dropna(subset=['HEAT'], inplace=True)


# where ZP and HEAT_PUMP is the fuel divide equally between ZP and hEAT_PUMP
public.loc[public.ZP_HEAT_PUMP > 0, 'ZP'] = public[public.ZP_HEAT_PUMP > 0]['ZP_HEAT_PUMP'] * 0.5
public.loc[public.ZP_HEAT_PUMP > 0, 'HEAT_PUMP_GROUND'] = public[public.ZP_HEAT_PUMP > 0]['ZP_HEAT_PUMP'] * 0.5
public.loc[public.ELKO_HEAT_PUMP > 0, 'ELKO'] = public[public.ELKO_HEAT_PUMP > 0]['ELKO_HEAT_PUMP'] * 0.5
public.loc[public.ELKO_HEAT_PUMP > 0, 'HEAT_PUMP_GROUND'] = public[public.ELKO_HEAT_PUMP > 0]['ELKO_HEAT_PUMP'] * 0.5


to_keep = ['STA_SID',
           'ZP',
           'ELKO',
           'UNP',
           'DISTRICT_HEAT',
           'BIOMASS',
           'HEAT_PUMP_GROUND',
           'NA_FUEL',
           ]

final = public[to_keep]


# save result
file_path = all_cities['root'] / paths['public_cleaned']
final.to_csv(
    file_path,
    index=False,
)
