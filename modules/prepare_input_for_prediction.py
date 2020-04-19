import pandas as pd
from paths.path_definition import all_cities, city_paths
from values import OB_MID_dict, area_use_codes, area_use_columns, heated_area_codes
from preprocessing import fill_and_mark, imputer_kNeighbors, missing_data, \
    one_hot_encode_column, decode_column
import warnings
warnings.filterwarnings('ignore')


city_name = 'cerklje_na_gorenjskem'
paths = city_paths[city_name]
OB_MID = OB_MID_dict[city_name]
surface_variable = 'UPORABNA_POVRSINA'
print(f'\nUsea areas normalized with: {surface_variable}.\n'
      f'Make sure surface_variable={surface_variable} in model!\n')

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
stavbe = stavbe[stavbe.OB_MID.eq(OB_MID)]
stavbe.drop('OB_MID', axis=1, inplace=True)


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
delistavb = delistavb[delistavb.STA_SID.isin(stavbe.index.unique())]


# read sifranti
sifranti_path = all_cities['root'] / all_cities['sifranti']
sifranti = pd.read_csv(
    sifranti_path,
    # encoding='cp1250',
    sep=';'
)


# read temperature deficit
file_path_temp_deficit = all_cities['root'] / all_cities['temperature_deficit_cleaned']
temp_deficit = pd.read_csv(
    file_path_temp_deficit,
    index_col='STA_SID',
    usecols=['TEMP_DEFICIT', 'STA_SID']
)

# add temperature deficit to main table
df = stavbe.join(temp_deficit, how='left')


# missing data
# drop entries where areas m2 not given
delistavb.fillna(0, inplace=True)

# collect total areas of building
df['UPORABNA_POVRSINA'] = delistavb.groupby('STA_SID')['UPOR_POV_STAN'].sum()
df['NETO_TLORIS'] = delistavb.groupby('STA_SID')['NETO_TLORIS_POV_DST'].sum()

# drop nans
df.dropna(subset=['UPORABNA_POVRSINA', 'NETO_TLORIS'], inplace=True)

# sum up heated area
ds = delistavb.loc[delistavb.DEJANSKA_RABA.isin(heated_area_codes)]
df['HEATED_AREA'] = ds.groupby('STA_SID')['UPOR_POV_STAN'].sum()
df.HEATED_AREA.fillna(0, inplace=True)

# get median window age of each building
df['LETO_OBN_OKEN'] = delistavb.groupby('STA_SID')['LETO_OBN_OKEN'].median().astype(int)


# MISSING DATA
# print out the ratios of missing values
missing_data(df)


# fill construction year with median and one hot encode the entry
v = df['LETO_IZG_STA'].median()
df = fill_and_mark(df, 'LETO_IZG_STA', v)


# If building rennovation year not given, set rennovation to construction year
for c in ['LETO_OBN_OKEN', 'LETO_OBN_STREHE', 'LETO_OBN_FASADE']:
    df['NA_'+c] = 0
    idx = (df[c].isna()) | (df[c] == 0)
    df.loc[idx, 'NA_'+c] = 1
    df.loc[idx, c] = df.loc[idx]['LETO_IZG_STA']


# fill missing data and one hot encode nans
for c in ['ID_TIP_STAVBE', 'ID_OGREVANJE', 'ID_KONSTRUKCIJE', 'DEJANSKA_RABA', 'TEMP_DEFICIT']:
    v = df[c].median()
    df = fill_and_mark(df, c, v)

# impute missing values in ST_ETAZ
df.loc[df['ST_ETAZ'].isna(), 'ST_ETAZ'] = (
    imputer_kNeighbors(
        df,
        attrib_to_impute='ST_ETAZ',
        reference='NETO_TLORIS',
        n_neighbors=3
    )
)

# impute missing values in ST_PRIT_ETAZE
df.loc[df['ST_PRIT_ETAZE'].isna(), 'ST_PRIT_ETAZE'] = (
    imputer_kNeighbors(
        df,
        attrib_to_impute='ST_PRIT_ETAZE',
        reference='NETO_TLORIS',
        n_neighbors=3
    )
)


# print out the ratios of missing values to check if any left
missing_data(df)


# ENGINEER new vars
# add variable to represent the share of the area dedicated to second holiday houses/apartments
df['SHARE_HOLIDAY'] = delistavb[delistavb['ID_POCIT_RABA'] == 1622].groupby('STA_SID')['UPOR_POV_STAN'].sum()
df['SHARE_HOLIDAY'] = df['SHARE_HOLIDAY'] / df['UPORABNA_POVRSINA']
df['SHARE_HOLIDAY'].fillna(0, inplace=True)


columns_one_hot_encode = ['ID_TIP_STAVBE',
                          'DEJANSKA_RABA',
                          'ID_KONSTRUKCIJE',
                          'ID_OGREVANJE']

# decode columns
for col in columns_one_hot_encode:
    codes = df[col].unique()
    categories = sifranti.loc[sifranti.ID.isin(codes)]['IME'].values
    d = dict(zip(codes, categories))
    df = decode_column(df, col, d)

for c in columns_one_hot_encode:
    df = one_hot_encode_column(df, column=c)


# CREATE AREA USE VARIABLES
# create first columns for new
for c in area_use_columns:
    df[c] = 0

# # drop STA_SID that are not in the final table
# delistavb = delistavb[delistavb.STA_SID.isin(df.index)]

# copy area surfaces into corresponding columns
for r, c in zip(area_use_codes, area_use_columns):
    tmp = delistavb.loc[delistavb.DEJANSKA_RABA == r][['STA_SID', 'UPOR_POV_STAN']]
    tmp = tmp.groupby('STA_SID')['UPOR_POV_STAN'].sum()
    df.loc[tmp.index, c] = tmp.values
    # t = df.loc[tmp.index, c]
    # print(round(t.sum()), round(tmp.values.sum()), ' ', c)

# make copy for final table
df_REN_cleaned = df.copy()

# normalize surface areas by total are of building - UPORABNA POVRSINA
for i in area_use_columns:
    df[i] = df[i]/df[surface_variable]

# finally fill are_use_columns where UPORABNA_POVRSINA==0 in above loop
df[area_use_columns] = df[area_use_columns].fillna(0)

# add YEAR to estimate consumption for - variable derived from model inputs collected over years
df['YEAR_MEASURED'] = 2019


# print out the ratios of missing values to check if any left
missing_data(df)


# save result
file_path = all_cities['root'] / paths['input_for_prediction']
df.to_csv(
    file_path,
)
print(f'Result saved to {file_path}')
# print(df[area_use_columns].sum())
