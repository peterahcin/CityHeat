from paths.path_definition import all_cities
import pandas as pd


sifranti_path = all_cities['root'] / all_cities['sifranti']
sifranti = pd.read_csv(
    sifranti_path,
    sep=';'
)


# all area use categories from REN
area_use_columns = sifranti.loc[sifranti.POLJE_PK == 'DEJANSKA_RABA']['IME'].values
area_use_codes = sifranti.loc[sifranti.POLJE_PK == 'DEJANSKA_RABA']['ID'].values


# dictionary with heating system efficiencies as keys and periods of installation as values
eff_dict = {0.89: [1, 1989],
            0.92: [1990, 1998],
            0.94: [1999, 2008],
            0.95: [2009, 2345]
            }


OB_MID_dict = dict({
    'kranj': 11027784,
    'ljubljana': 11027849,
    'cerklje_na_gorenjskem': 11026630
})


# heated area uses
heated_area_cols = [
    'Arhiv',
    'Atelje',
    # 'Avtobusna postaja',
    'Avtosalon',
    'Banka, pošta, zavarovalnica',
    'Bencinski servis za maloprodajo',
    'Bife',
    'Bivalna enota v stavbi za posebne namene',
    'Cerkev, molilnica',
    'Dvorana za družabne prireditve',
    # 'Elektrarna',
    'Gasilski dom',
    'Hladilnice in specializirana skladišča',
    'Hotel, motel',
    'Industrijski del stavbe',
    'Klinika, ambulanta',
    'Koča, dom',
    'Letališče',
    'Muzej, knjižnica',
    'Nakupovalni center',
    'Oskrbovano stanovanje',
    'Paviljon, prostor za živali in rastline v živalskih in botaničnih vrtovih',
    'Penzion, gostišče',
    # 'Pokopališki del stavbe',
    'Pokrit plavalni bazen',
    'Pokrit prostor za šport in prireditve',
    'Poslovni prostori',
    'Poslovni prostori javne uprave',
    'Prevzgojni dom, zapor, vojašnica, prostor za nastanitev policistov, gasilcev',
    'Prodajalna',
    'Prostor za izobraževanje in usposabljanje otrok s posebnimi potrebami',
    'Prostor za nastanitev, nego, zdravstveno in veterinarsko oskrbo',
    'Prostor za neinstitucionalno izobraževanje',
    'Prostor za pastoralno dejavnost',
    'Prostor za razvedrilo',
    'Prostor za zdravstvo',
    'Prostor za znanstvenoraziskovalno delo',
    'Prostori za izkoriščanje mineralnih surovin',
    'Prostori za oskrbo in nego hišnih živali',
    'Prostori za proizvodnjo izdelkov za gradbeništvo',
    'Prostori za storitvene dejavnosti',
    'Restavracija, gostilna',
    'Sejemska dvorana, razstavišče',
    'Skladišča',
    'Skupna raba',
    'Spremljajoči objekti za prodajo bencina in drugih motornih goriv',
    'Stanovanje v krajni vrstni hiši z dvema stanovanjema',
    'Stanovanje v samostoječi stavbi z dvema stanovanjema',
    'Stanovanje v samostoječi stavbi z enim stanovanjem',
    'Stanovanje v večstanovanjski stavbi ali stanovanjsko poslovni stavbi',
    'Stanovanje v vmesni vrstni hiši z dvema stanovanjema',
    'Stanovanje, ki se nahaja v krajni vrstni hiši',
    'Stanovanje, ki se nahaja v vmesni vrstni hiši',
    'Veleposlaništva in konzularna predstavništva',
    'Veterinarska klinika',
    'Zdravilišče',
    'prodajalna polizdelkov',
    'Šola, vrtec',
    'Železniška postaja',
    'Športna dvorana']


# collect use codes corresponding to heated areas
heated_area_codes = sifranti.loc[sifranti.IME.isin(heated_area_cols)]['ID'].values


# dictionary with heating system efficiencies as keys and periods of installation as values

elko_efficiency = {0.89: [1, 1989],
                   0.92: [1990, 1998],
                   0.94: [1999, 2008],
                   0.95: [2009, 2345]}

zp_efficiency = elko_efficiency

unp_efficiency = elko_efficiency

biomass_efficiency = elko_efficiency
peleti_efficiency = elko_efficiency
sekanci_efficiency = elko_efficiency
polena_efficiency = elko_efficiency
naravni_les_efficiency = elko_efficiency

solar_thermal_efficiency = {1: [1, 2345]}

heat_pump_air_efficiency = solar_thermal_efficiency

heat_pump_ground_efficiency = solar_thermal_efficiency

geothermal_efficiency = solar_thermal_efficiency

district_heat_efficiency = elko_efficiency

coal_efficiency = elko_efficiency

na_fuel_efficiency = {0.9: [1, 3000]}

system_efficiencies = dict({
    'ELKO': elko_efficiency,
    'ZP': zp_efficiency,
    'UNP': unp_efficiency,
    'BIOMASS': biomass_efficiency,
    'PELETI': peleti_efficiency,
    'SEKANCI': sekanci_efficiency,
    'POLENA': polena_efficiency,
    'NARAVNI_LES': naravni_les_efficiency,
    'HEAT_PUMP_AIR': heat_pump_air_efficiency,
    'HEAT_PUMP_GROUND': heat_pump_ground_efficiency,
    'SOLAR_THERMAL': solar_thermal_efficiency,
    'GEOTHERMAL': geothermal_efficiency,
    'DISTRICT_HEAT': district_heat_efficiency,
    'COAL': coal_efficiency,
    'NA_FUEL': na_fuel_efficiency
})
# fuel columns in final table
fuel_columns = system_efficiencies.keys()


# heating system info
system_info_columns = [
    'Naziv namen naprave',
    'Naziv vrsta naprave',
    'kW_m2_stevilo',
    'INSTALLATION_YEAR',
    ]

# energy class labels taken from https://energetska-izkaznica.visia.si/energetski-razredi/
class_labels = list(['A1', 'A2', 'B1', 'B2', 'C', 'D', 'E', 'F', 'G'])
class_borders = list([[1, 10], [11, 15], [16, 25], [26, 35], [36, 60],
                      [61, 105], [106, 150], [151, 210], [211, 3000]])
