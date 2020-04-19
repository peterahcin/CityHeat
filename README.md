# CityHeat
The code is used to calculate a municipality's fuel consumption based on somewhat standardized data sources:

- evidim
- energetske izkaznice (building energy audits)
- eko sklad (registered subsidies for biomass systems and heat pumps)
- plinski priljucki (info about active and inactive gas consumers)
- plin (measured gas deliveries)
- daljinjska toplota (measured district heat deliveries)
- REN (state registry - info on individual building characteristics)
- temperaturni primanjklaj (temperature derived indicator of heat demand)
- public buildings measured consumption
- small scale district heating systems - can include measured deliveries or just addresses and/or building identifiers

Preprocess data sources with corresponding scripts in the preprocess folder. 
Depending on how a particular municipality collects and organizes its data, you will need to make small adjustments in the script.

After the scripts are preprocessed run scripts with municipality name in lowercase:

- prepare_input_for_prediction.py (this script all the necessary building info for the prediction model)
- generate_predictions.py (predicts heat consumption per m2 for each building in city)
- main.py (generates table containing heat and all fuel consumption for each building and a summary table by sectors)
