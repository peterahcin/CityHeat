import pandas as pd
from path_definition import all_cities, model
# Avoid unnecessary imports
from preprocessing import remove_symbols_from_series


addresses_path = all_cities['root'] / all_cities['addresses_all']
addresses = pd.read_csv(
    addresses_path,
    usecols=['STA_SID', 'KO_SIFKO', 'STEV', 'X_C', 'Y_C'],
    encoding='cp1250',
)


cols = [
    'card_number',
    'building_identification',
    'au',
    'qsum',
    'qsum_au',
    # Avoid commented out code blocks
    # 'qel',
    # 'qel_au',
    # 'qp',
    # 'date_issued',
    # 'in_energy_sum',
    # 'in_elko_energy',
    # 'in_unpm3_energy',
    # 'in_unpkg_energy',
    # 'in_zemeljski_plin_energy',
    # 'in_zemeljski_plin_primary',
    # 'in_daljinska_toplota_energy',
    # 'in_lesna_biomasa_energy',
    # 'in_premog_energy',
    # 'in_elektrika_energy',
    # 'out_energy_sum',
    # 'out_electricity_energy',
    # 'out_heat_cogeneration_energy',
    # 'out_heat_other_energy'
]


file_path = all_cities['root'] / model['audits_measured']
audits = pd.read_csv(
        file_path,
        usecols=cols,
        thousands=','
)

audits.rename(
    columns={
        'au': 'AREA_AUDIT',
        'qsum': 'TOTAL_HEAT',
        'qsum_au': 'HEAT_m2'
    },
    inplace=True)

# Read building identifiers
audits['DELI_STAVBE'] = audits['building_identification'].str.findall('(\d+)').apply(lambda x: [int(i) for i in x])
audits['KO_SIFKO'] = audits['DELI_STAVBE'].apply(lambda x: x.pop(0) if len(x) > 0 else 0)
audits['STEV'] = audits['DELI_STAVBE'].apply(lambda x: x.pop(0) if len(x) > 0 else 0)


# add year measured
audits['YEAR_MEASURED'] = audits['card_number'].str.partition('-')[0].astype('int') -1


# eliminate entries referring to only parts of buildings or multiple buildings
audits = audits[audits.building_identification.str.contains('del').__neg__()]
audits = audits[audits.building_identification.str.contains(',').__neg__()]


audits = audits[(audits.HEAT_m2 > 0) & (audits.TOTAL_HEAT > audits.AREA_AUDIT)]
audits.drop(columns=['building_identification', 'card_number', 'DELI_STAVBE'], inplace=True)

# add STA_SID
audits = audits.set_index(['KO_SIFKO', 'STEV']).join(addresses.set_index(['KO_SIFKO', 'STEV']), how='inner')


audits.to_csv(
    all_cities['root'] / all_cities['audits_cleaned_for_model'],
    index=False,
)
