from paths.path_definition import all_cities
from preprocessing import remove_symbols_from_series
import pandas as pd

addresses_path = all_cities['root'] / all_cities['addresses_all']
addresses = pd.read_csv(
    addresses_path,
    encoding='cp1250',
)

cols = [#'building_community',
        'card_number',
        #'epdb_classification',
        'building_identification',
        'au',
        'qfh_au',
        'qfw_au',
        'energy_elko',
        'energy_unp',
        'energy_zp',
        'energy_dt',
        'energy_lb',
        'energy_p',
        'energy_e',
        'energy_sse',
        'energy_se',
        'energy_to',
        'energy_ge',
        'energy_dteu',
        'energy_dtlb']

file_path = all_cities['root'] / all_cities['energetske_izkaznice_raw']
audits = pd.read_csv(
    file_path,
    usecols=cols,
    encoding='cp1250',
    thousands='.',
    low_memory=False,
    sep=';'
)

audits.rename(columns={'building_community': 'Municipality',
                       'qfw_au': 'HOT_WATER_m2',
                       'energy_elko': 'ELKO',
                       'energy_unp': 'UNP',
                       'energy_zp': 'ZP',
                       'energy_dt': 'DISTRICT_HEAT',
                       'energy_lb': 'BIOMASS',
                       'energy_p': 'COAL',
                       'energy_e': 'EL',
                       'energy_sse': 'SOLAR_THERMAL',
                       'energy_se': 'PV',
                       'energy_to': 'HEAT_PUMP_AIR',
                       'energy_ge': 'GEOTHERMAL',
                       'energy_dteu': 'DISTRICT_HEAT_HIGH_EFF',
                       'energy_dtlb': 'DISTRICT_HEAT_BIOMASS'},
              inplace=True)

audits.fillna(0, inplace=True)
# drop entries with zero surface area
audits = audits[audits.au > 0]

fuel_cols = ['ELKO',
             'UNP',
             'ZP',
             'DISTRICT_HEAT',
             'BIOMASS',
             'COAL',
             'SOLAR_THERMAL',
             'HEAT_PUMP_AIR',
             'GEOTHERMAL',
             'DISTRICT_HEAT_HIGH_EFF',
             'DISTRICT_HEAT_BIOMASS']

# drop entries with no fuel consumption
audits['TOTAL_FUEL'] = audits[fuel_cols].sum(axis=1)
audits = audits[audits.TOTAL_FUEL > 0]

# Calculate heat and hot water per m2
audits['FUEL_m2'] = audits['TOTAL_FUEL'] / audits.au


# Eliminate duplicated and triplicated fuel entries (same quantity given for different fuels)
def delete_duplicate_entries_wrapper(func):
    def wrapper(df, *args):
        print(' - Of duplicate fuel entries: ', args, '\n', ' ' * 23, 'set: ', args[:-1], 'to 0.')
        return func(df, *args)
    return wrapper


# @delete_duplicate_entries_wrapper
def eliminate_entries_with_multiple_entry_fuels(df, *args):
    '''
    Looks for entries in ENERGETSKE IZKAZNICE where the fuel for heating is given in approx equal amounts of
    multiple fuels, resulting in a multiple of the actual fuel consumed.

    The method performs a test:
        If FUEL_m2 - total sum of fuels divided by surface area - is a multiple of qfh_au
        & the fuel amounts are approx. equal.
        => set all but last column values in args to 0.
    '''
    number_fuels = len(args)

    upper_bound = number_fuels * 1.25
    lower_bound = number_fuels * 0.75

    ind_bool = (df.FUEL_m2 / df.qfh_au <= upper_bound) & (df.FUEL_m2 / df.qfh_au >= lower_bound)

    for arg1 in args[:-1]:
        for arg2 in list(set(args[1:]).difference([arg1])):
            ind_bool = ind_bool & (df[arg1] / df[arg2] <= 1.3) & (df[arg1] / df[arg2] >= 0.7)

    df.loc[df[ind_bool].index, args[:-1]] = 0
    return df


