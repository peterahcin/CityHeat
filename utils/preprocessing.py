import sklearn.neighbors
import pandas as pd


# remove symobols from addresses
def clean_string_column(df, signs_to_remove, column):
    for s in signs_to_remove:
        df[column] = df[column].str.replace(s, '')
    return df


to_remove = [r'C\.',
             r'UL\.',
             ' NH ',
             ' ',
             '/',
             ',',
             'ULICA',
             'CESTA',
             'NOVASTAVBA',
             'NOVOGRADNJA',
             r'\(',
             r'\)',
             '.']


def make_categorical_features(df, column, new_names):
    """
    reads all the categories in column and creates a separate column for each category.
    the names of the new columns are given in the dictionary new_names.

    column: - column containing the categories to one-hot enocode
    new_names: - contains names of categories as keys and names of corresponding columns as values.
    """

    # make new columns for each category
    for c in list(new_names.values()):
        df[c] = 0

    cats = df[column].unique()
    for v in cats:
        new_col_name = new_names[v]
        df.loc[df[column] == v, new_col_name] = 1
    return df


# drop no address entries
def drop_if_contains(df, column, values):
    for v in values:
        df.drop(
            index=df.index[df[column].str.contains(v)],
            inplace=True
        )
    return df


def address_to_sta_sid(df, df_addresses, address_column='ADDRESS'):
    """
    Finds STA_SID for given addresses.
    Returns original DataFrame df with STA_SID and remaining unassigned entries.

    df           - includes ADDRESS columns of capital letter addresses
    df_addresses - contains addresses in address_columns and corresponding STA_SID

    """

    # remove symbols from addresses
    df_addresses_ = clean_string_column(df_addresses, to_remove, address_column)
    df = clean_string_column(df, to_remove, address_column)

    df = df.join(
        df_addresses_.set_index(address_column),
        on=address_column,
        how='left'
    )

    # collect unassigned entries - discard entries without house number
    unassigned = df[df.STA_SID.isna()]
    unassigned = unassigned[unassigned.ADDRESS.str.findall(r'(\d+)').apply(lambda x: len(x) > 0)]

    return df, unassigned


def decode_column(df, column, dictionary):
    """
    :param df: dataframe
    :param column: column with codes to convert to categories
    :param dictionary: dict containing codes with corresponding categories
    :return: returns new dataframe with decoded column
    """

    for code, category in dictionary.items():
        df.loc[df[column].eq(code), column] = category
    return df


def one_hot_encode_column(df, column):
    """

    :param df: input dataframe
    :param column: column whose categories are encoded
    :return: returns dataframe with one hot encoded variables. Original column dropped

    """

    cats = df[column].unique()
    for c, v in enumerate(cats):
        new_col = column + '_' + str(c)
        df[new_col] = 0
        df.loc[df[column] == v, new_col] = 1
    return df.drop(column, axis=1)


def fill_and_mark(df, column, value=0):
    """

    fills missing values and creates new column to one hot encode the nans.
    columns - the column to fill and one hot encode
    value - the value to replace nan

    """

    df['NA_'+column] = 0
    idx = df[df[column].isna()].index.astype('int32')
    df.loc[idx, 'NA_'+column] = 1
    df[column].fillna(value, inplace=True)
    return df


def imputer_kNeighbors(df, attrib_to_impute, reference, n_neighbors=3):

    """

    :param df: dataframe
    :param attrib_to_impute: column to fill missing values
    :param reference: reference column based on which we impute the attrib_to_impute
    :param n_neighbors: number of neighbors to generate
    :return: returns the imputed values that are to replace the nans in attrib_to_impute column

    """

    neigh = sklearn.neighbors.KNeighborsRegressor(n_neighbors=n_neighbors)

    y = df[df[attrib_to_impute] > 0][attrib_to_impute]
    x = df[df[attrib_to_impute] > 0][reference].values.reshape(-1, 1)

    neigh.fit(x, y)

    x_missing = df[df[attrib_to_impute].isna()][reference].values.reshape(-1, 1)
    imputed_values = neigh.predict(x_missing)

    return imputed_values


def missing_data(df):
    all_data_na = (df.isnull().sum() / len(df)) * 100
    all_data_na = all_data_na.drop(all_data_na[all_data_na == 0].index).sort_values(ascending=False)[:]
    miss_data = pd.DataFrame({'Missing Ratio': all_data_na})
    print('\n Missing data shares remaining: ')
    print(miss_data.head(20))


