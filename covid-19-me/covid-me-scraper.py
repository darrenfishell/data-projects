import pandas as pd
import requests
import os
import pygsheets
import datadotworld as dw
import http.client
import json

#Dictionary of table match (key], then (header_row, column count]
shape_dict = {'Testing Data':{'header_row':2, 'column_count':3, 'filename':'case_summary'}
            ,'Confirmed, Presumptive and Recovered Case Counts by County':{'header_row':1, 'column_count':4, 'filename':'cases_by_county'}
            ,'Confirmed and Presumptive Cases by Age':{'header_row':1,'column_count':3,'filename':'cases_by_age'}
            ,'Confirmed and Presumptive Cases by Sex':{'header_row':1,'column_count':3,'filename':'cases_by_sex'}}

matches = list(shape_dict)[0:]

#Manual column mapping for each table -- new columns will show null values for old records
column_list = {'Testing Data': ['Confirmed Cases1','Negative Tests2']
            ,'Confirmed, Presumptive and Recovered Case Counts by County': ['County','Confirmed','Recovered']
            ,'Confirmed and Presumptive Cases by Age':['Age Range','Count']
            ,'Confirmed and Presumptive Cases by Sex':['Sex','Count']}

cols = list(column_list.values())

#Pull in summary update time
try:
    update_time = pd.read_html('https://www.maine.gov/dhhs/mecdc/infectious-disease/epi/airborne/coronavirus.shtml',
                     match=matches[0],header=None)[0].columns[0][1].replace('Updated: ', '').replace(' at ',' ').strip()
except:
    #Print error and exit if this fails
    print('Update time load failed.')
    exit(1)

i=0
y=0
for x in range(0,2):
    try:
        #Finds tables in order of dictionary match, sets header row, specifies columns
        df = pd.read_html('https://www.maine.gov/dhhs/mecdc/infectious-disease/epi/airborne/coronavirus.shtml',
                          match=matches[i], header=list(shape_dict.values())[i]['header_row'])[0][cols[i]]
    except:
        #log failures
        y+=1
        print(str(list(shape_dict.values())[i]['filename'])+' failed to load or changed structures.')

        # advance iterator
        i += 1
    else:
        # Join county data table to county population records
        if matches[i] == 'Confirmed, Presumptive and Recovered Case Counts by County':
            # Bring in population source, join and drop dupe column
            results = dw.query('darrenfishell/covid-19-me', 'SELECT * FROM `2018_population_by_county`').dataframe
            results['county'] = results['county'].str.strip()
            df = pd.merge(df, results, left_on='County', right_on='county', how='left')
            df.drop(['county'], axis=1, inplace=True)

        #Write to Google Sheets
        df['timestamp'] = update_time
        #Convert NAs to blanks
        df.fillna('', inplace=True)

        ##WRITE FILES TO Google Sheets##
        # Authenticate and workbook
        gc = pygsheets.authorize(service_file='covid-gcreds.json')
        sh = gc.open('covid-19-maine')

        # Declare target sheet
        wks = sh.worksheet('index', i)

        dfg = wks.get_as_df()
        # print(df)
        # print(dfg)

        # Get target sheet as dataframe, combine with new load and eliminate dupes
        df = pd.concat([df, dfg]).drop_duplicates(keep='last')

        # Truncate table and load modified dataframe
        wks.clear()
        wks.rows = df.shape[0]
        wks.set_dataframe(df, start='A1', nan='')

        ##WRITE FILES to data.world##
        with dw.open_remote_file('darrenfishell/covid-19-me', list(shape_dict.values())[i]['filename'] + '.csv') as w:
            df.to_csv(w, index=False)

    i+=1

print(str(i)+' files loaded successfully.')
print(str(y)+' files failed.')