# Set high efficiency district heating to 0 where already included as biomass
audits.loc[audits['DISTRICT_HEAT_HIGH_EFF'] == audits['DISTRICT_HEAT_BIOMASS'], 'DISTRICT_HEAT_HIGH_EFF'] = 0
print(' - Of duplicate fuel entries: DISTRICT_HEAT_HIGH_EFF, set DISTRICT_HEAT_BIOMASS to 0')

# Set district heating to 0 where already included as heat pump
audits.loc[audits['DISTRICT_HEAT'] == audits['HEAT_PUMP_AIR'], 'DISTRICT_HEAT'] = 0
print(' - Of duplicate fuel entries: (district heating, heat_pump) set: district to 0')

# Set solar_thermal to 0 where already included as  solar PV
audits.loc[audits['SOLAR_THERMAL'] == audits['PV'], 'SOLAR_THERMAL'] = 0
print(' - Set solar thermal entries 0 where equal to solar PV - assumed duplicate')


# Where e_s approx. 2x/3x/4x qfh_au and the fuel quantities are almost equal set all but last fuel to 0
eliminate_entries_with_multiple_entry_fuels(audits, 'ELKO', 'ZP', 'BIOMASS')
eliminate_entries_with_multiple_entry_fuels(audits, 'ELKO', 'BIOMASS')
eliminate_entries_with_multiple_entry_fuels(audits, 'ELKO', 'ZP')
eliminate_entries_with_multiple_entry_fuels(audits, 'ZP', 'BIOMASS')
eliminate_entries_with_multiple_entry_fuels(audits, 'UNP', 'BIOMASS')
eliminate_entries_with_multiple_entry_fuels(audits, 'DISTRICT_HEAT', 'BIOMASS')
eliminate_entries_with_multiple_entry_fuels(audits, 'GEOTHERMAL', 'HEAT_PUMP_AIR')
eliminate_entries_with_multiple_entry_fuels(audits, 'DISTRICT_HEAT', 'HEAT_PUMP_AIR')


# Where heat pump 4.7x geothermal store value as geothermal_heat_pump
ind = (audits.HEAT_PUMP_AIR / audits.GEOTHERMAL * 10).round() == 47
audits.loc[ind, 'HEAT_PUMP_47'] = audits[ind]['HEAT_PUMP_AIR']
audits.loc[ind, ['HEAT_PUMP_AIR', 'GEOTHERMAL']] = 0
audits.HEAT_PUMP_47.fillna(0, inplace=True)

print(' - Set HEAT_PUMP_47 to HEAT_PUMP_AIR where HEAT_PUMP_AIR/GEOTHERMAL = 4.7')
print('- ' * 40, '\n')

# Add HEAT_PUMP_47 to heat and hot water per m2
fuel_cols.append('HEAT_PUMP_47')

# Recalculate FUEL_m2
audits['FUEL_m2'] = audits[fuel_cols].sum(axis=1) / audits.au

# Calculate electricity per m2 over normal non-heat consumption 30 kWh/m2
audits['EL_m2'] = audits.EL / audits.au - 30

# if all fuels == 0 use values qfh_au and hot_water_per_m2
audits.loc[audits.FUEL_m2 == 0, 'FUEL_m2'] = audits[audits.FUEL_m2 == 0][['qfh_au', 'HOT_WATER_m2']].sum(axis=1)

# Convert all values to int for smooth reading
audits[fuel_cols] = audits[fuel_cols].round().astype('int')

