from pathlib import Path

all_cities = dict({
    'root': Path('C:/Users/petera/Documents/Envirodual'),
    'results': Path('results'),
    'addresses_all': Path('data/ALL_CITIES/naslovi/addresses_all.csv'),
    'energetske_izkaznice_raw': Path('data/ALL_CITIES/Energetske_izkaznice/energetske_izkaznice.csv'),
    'energetske_izkaznice_cleaned': Path('data/ALL_CITIES/Energetske_izkaznice/energetske_izkaznice_cleaned.csv'),
    'audits_cleaned_for_model': Path('data/ALL_CITIES/Energetske_izkaznice/audits_cleaned_for_model.csv'),
    'eko_sklad_folder': Path('data/ALL_CITIES/Eko_sklad'),
    'eko_sklad_cleaned': Path('data/ALL_CITIES/Eko_sklad/eko_sklad_cleaned.csv'),
    'geothermal_raw': Path('data/ALL_CITIES/Geotermalna_energija/toplotne_crpalke_ekosklad_energija.csv'),
    'geothermal_cleaned': Path('data/ALL_CITIES/Geotermalna_energija/geothermal_cleaned.csv'),
    'delistavb': Path('data/ALL_CITIES/REN_all_cities/REN_SLO_delistavb_20191228.csv'),
    'stavbe': Path('data/ALL_CITIES/REN_all_cities/REN_SLO_stavbe_20191228.csv'),
    'addresses_city': Path('data/ALL_CITIES/REN_all_cities/REN_SLO_stavba_naslovi_20191228.csv'),
    'sifranti': Path('data/ALL_CITIES/REN_all_cities/REN_SLO_sifranti_20191228.csv'),
    'temperature_deficit_cleaned': Path('data/ALL_CITIES/temperature_deficit/temperature_deficit_cleaned.csv')
})

cerklje_na_gorenjskem = dict({
    'evidim_raw': Path('data/cerklje_na_gorenjskem/evidim/EVIDIM_cerklje_n_g.xlsx'),
    'evidim_cleaned': Path('data/cerklje_na_gorenjskem/evidim/evidim_cleaned.csv'),
    'heat_m2': Path('results/energijsko_cerklje_na_gorenjskem.csv'),
    'public': Path('data/cerklje_na_gorenjskem/public_buildings/javne_stavbe_cerklje_n_g.csv'),
    'public_cleaned': Path('data/cerklje_na_gorenjskem/public_buildings/public_cleaned.csv'),
    'objekti_kotlovnice_raw': Path('data/cerklje_na_gorenjskem/skupne_kotlovnice/objekti_v_skupnem_sistemu_cerklje_n_g.xlsx'),
    'kotlovnice_raw': Path('data/cerklje_na_gorenjskem/skupne_kotlovnice/skupne_kotlovnice_cerklje_n_g.xlsx'),
    'kotlovnice_cleaned': Path('data/cerklje_na_gorenjskem/skupne_kotlovnice/kotlovnice_cleaned.csv'),
    'REN_cleaned': Path('data/cerklje_na_gorenjskem/REN/REN_cleaned.csv'),
    'vodna_dovoljenja_raw': Path('data/cerklje_na_gorenjskem/vodna_dovoljenja/voda_za_pridobivanje_toplote_cerklje_n_g.xlsx'),
    'vodna_dovoljenja_cleaned': Path('data/cerklje_na_gorenjskem/vodna_dovoljenja/voda_za_pridobivanje_toplote_cerklje_n_g.xlsx'),
    'input_for_prediction': Path('data/cerklje_na_gorenjskem/prediction_input/ready_for_prediction.csv'),
    'predicted_heat': Path('data/cerklje_na_gorenjskem/predicted_heat/predicted_heat.csv'),
    'predicted_heat_total': Path('data/cerklje_na_gorenjskem/predicted_heat/predicted_heat.csv'),
    'gas_active_raw': Path('data/cerklje_na_gorenjskem/plinski_prikljucki/aktivni_prikljucki_cerklje_n_g.xlsx'),
    'gas_inactive_raw': Path('data/cerklje_na_gorenjskem/plinski_prikljucki/neaktivni_prikljucki_cerklje_n_g.xlsx'),
    'active_gas_cleaned': Path('data/cerklje_na_gorenjskem/plinski_prikljucki/aktivni_prikljucki_cleaned.csv'),
})


