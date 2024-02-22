import pandas as pd
import requests
import numpy as np
import os
import glob
import re
from datetime import datetime
from zipfile import ZipFile
from io import BytesIO

eia_page = 'https://www.eia.gov/electricity/data/eia861/'


def download_eia_861(start_year, end_year, data_dir=None):
    target_regex = re.compile(r'Sales_Ult_Cust_\d{4}\.xls')

    if start_year < 2012:
        start_year = 2012

    this_year = int(datetime.today().strftime('%Y'))

    if end_year > this_year - 1:
        end_year = this_year - 1

    year_list = list(range(start_year, end_year))

    for year in year_list:
        if year == this_year - 1:
            filename = f'https://www.eia.gov/electricity/data/eia861/zip/f861{year}.zip'
        else:
            filename = f'https://www.eia.gov/electricity/data/eia861/archive/zip/f861{year}.zip'

        file = requests.get(filename)
        zip_data = BytesIO(file.content)

        with ZipFile(zip_data, 'r') as zip_ref:
            files = zip_ref.namelist()
            files_to_extract = [file for file in files if target_regex.search(file)]
            for file_to_extract in files_to_extract:
                zip_ref.extract(file_to_extract, data_dir)
                print(f'Extracted {file_to_extract}')


def process_and_merge_861(data_dir, process_dir):
    files = glob.glob(os.path.join(data_dir, 'Sales_*.xls*'))
    col_range = 'A:R'
    skiprows = 2
    tiers = ['RESIDENTIAL', 'COMMERCIAL', 'INDUSTRIAL']
    measures = ['REVENUE', 'SALES_MWH', 'CUSTOMERS']

    # Set up column names
    tier_cols = [f'{tier}_{measure}' for tier in tiers for measure in measures]
    all_columns = ['YEAR', 'UTILITY_NUMBER', 'UTILITY_NAME', 'PART', 'SERVICE_TYPE', 'DATA_TYPE', 'STATE', 'OWNERSHIP', 'BA_CODE'] + tier_cols

    dfs = []

    for file in files:
        print(f'Reading in {file}')

        if '2019' in file:
            col_range = 'A:S'
        else:
            col_range = 'A:R'

        df = pd.read_excel(file, skiprows=skiprows, usecols=col_range)

        # BA_CODE does not exist in 2012 file, add this
        # Drop last column incorrectly indexed from A:K
        if '2012' in file:
            df.insert(loc=8, column='BA_CODE', value=np.nan)
            df = df.drop(df.columns[-1], axis=1)

        if '2019' in file:
            df = df.drop('Short Form', axis=1)

        df.columns = all_columns

        display(df.head())

        dfs.append(df)

    df_merged = pd.concat(dfs, axis=0).reset_index(drop=True)

    # Remove erroneous footer rows
    df_merged = df_merged[df_merged['YEAR'].apply(lambda x: isinstance(x, int))]

    dfs = []

    for tier in tiers:
        ref_list = tiers.copy()
        ref_list.remove(tier)

        exclusion = '|'.join(ref_list)
        exclude_regex = f'^(?!{exclusion})'

        df = df_merged.filter(regex=exclude_regex).assign(CUSTOMER_TYPE=tier)
        df.columns = [col.replace(f'{tier}_', '') for col in df.columns]
        dfs.append(df)

    pivot_df = pd.concat(dfs, axis=0).reset_index(drop=True)

    # Correct value to thousands of dollars
    pivot_df['REVENUE'] = pivot_df['REVENUE'] * 1000
    pivot_df['SALES_MWH'] = pivot_df['SALES_MWH'] * 1000
    pivot_df.rename(columns={'SALES_MWH': 'SALES_KWH'}, inplace=True)

    print(f'Merged dataframe of {pivot_df.shape}')

    output_file_path = os.path.join(process_dir, 'sales_ult_cust_all_years.csv')
    pivot_df.to_csv(output_file_path, index=False)

    print(f'Wrote dataframe to CSV in {process_dir}')

    return pivot_df


def process_customer_migration_files(remote_file, data_dir, target_dir):

    # Get and write file
    resp = requests.get(remote_file)
    filepath = os.path.join(data_dir, 'customer_migration_statistics.xls')
    with open(filepath, 'wb') as file:
        file.write(resp.content)

    cust_cols = ['DATE', 'CEP_CUSTOMERS', 'TOTAL_CUSTOMERS']
    load_cols = ['DATE', 'CEP_LOAD_MWH', 'TOTAL_CLASS_LOAD_MWH']

    # Select and transform source data
    col_range = 'A:AK'

    sheet_to_file_map = {
        'Customers': {
            'filename': 'customers_migrated.csv',
            'cols': cust_cols,
            'skiprows': 3
        },
        'Load': {
            'filename': 'load_migrated.csv',
            'cols': load_cols,
            'skiprows': 4
        }
    }

    for sheet, deets in sheet_to_file_map.items():

        df = pd.read_excel(resp.content, sheet_name=sheet, skiprows=deets.get('skiprows'), usecols=col_range)
        df = df[~df.iloc[:, 1].isna()]

        exclude_regex = f'^(?!%)'
        df = df.filter(regex=exclude_regex)

        district_dict = {
            'BANGOR HYDRO DISTRICT': {
                'SMALL': slice(1, 3),
                'MEDIUM': slice(3, 5)
            },
            'CENTRAL MAINE POWER CO.': {
                'SMALL': slice(9, 11),
                'MEDIUM': slice(11, 13)
            },
            'MAINE PUBLIC SERVICE': {
                'SMALL': slice(17, 19),
                'MEDIUM': slice(19, 21)
            }
        }

        dfs = []

        # Transform each utility partition, adding ref column
        for utility, v in district_dict.items():
            for customer_class, col_slice in v.items():
                df_slice = df.iloc[:, np.r_[0, col_slice]]
                df_slice.columns = deets.get('cols')
                df_slice = df_slice.assign(UTILITY=utility).assign(CUSTOMER_CLASS=customer_class)
                dfs.append(df_slice)

        migration_df = pd.concat(dfs, axis=0)

        migration_df.to_csv(os.path.join(target_dir, deets.get('filename')), index=False)

        print(f'Captured and wrote {sheet} file of shape {migration_df.shape}')

    return migration_df
