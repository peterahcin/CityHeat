import pandas as pd
from paths.path_definition import all_cities, city_paths
from values import OB_MID_dict, heated_area_codes
import pickle
from preprocessing import decode_column
import warnings
warnings.filterwarnings('ignore')


city_name = 'kranj'
paths = city_paths[city_name]
OB_MID = OB_MID_dict[city_name]


# read stavbe
# columns to load from tables
cols_stavbe = ['STA_SID',
               'OB_MID',
               'ST_ETAZ',
               'ST_PRIT_ETAZE',
               'ST_STANOVANJ',
               'ST_POSLOVNIH_PROSTOROV',
               'DEJANSKA_RABA',
               'ID_TIP_STAVBE',
               'LETO_IZG_STA',
               'LETO_OBN_STREHE',
               'LETO_OBN_FASADE',
               'ID_KONSTRUKCIJE',
               'ID_OGREVANJE']

stavbe_path = all_cities['root'] / all_cities['stavbe']
stavbe = pd.read_csv(
    stavbe_path,
    usecols=cols_stavbe,
    index_col='STA_SID',
    # encoding='cp1250',
    sep=';'
)
# keep only current municipality
df = stavbe[stavbe.OB_MID.eq(OB_MID)]


# read delistavb
cols_delistavb = ['STA_SID',
                  'DEJANSKA_RABA',
                  'UPOR_POV_STAN',
                  'NETO_TLORIS_POV_DST',
                  'LETO_OBN_OKEN',
                  'ID_POCIT_RABA']


delistavb_path = all_cities['root'] / all_cities['delistavb']
delistavb = pd.read_csv(
    delistavb_path,
    usecols=cols_delistavb,
    # encoding='cp1250',
    decimal=',',
    sep=';'
)
delistavb = delistavb[delistavb.STA_SID.isin(df.index.unique())]


# read sifranti
sifranti_path = all_cities['root'] / all_cities['sifranti']
sifranti = pd.read_csv(
    sifranti_path,
    # encoding='cp1250',
    sep=';'
)


# missing data
# drop entries where areas m2 not given
delistavb.fillna(0, inplace=True)

# collect total areas of building
df['UPORABNA_POVRSINA'] = delistavb.groupby('STA_SID')['UPOR_POV_STAN'].sum()
df['NETO_TLORIS'] = delistavb.groupby('STA_SID')['NETO_TLORIS_POV_DST'].sum()

# sum up heated area
ds = delistavb.loc[delistavb.DEJANSKA_RABA.isin(heated_area_codes)]
df['HEATED_AREA'] = ds.groupby('STA_SID')['UPOR_POV_STAN'].sum()
df.HEATED_AREA.fillna(0, inplace=True)

# drop nans
df.dropna(subset=['UPORABNA_POVRSINA', 'NETO_TLORIS'], inplace=True)


# load sector area use codes
use_codes_path = all_cities['root'] / 'values/use_codes_dict.pkl'
with open(use_codes_path, 'rb') as f:
    use_codes = pickle.load(f)


# sum areas by sector
for sector, n_values in use_codes.items():

    # read use codes from sifranti
    codes = sifranti.loc[sifranti.VREDNOST_N.isin(n_values)]['ID'].values

    # sum up use areas surfaces for sector
    ind = delistavb.DEJANSKA_RABA.isin(codes)
    df[sector] = delistavb.loc[ind].groupby('STA_SID')['UPOR_POV_STAN'].sum()
    df[sector].fillna(0, inplace=True)


# decode columns
for col in ['DEJANSKA_RABA', 'ID_TIP_STAVBE', 'ID_KONSTRUKCIJE', 'ID_OGREVANJE']:
    codes = set(df[col].dropna())
    categories = sifranti.set_index('ID').loc[codes].IME.values
    d = dict(zip(codes, categories))
    df = decode_column(df, col, d)


to_drop = ['ST_ETAZ',
           'ST_PRIT_ETAZE',
           'ST_STANOVANJ',
           'ST_POSLOVNIH_PROSTOROV',
           'DEJANSKA_RABA']

df.drop(to_drop, axis=1, inplace=True)


# collect area uses in one column
codes = set(delistavb['DEJANSKA_RABA'].dropna())
codes.remove(0)
categories = sifranti.set_index('ID').loc[codes].IME.values
d = dict(zip(codes, categories))
dejanska_raba = decode_column(delistavb, 'DEJANSKA_RABA', d)


# dejanska_raba = list_unique_values(dejanska_raba, 'DEJANSKA_RABA', groupby='STA_SID')
dejanska_raba.DEJANSKA_RABA = dejanska_raba.DEJANSKA_RABA.astype('str').apply(lambda x: x + ', ')
dejanska_raba = dejanska_raba.groupby('STA_SID')['DEJANSKA_RABA'].unique()
dejanska_raba = dejanska_raba.astype('str').str.replace("]", '')
dejanska_raba = dejanska_raba.str.replace("[", '')
dejanska_raba = dejanska_raba.str.replace("'", '')
dejanska_raba = dejanska_raba.str.rpartition(sep=',')[0]

df[col] = df[col].astype('str').apply(lambda x: x + ', ')
df_ = df.groupby('STA_SID')[col].unique()
df_ = df_.astype('str').str.replace("]", '')
df_ = df_.str.replace("[", '')
df_ = df_.str.replace("'", '')
df_ = df_.str.rpartition(sep=',')[0]


df['DEJANSKA_RABA'] = dejanska_raba
df = df[list(['DEJANSKA_RABA']) + list(df.columns[:-1])]

# save result
file_path = all_cities['root'] / paths['REN_cleaned']
df.to_csv(
    file_path,
)