def share_unassigned(df, final):
    """
    Calculates and prints out percentage of unassigned entries from raw data.
    :param df: raw data
    :param final: final table, cleaned data
    """
    ind = list(set(df.index).difference(set(final.index)))
    unassigned = df.loc[ind]
    print(f'Unassigned entries: {round(unassigned.shape[0]/df.shape[0]*100, 2)}%')


def heat_conversion_factors(df, system_efficiencies):
    """
    :param df: dataframe indicating with 0 and 1 where to insert conversion factors (1/system efficiency)
    :param system_efficiencies: dictionary of fuel efficiencies - contains dictionaries corresponding to each fuel
    :return: returns dataframe with inserted conversion factors
    """

    fuel_columns = system_efficiencies.keys()
    fuels = set(df.columns).intersection(set(fuel_columns))
    for f in fuels:

        efficiency_dictionary = system_efficiencies[f]
        # age groups
        age_groups = list(efficiency_dictionary.values())
        # Add heating system efficiencies
        efficiencies = list(efficiency_dictionary)
        # entries with f as fuel
        ind1 = df[f] == 1

        for a, e in zip(age_groups, efficiencies):
            # entries with systems installed in interval a
            ind2 = df.INSTALLATION_YEAR.between(a[0], a[1])
            # set heat to fuel conversion rate to 1/system efficiency
            df.loc[ind1 & ind2, f] = 1/e

    return df


def add_system_info(df_final, df_source, info_columns):
    # print(f'Added {source_name} to final table')
    df_source = df_source.loc[df_source.index.intersection(df_final.index)]
    for f in info_columns:
        if f in df_source.columns:
            df_final.loc[df_source.index, f] = df_source[f]
        else:
            df_final.loc[df_source.index, f] = ''
    # df_final.loc[df_source.index, 'DATA_SOURCE'] = source_name
    return df_final


def calculate_fuel_from_conversion_factors(df_final, df_source, source_name, fuel_columns):
    # print(f'Added {source_name} to final table')
    df_source = df_source.loc[df_source.index.intersection(df_final.index)]
    for f in fuel_columns:
        if f in df_source.columns:
            df_final.loc[df_source.index, f] = df_final.loc[df_source.index]['PREDICTED_HEAT_kWh'] * df_source[f]
        else:
            df_final.loc[df_source.index, f] = 0
    df_final.loc[df_source.index, 'DATA_SOURCE'] = source_name
    return df_final


def add_fuel_from_measured_sources(df_final, df_source, source_name, fuel_columns):
    # print(f'Added {source_name} to final table')
    df_source = df_source.loc[df_source.index.intersection(df_final.index)]
    for f in fuel_columns:
        if f in df_source.columns:
            df_final.loc[df_source.index, f] = df_source[f]
        else:
            df_final.loc[df_source.index, f] = 0
    df_final.loc[df_source.index, 'DATA_SOURCE'] = source_name
    return df_final


def make_sum_table(df, fuel_columns, sectors):
    sum_table = pd.DataFrame(index=[f for f in fuel_columns], columns=sectors)
    for s in sectors:
        for f in fuel_columns:
            sum_table.loc[f, s] = (df[s]
                                   / df[sectors].sum(axis=1)
                                   * df[f]).sum().round().astype('int')
    return sum_table


def fuel_consumption_by_type(df):
    return df.sum(axis=1)


def total_fuel_consumption(df):
    return df.sum().sum()


# % fuel consumption by type (%)
def fuels_by_share(df):
    return 100 * fuel_consumption_by_type(df) \
               / total_fuel_consumption(df)


# remove symobols from seres
def remove_symbols_from_series(series, signs_to_remove):
    for s in signs_to_remove:
        series = series.str.replace(s, '')
    return series


def list_unique_values(df, column, groupby='STA_SID'):
    df[column] = df[column].astype('str').apply(lambda x: x + ', ')
    df = df.groupby(groupby)[column].unique()
    df = df.astype('str').str.replace("]", '')
    df = df.str.replace("[", '')
    df = df.str.replace("'", '')
    return df.str.rpartition(sep=',')[0]