# Select indices of seemingly correct entries
ind_correct = audits[((audits.FUEL_m2 - audits.qfh_au).abs() < 0.35 * audits.FUEL_m2)
                     | ((audits.FUEL_m2 - audits.qfh_au - audits.HOT_WATER_m2).abs() < 0.35 * audits.FUEL_m2)
                     | ((audits.FUEL_m2 - audits.qfh_au).abs() < 20)
                     | ((audits.FUEL_m2 - audits.qfh_au - audits.HOT_WATER_m2).abs() < 20)
                     | ((audits.FUEL_m2 + audits.EL_m2 - audits.qfh_au).abs() < 0.35 * audits.FUEL_m2)
                     | ((audits.FUEL_m2 + audits.EL_m2 - audits.qfh_au - audits.HOT_WATER_m2).abs() < 0.35 * audits.FUEL_m2)
                     | ((audits.FUEL_m2 + audits.EL_m2 - audits.qfh_au).abs() < 20)
                     | ((audits.FUEL_m2 + audits.EL_m2 - audits.qfh_au - audits.HOT_WATER_m2).abs() < 20)
                     | (audits.HEAT_PUMP_47 > 0)].index


# Read building identifiers
audits['DELI_STAVBE'] = audits['building_identification'].str.findall('(\d+)').apply(lambda x: [int(i) for i in x])
audits['KO_SIFKO'] = audits['DELI_STAVBE'].apply(lambda x: x.pop(0) if len(x) > 0 else 0)
audits['STEV'] = audits['DELI_STAVBE'].apply(lambda x: x.pop(0) if len(x) > 0 else 0)


# if individual building parts not listed set column ENTIRE_BUILDING to 1
audits['ENTIRE_BUILDING'] = 0
audits.loc[audits.DELI_STAVBE.apply(lambda x: len(x) == 0), 'ENTIRE_BUILDING'] = 1


# connect to STA_SID
audits = audits.join(
    addresses[['STA_SID', 'KO_SIFKO', 'STEV']].set_index(['KO_SIFKO', 'STEV']),
    on=['KO_SIFKO', 'STEV'],
    how='left'
)
audits.drop_duplicates(subset='card_number', inplace=True)


# add comma after audit number
audits.card_number = audits.card_number.astype('str').apply(lambda x: x + ', ')


# separate entire building audits and partial building audits
audits_whole_building = audits[audits.ENTIRE_BUILDING == 1]
audits_parts = audits[audits.ENTIRE_BUILDING == 0]


# collect all audits card numbers per STA_SID
card_numbers = audits_parts.groupby('STA_SID').card_number.unique()
# convert to string and remove brackets
card_numbers = remove_symbols_from_series(card_numbers.astype('str'), ["[", "'", "]"])
# sum up fuel, m2 and card_numbers for partial building audits per STA_SID
cols_to_sum = fuel_cols + list(['au', 'ENTIRE_BUILDING', 'TOTAL_FUEL'])
audits_parts = audits_parts.groupby(['STA_SID'])[cols_to_sum].sum()
# add card numbers
audits_parts['card_number'] = card_numbers


# exclude STA_SID that already included in audits_whole_building
ind = set(audits_parts.index).intersection(set(audits_whole_building['STA_SID'].unique()))
audits_parts.drop(index=ind, inplace=True)
audits = pd.concat([audits_whole_building.set_index('STA_SID'), audits_parts], sort=False)
# remove last comma after card numbers
audits.card_number = audits.card_number.apply(lambda x: x.rpartition(',')[0])


# save result
to_keep = ['card_number',
           'au',
           #'qfh_au',
           'HOT_WATER_m2',
           'ELKO',
           'UNP',
           'ZP',
           'DISTRICT_HEAT',
           'BIOMASS',
           'COAL',
           'SOLAR_THERMAL',
           'HEAT_PUMP_AIR',
           'GEOTHERMAL',
           'DISTRICT_HEAT_HIGH_EFF',
           'DISTRICT_HEAT_BIOMASS',
           'TOTAL_FUEL',
           'HEAT_PUMP_47',
           'ENTIRE_BUILDING']

audits = audits[to_keep]
audits.drop_duplicates(inplace=True)

# TODO scale consumption of partial audits to entire buildings surface area
# TODO indicate whether audit measured or calculated
# surface = pd.read_csv(all_cities['root'] / all_cities['stavbe'])

save_file_path = all_cities['root'] / all_cities['energetske_izkaznice_cleaned']
audits.to_csv(
    save_file_path,
    columns=to_keep,
    index=True,
    encoding='cp1250'
)