cerknica = dict({
    'city': Path('Data/Cerknica'),
    'REN': Path('Data/Cerknica/REN'),
    'stavbe': Path('REN_013_stavbe_20191102.csv'),
    'addresses': Path('REN/REN_013_stavba_naslovi_20191102.csv'),
    'deli_stavb': Path('REN_013_delistavb_20191102.csv'),
    'sifranti': Path('REN_013_sifranti_20191019.csv'),
    'evidim': Path('evidim/20191107_EVIDIM_Cerknica.xls'),
    'heat_m2': Path('Results/energijsko_stevilo_cerknica.csv')
})


medvode = dict({
    'city_folder': Path('Data/Medvode'),
    'REN': Path('Data/Medvode/REN'),
    'stavbe': Path('REN_071_stavbe_D48_20190907.csv'),
    'addresses': Path('REN_071_stavba_naslovi_D48_20190907.csv'),
    'deli_stavb': Path('REN_071_delistavb_D48_20190907.csv'),
    'sifranti': Path('REN_071_sifranti_D48_20190907.csv'),
    'evidim': Path('evidim/EVIDIM.csv'),
    'heat_m2': Path('Results/energijsko_stevilo_medvode.csv')
})


murska_sobota = dict({
    'city_folder': Path('Data/Murska_Sobota'),
    'REN': Path('Data/Medvode/REN'),
    'stavbe': Path('REN_080_stavbe_20191019.csv'),
    'addresses': Path('REN_080_stavba_naslovi_20191102.csv'),
    'deli_stavb': Path('REN_080_delistavb_20191019.csv'),
    'sifranti': Path('REN_080_sifranti_20191019.csv'),
    'evidim': Path('evidim/evidim_cleaned.csv'),
    'heat_m2': Path('Results/energijsko_murska_sobota.csv'),
    'public': Path('municipal_buildings_murska_sobota.csv')
})


ljubljana = dict({
    'evidim': Path('data/ljubljana/evidim/evidim_cleaned.csv'),
    'heat_m2': Path('Results/energijsko_murska_sobota.csv'),
    'public': Path('data/ljubljana/municipal_buildings_murska_sobota.csv'),
    'gas_raw': Path('data/ljubljana/gas/ljubljana_gas_2018.csv'),
    'gas_cleaned': Path('data/ljubljana/gas/gas_2018_cleaned.csv'),
    'district_heat_cleaned': Path('data/ljubljana/district_heat/district_heat_cleaned_2017.csv')
})


kranj = dict({
    'gas_raw': Path('data/kranj/gas/DistribucijaKranjPOletih-p.xlsx'),
    'gas_cleaned': Path('data/kranj/gas/gas_cleaned.csv'),
    'evidim_raw': Path('data/kranj/evidim/EVIDIM_kranj_2020.csv'),
    'evidim_cleaned': Path('data/kranj/evidim/evidim_cleaned.csv'),
    'heat_m2': Path('results/energijsko_kranj.csv'),
    'public': Path('data/kranj/public_buildings/javne_stavbe_kranj_2016-2018.csv'),
    'public_cleaned': Path('data/kranj/public_buildings/public_cleaned.csv'),
    'objekti_kotlovnice_raw': Path('data/kranj/skupne_kotlovnice/objekti_v_skupnem_sistemu_kranj.csv'),
    'kotlovnice_raw': Path('data/kranj/skupne_kotlovnice/skupne_kotlovnice_kranj.csv'),
    'kotlovnice_cleaned': Path('data/kranj/skupne_kotlovnice/kotlovnice_cleaned.csv'),
    'REN_cleaned': Path('data/kranj/REN/REN_cleaned.csv'),
    'vodna_dovoljenja_raw': Path('data/kranj/vodna_dovoljenja/vodna_dovoljenja_kranj.xlsx'),
    'vodna_dovoljenja_cleaned': Path('data/kranj/vodna_dovoljenja/vodna_dovoljenja_cleaned.csv'),
    'input_for_prediction': Path('data/kranj/prediction_input/ready_for_prediction.csv'),
    'predicted_heat': Path('data/kranj/predicted_heat/predicted_heat.csv'),
    'predicted_heat_total': Path('data/kranj/predicted_heat/predicted_heat.csv')
})


