import pandas as pd
from paths.path_definition import all_cities, city_paths
from values import OB_MID_dict

city_name = 'ljubljana'
paths = city_paths[city_name]
OB_MID = OB_MID_dict[city_name]

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


# read stavbe
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

cols_delistavb = ['STA_SID',
                  'DEJANSKA_RABA',
                  'UPOR_POV_STAN',
                  'NETO_TLORIS_POV_DST',
                  'LETO_OBN_OKEN',
                  'ID_POCIT_RABA']

# read delistavb
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

# drop entries where areas m2 not given
delistavb.fillna(0, inplace=True)

# collect total areas of building
stavbe['UPORABNA_POVRSINA'] = delistavb.groupby('STA_SID')['UPOR_POV_STAN'].sum()
stavbe['NETO_TLORIS'] = delistavb.groupby('STA_SID')['NETO_TLORIS_POV_DST'].sum()

# drop nans
stavbe.dropna(subset=['UPORABNA_POVRSINA', 'NETO_TLORIS'], inplace=True)

# get mean windows age
stavbe['LETO_OBN_OKEN'] = delistavb.groupby('STA_SID')['LETO_OBN_OKEN'].median().astype(int)

# add variable to represent the share of the area dedicated to second holiday houses/apartments
stavbe['SHARE_HOLIDAY'] = delistavb[delistavb['ID_POCIT_RABA'] == 1622].groupby('STA_SID')['UPOR_POV_STAN'].sum()
stavbe['SHARE_HOLIDAY'] = stavbe['SHARE_HOLIDAY'] / stavbe['UPORABNA_POVRSINA']
stavbe['SHARE_HOLIDAY'].fillna(0, inplace=True)


ORIGINAL_ATTRIBUTES = ['DEJANSKA_RABA',
                       'ID_KONSTRUKCIJE',
                       'ID_OGREVANJE']

NEW_ATTRIBUTES = ['NAMENSKA_RABA',
                  'MATERIAL_NOSILNE_KONSTRUKCIJE',
                  'VRSTA_OGREVANJA']


def decode_attributes(df):
    ''' takes original categorical attributes from stavbe and produces new attributes
    based on sifranti '''
    for attrib, new_attrib in zip(ORIGINAL_ATTRIBUTES, NEW_ATTRIBUTES):
        for i in df[attrib].dropna().unique():
            df.at[df[attrib] == i, new_attrib] = sifranti[sifranti.ID == i]['IME'].values[0]

    return df.drop(ORIGINAL_ATTRIBUTES, axis=1)


# decode ORIGINAL_ATTRIBUTES to NEW_ATTRIBUTES
stavbe = decode_attributes(stavbe)


# make categorical values with one hot encoder
def categorize(df, column):
    df_ = df.copy()
    cats = df_[column].unique()
    for c, v in enumerate(cats):
        new_col = column + '_' + str(c)
        df_[new_col] = 0
        df_.loc[df_[column] == v, new_col] = 1
    return df_.drop(column, axis=1)


# one hot encode category attributes
columns_one_hot_encode = ['NAMENSKA_RABA',
                          'MATERIAL_NOSILNE_KONSTRUKCIJE',
                          'VRSTA_OGREVANJA',
                          'ID_TIP_STAVBE']

for c in columns_one_hot_encode:
    stavbe = categorize(stavbe, column=c)


# create area use variables
area_use_cols = sifranti.loc[sifranti.POLJE_PK == 'DEJANSKA_RABA']['IME']
for c in area_use_cols:
    stavbe[c] = 0

areas_use = sifranti.loc[sifranti.POLJE_PK == 'DEJANSKA_RABA'][['ID', 'IME']]
# areas_use = dict(zip(areas_use.ID.values, areas_use.IME.values))
for r, c in zip(areas_use.ID.values, areas_use.IME.values):
    tmp = delistavb.loc[delistavb.DEJANSKA_RABA == r][['STA_SID', 'UPOR_POV_STAN']]
    stavbe.loc[tmp.STA_SID.values, c] = tmp['UPOR_POV_STAN'].values

# recreate STA_SID from INDEX
# stavbe.reset_index(inplace=True)
#
# # save result
# file_path = all_cities['root'] / paths['city_folder'] / paths['REN_cleaned']
# stavbe.to_csv(
#     file_path,
#     encoding='cp1250',
#     sep=',',
#     index=False
# )
#
# print(f'\nFile saved to: {file_path}\n')
