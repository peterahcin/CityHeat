import pickle
import pandas as pd
from path_definition import all_cities, city_paths, model
import numpy as np

city_name = 'cerklje_na_gorenjskem'
paths = city_paths[city_name]
model_name = 'model_13_04'
model_features = 'columns_' + model_name

# load input data set
file_path = all_cities['root'] / paths['input_for_prediction']
X = pd.read_csv(
    file_path
)

# load model
with open(all_cities['root'] / model['models'] / (model_name + '.pkl'), 'rb') as f:
    m = pickle.load(f)

# load corresponding columns
with open(all_cities['root'] / model['models'] / (model_features + '.pkl'), 'rb') as f:
    cols = pickle.load(f)

# make predictions (y - logpm1 of heat per m2 of heated area
heat_m2 = np.expm1(m.predict(X[cols]))

# load REN
REN_path = all_cities['root'] / paths['REN_cleaned']
df = pd.read_csv(
    REN_path,
)

# heat per m2 of heated area
df['PREDICTED_HEAT_m2'] = heat_m2
# total heat
df['PREDICTED_HEAT_kWh'] = df['PREDICTED_HEAT_m2'] * df['UPORABNA_POVRSINA']
# convert HEAT_m2 from HEAT per HEATED_AREA to HEAT per NETO_TLORIS - standard
df['PREDICTED_HEAT_m2'] = df['PREDICTED_HEAT_kWh'] / df['NETO_TLORIS']

to_keep = ['STA_SID', 'HEATED_AREA', 'UPORABNA_POVRSINA', 'NETO_TLORIS', 'PREDICTED_HEAT_kWh', 'PREDICTED_HEAT_m2']

save_file_path = all_cities['root'] / paths['predicted_heat_total']
df.to_csv(
    save_file_path,
    columns=to_keep,
    index=False
)
