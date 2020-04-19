import pandas as pd
import numpy as np
from path_definition import all_cities, model
import warnings
from values import heated_area_cols, area_use_columns
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
# from sklearn.base import BaseEstimator, TransformerMixin, RegressorMixin, clone
# from sklearn.metrics import mean_squared_error

import xgboost as xgb
# from xgboost import plot_importance, plot_tree
# from sklearn.metrics import mean_squared_error, mean_absolute_error

import math
import pickle

kranj_path = all_cities['root'] / model['gas_kranj']
gas_kranj = pd.read_csv(
    kranj_path,
    index_col='STA_SID',
)
print(f'\n Data set size: {gas_kranj.shape}')


ljubljana_path = all_cities['root'] / model['gas_ljubljana']
gas_ljubljana = pd.read_csv(
    ljubljana_path,
    index_col='STA_SID',
)
print(f'\n Data set size: {gas_ljubljana.shape}')


gas_ljubljana['YEAR_MEASURED'] = 2017
gas_kranj['YEAR_MEASURED'] = 2019


# df_raw = pd.concat([gas_kranj, gas_ljubljana])
df_raw = gas_kranj
print(f'\n Data set size: {df_raw.shape}')


# drop buildings with 0 m2 surface area
df = df_raw.copy()
df = df[df['UPORABNA_POVRSINA'] > 5]
df = df[df['NETO_TLORIS'] > 5]


# create variable heat per m2
independent_var = 'heat_m2'
surface_variable = 'UPORABNA_POVRSINA'

# columns energy consumption - quantities before conversion to heat
fuel_columns = 'ZP_gas'

# add all fuel consumption (converted to heat) + all forms of delivered heat
conversion_efficiency = 0.95
# df[independent_var] = df[fuel_columns] * conversion_efficiency / df[heated_area_cols].sum(axis=1)
df[independent_var] = df[fuel_columns] * conversion_efficiency / df[surface_variable]

# cutoff
lower = 10
upper = 1300
df = df[df[independent_var] < upper]
df = df[df[independent_var] > lower]


independent_var = 'log1p_heat_m2'
df['log1p_heat_m2'] = np.log1p(df['heat_m2'])
df = df.drop(columns='heat_m2')


# drop irrelevant variables
df.drop(columns=fuel_columns, inplace=True)
df.drop(columns='OB_MID', inplace=True)


for i in area_use_columns:
    df[i] = df[i]/df[surface_variable]


# Split set into train and test set
train_set, test_set = train_test_split(df, test_size=0.0005, random_state=42)

df_trn = train_set.drop(independent_var, axis=1)
y_trn = train_set[independent_var].copy()

X_test = test_set.drop(independent_var, axis=1)
y_test = test_set[independent_var].copy()


# make validation set
def split_vals(a, n):
    return a.iloc[:n].copy(), a.iloc[n:].copy()


n_valid = 700
n_trn = len(df_trn)-n_valid

X_train, X_valid = split_vals(df_trn, n_trn)
y_train, y_valid = split_vals(y_trn, n_trn)
raw_train, raw_valid = split_vals(train_set, n_trn)


def rmse(x, y): return math.sqrt(((x-y)**2).mean())


def print_score(m):
    res = ['RMSE train:', round(rmse(m.predict(X_train), y_train), 5),
           'RMSE valid:', round(rmse(m.predict(X_valid), y_valid), 5),
           'R2 train:', round(m.score(X_train, y_train), 5),
           'R2 valid:', round(m.score(X_valid, y_valid), 5)]
    if hasattr(m, 'oob_score_'):
        res.append(['R2 oob_score_', round(m.oob_score_, 5)])
    print(res)


m = RandomForestRegressor(
    n_estimators=800,
    min_samples_leaf=3,
    max_features=0.55,
    n_jobs=-1,
    oob_score=True
)
# m = xgb.XGBRegressor(colsample_bytree=0.4603, gamma=0.0468, learning_rate=0.05,
#                      max_depth=3, min_child_weight=1.7817, n_estimators=800,
#                      reg_alpha=0.4640, reg_lambda=0.8571, subsample=0.5213,
#                      silent=1, random_state=7, nthread=-1)
m.fit(X_train, y_train)
print_score(m)


fi = pd.DataFrame({'cols': X_valid.columns,
                   'imp': m.feature_importances_}).sort_values(
    'imp',
    ascending=False
)

to_keep = fi[fi.imp > 0.003].cols


df_keep = df_trn[to_keep].copy()
keep_cols = df_keep.columns
X_train, X_valid = split_vals(df_keep, n_trn)
X_test = X_test[keep_cols]

m1 = RandomForestRegressor(
    n_estimators=800,
    min_samples_leaf=3,
    max_features=0.55,
    n_jobs=-1,
    oob_score=True
)
# m1 = xgb.XGBRegressor(colsample_bytree=0.4603, gamma=0.0468, learning_rate=0.05,
#                       max_depth=3, min_child_weight=1.7817, n_estimators=800,
#                       reg_alpha=0.4640, reg_lambda=0.8571, subsample=0.5213,
#                       silent=1, random_state=7, nthread=-1)
m1.fit(X_train, y_train)
print_score(m1)

fi = pd.DataFrame({'cols': X_valid.columns,
                   'imp': m1.feature_importances_}).sort_values(
    'imp',
    ascending=False
)

fi.set_index('cols')[:30].plot.barh(figsize=(12, 9), legend=False)


# save model
model_designation = '_13_04.pkl'
model_path = all_cities['root'] / ('prediction_models/model' + model_designation)
with open(model_path, 'wb') as f:
    pickle.dump(m1, f)

columns_path = all_cities['root'] / ('prediction_models/columns_model' + model_designation)
with open(columns_path, 'wb') as f:
    pickle.dump(to_keep, f)