model = dict({
    'gas_kranj': Path('data/model_inputs/gas_kranj_2019.csv'),
    'gas_ljubljana': Path('data/model_inputs/gas_ljubljana_2017.csv'),
    'district_ljubljana': Path('data/model_inputs/district_heating_ljubljana_2017.csv'),
    'audits_measured': Path('data/ALL_CITIES/energetske_izkaznice/merjene_energetske_izkaznice.csv'),
    'audits_cleaned_for_model': Path('data/model_inputs/audits_cleaned_for_model.csv'),
    'models': Path('prediction_models'),
    'model_06_05': Path('prediction_models/model.pkl'),
    'model_08_04': Path('prediction_models/model_08_04.pkl'),
    'features_model_08_04': Path('prediction_models/columns_model_08_04.pkl'),
    'model_10_04': Path('prediction_models/model_10_04.pkl'),
    'features_model_10_04': Path('prediction_models/columns_model_10_04.pkl'),
    'model_11_04': Path('prediction_models/model_11_04.pkl'),
    'features_model_11_04': Path('prediction_models/columns_model_11_04.pkl'),
})


city_paths = dict({
    'kranj': kranj,
    'ljubljana': ljubljana,
    'cerklje_na_gorenjskem': cerklje_na_gorenjskem,
})


# Skofja Loka
# CITY_NAME_ORIGINAL = 'škofja_loka'
# file_name_stavbe = 'REN__stavbe.csv'
# ADRESSES = 'REN__stavba_naslovi.csv'
# file_name_delistavb = 'REN__delistavb.csv'
# file_name_evidim = 'evidim.csv'
# file_name_sifranti = 'REN__sifranti.csv'
# PATH_REN = 'Data/Skofja_Loka/REN/'
# PATH_EVIDIM = 'Data/Skofja_Loka/evidim/'
# PATH_SAVE_EI = 'Data/Skofja_Loka/'
# file_name_ei = 'ei.csv'

# Menges
# CITY_NAME_ORIGINAL = 'mengeš'
# file_name_stavbe = 'REN_072_stavbe_20191130.csv'
# ADRESSES = 'REN_072_stavba_naslovi_20191130.csv'
# file_name_delistavb = 'REN_072_delistavb_20191130.csv'
# file_name_evidim = 'EVIDIM_2019_Menges.xlsx'
# file_name_sifranti = 'REN_072_sifranti_20191130.csv'
# PATH_REN = 'Data/Menges/REN/'
# PATH_EVIDIM = 'Data/Menges/evidim/'
# PATH_SAVE_EI = 'Data/Menges/'
# file_name_ei = 'ei_menges.csv'

# Kranjska Gora
# CITY_NAME_ORIGINAL = 'kranjska_gora'
# file_name_stavbe = 'REN_053_stavbe_20200201.csv'
# ADRESSES = 'REN_053_stavba_naslovi_20200201.csv'
# file_name_delistavb = 'REN_053_delistavb_20200201.csv'
# file_name_evidim = 'Kranjska Gora_EVIDIM.csv'
# file_name_sifranti = 'REN_053_sifranti_20200201.csv'
# PATH_REN = 'Data/Kranjska_Gora/REN/'
# PATH_EVIDIM = 'Data/Kranjska_Gora/evidim/'
# PATH_SAVE_EI = 'Data/Kranjska_gora/'
# file_name_ei = 'ei.csv'


