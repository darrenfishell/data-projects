import pandas as pd
import pygsheets
import datadotworld as dw
import datetime

def get_county():
    county = pd.read_csv(county_url, parse_dates=['DATA_REFRESH_DT', 'DATA_AS_OF_DT'])
    pops = dw.query('darrenfishell/covid-19-me', 'SELECT * FROM `2018_population_by_county`').dataframe
    pops['county'] = pops['county'].str.strip()
    county = pd.merge(county, pops, left_on='PATIENT_COUNTY', right_on='county', how='left')
    county.drop(['county'], axis=1, inplace=True)
    cols = ['PATIENT_COUNTY'
            , 'CASES'
            , 'RECOVERIES'
            , 'HOSPITALIZATIONS'
            , 'DEATHS'
            , '2018_pop'
            , 'DATA_REFRESH_DT']
    county = county[cols]
    return county


def get_age():
    age = pd.read_csv(age_url, parse_dates=['DATA_REFRESH_DT', 'DATA_AS_OF_DT'])
    cols = ['PATIENT_AGE'
            , 'CASES'
            , 'DATA_REFRESH_DT']
    age = age[cols]
    return age

def write_to_gsheet(df, tab):
    # Declare target sheet
    wks = sh.worksheet('title', tab)
    dfg = wks.get_as_df()

    if tab == 'nyt_states':

        last_update = pd.to_datetime(dfg['date']).max()
        new_file_dt = pd.to_datetime(df['date']).max()

        if new_file_dt > last_update:

            wks = sh.worksheet('title', tab)
            wks.clear()
            wks.rows = df.shape[0]
            wks.set_dataframe(df, start='A1', nan='')
            print('NYT data refreshed')

        else:
            print(f'NYT data not updated. Current through {last_update}')

    else:
        last_update = pd.to_datetime(dfg['timestamp']).max().date()
        new_file_dt = pd.to_datetime(df['DATA_REFRESH_DT']).max().date()

        if new_file_dt > last_update:

            new_cols = {x: y for x, y in zip(df.columns, dfg.columns)}
            df = df.rename(columns=new_cols)
            #Rename CSV columns to match Sheets

            df = pd.concat([df, dfg], sort=False).drop_duplicates()

            wks.clear()
            wks.rows = df.shape[0]
            wks.set_dataframe(df, start='A1', nan='')
            now = datetime.time()
            print(f'Data updated at {now}')

        else:
            print(f'Data not updated. Current through {last_update}.')

# Initialize GSheets creds and Sheet
gc = pygsheets.authorize(service_file='covid-gcreds.json')
sh = gc.open('covid-19-maine')

county_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRPtRRaID4XRBSnrzGomnTtUUkq5qsq5zj8fGpg5xse8ytsyFUVqAKKypYybVpsU5cHgIbY3BOiynOC/pub?gid=0&single=true&output=csv'
age_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRPtRRaID4XRBSnrzGomnTtUUkq5qsq5zj8fGpg5xse8ytsyFUVqAKKypYybVpsU5cHgIbY3BOiynOC/pub?gid=574023130&single=true&output=csv'
nyt_url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv'


county = get_county()
age = get_age()
nyt_file = pd.read_csv(nyt_url, parse_dates=['date'])

df_to_gsheet = {'cases_by_county': county
    , 'cases_by_age': age
    , 'nyt_states': nyt_file}

for tab, df in df_to_gsheet.items():

    write_to_gsheet(df, tab)