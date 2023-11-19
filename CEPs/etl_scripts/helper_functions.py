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

    files = glob.glob(os.path.join(data_dir, '*.xls*'))

    tiers = ['RESIDENTIAL', 'COMMERCIAL', 'INDUSTRIAL']
    measures = ['REVENUE', 'SALES_MWH', 'CUSTOMERS']

    tier_cols = [f'{tier}_{measure}' for tier in tiers for measure in measures]

    col_range = 'A:R'
    skiprows = 2

    columns = [
                  'YEAR',
                  'UTILITY_NUMBER',
                  'UTILITY_NAME',
                  'PART',
                  'SERVICE_TYPE',
                  'DATA_TYPE',
                  'STATE',
                  'OWNERSHIP',
                  'BA_CODE'
              ] + tier_cols

    dfs = []

    for file in files:
        print(f'Reading in {file}')
        df = pd.read_excel(file, skiprows=skiprows, usecols=col_range)
        df.columns = columns
        dfs.append(df)

    df_merged = pd.concat(dfs, axis=0).reset_index(drop=True)

    # Remove erroneous footer rows
    df_merged = df_merged[df_merged['YEAR'].apply(lambda x: type(x) == int)]

    print(f'Merged dataframe of {df.shape}')

    df_merged.to_csv(os.path.join(process_dir, 'sales_ult_cust_all_years.csv'))

    print(f'Wrote dataframe to CSV in {process_dir}')

    return df_merged