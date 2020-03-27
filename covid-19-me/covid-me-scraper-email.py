import pandas as pd
import smtplib
import requests
import os
import pygsheets
import datadotworld as dw
import http.client
import json

import config

email_address = os.environ['EMAIL_NAME']
pw = os.environ['EMAIL_PW']

gc = pygsheets.authorize(service_file='covid-gcreds.json')

# Dictionary of table match (key], then (header_row, column count]
shape_dict = {'Testing Data': {'header_row': 2, 'filename': 'case_summary'}
    , 'COVID-19 Case Counts by County': {'header_row': 2, 'filename': 'cases_by_county'}
    , 'Confirmed Cases by Age': {'header_row': 2, 'filename': 'cases_by_age'}
    , 'Confirmed Cases by Sex': {'header_row': 2, 'filename': 'cases_by_sex'}}

matches = list(shape_dict)[0:]

# Manual column mapping for each table -- new columns will show null values for old records
column_list = {matches[0]: ['Confirmed Cases1', 'Negative Tests2']
    , matches[1]: ['County', 'Confirmed', 'Recovered', 'Deaths']
    , matches[2]: ['Age Range', 'Count']
    , matches[3]: ['Sex', 'Count']}

cols = list(column_list.values())

i = 0
y = 0
for x in matches:
    try:
        # Finds tables in order of dictionary match, sets header row, specifies columns
        df = pd.read_html('https://www.maine.gov/dhhs/mecdc/infectious-disease/epi/airborne/coronavirus.shtml',
                          match=matches[i], header=list(shape_dict.values())[i]['header_row'])[0][cols[i]]

        # Update time could now unique to each table -- March 22
        update_time = pd.to_datetime(
            pd.read_html('https://www.maine.gov/dhhs/mecdc/infectious-disease/epi/airborne/coronavirus.shtml',
                         match=matches[i], header=None)[0].columns[0][1].replace('Updated: ', '').replace(' at ',
                                                                                                          ' ').strip())
    except:
        # log failures
        y += 1
        print(str(list(shape_dict.values())[i]['filename']) + ' failed to load or changed structures.')
        # advance main iterator
        i += 1
    else:
        # DETERMINE IF FILE IS NEW, IF SO EMAIL ALERT#
        # Declare target sheet and get data
        sh = gc.open('covid-19-maine')
        wks = sh.worksheet('index', i)
        dfg = wks.get_as_df()

        filename = list(shape_dict.values())[i]['filename']
        last_update_time = max(pd.to_datetime(dfg['timestamp']))

        if update_time > last_update_time:

            print('CDC ' + str(list(shape_dict.values())[i]['filename']) + str(
                update_time) + '. Prior update was at: ' + str(last_update_time))

            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()

                smtp.login(email_address, pw)

                subject = f'MAINE CDC TABLE {filename} UPDATED AS OF {update_time}'
                body = f'The prior update of {filename} was at {last_update_time} \n\n Data just refreshed at {update_time}'
                msg = f'Subject: {subject}\n\n{body}'

                smtp.sendmail(email_address, email_address, msg)

            # Join county data table to county population records
            if matches[i] == matches[1]:
                # Bring in population source, join and drop dupe column
                results = dw.query('darrenfishell/covid-19-me', 'SELECT * FROM `2018_population_by_county`').dataframe
                results['county'] = results['county'].str.strip()
                df = pd.merge(df, results, left_on='County', right_on='county', how='left')
                df.drop(['county'], axis=1, inplace=True)

            # TRANSFORM DATAFRAME FOR LOAD#
            df.fillna('', inplace=True)
            df['timestamp'] = update_time

            ##WRITE FILES TO Google Sheets##
            # Get target sheet as dataframe, combine with new load and eliminate dupes
            df = pd.concat([df, dfg], sort=False).drop_duplicates()

            # Truncate table and load modified dataframe
            wks.clear()
            wks.rows = df.shape[0]
            wks.set_dataframe(df, start='A1', nan='')

            ##WRITE FILES to data.world##
            with dw.open_remote_file('darrenfishell/covid-19-me',
                                     list(shape_dict.values())[i]['filename'] + '.csv') as w:
                df.to_csv(w, index=False)

        else:
            print('CDC ' + str(list(shape_dict.values())[i]['filename']) + ' not updated. Last updated: ' + str(
                last_update_time) + '. Current CDC timestamp: ' + str(update_time))
        i += 1

print(str(i) + ' files processed successfully.')
print(str(y) + ' files failed.')

##ADD NYT STATES FILE##
df = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv')
wks = sh.worksheet('index', 4)
wks.clear()
wks.rows = df.shape[0]
wks.set_dataframe(df, start='A1', nan='')

##WRITE NYT file to data.world##
with dw.open_remote_file('darrenfishell/covid-19-me', 'nyt_states.csv') as w:
    df.to_csv(w, index=False)