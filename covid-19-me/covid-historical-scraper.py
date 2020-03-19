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

wayback_urls = ['https://web.archive.org/web/20200310174334/https://www.maine.gov/dhhs/mecdc/infectious-disease/epi/airborne/coronavirus.shtml'
                ,'https://web.archive.org/web/20200311174029/https://www.maine.gov/dhhs/mecdc/infectious-disease/epi/airborne/coronavirus.shtml'
                ,'https://web.archive.org/web/20200312225603/https://www.maine.gov/dhhs/mecdc/infectious-disease/epi/airborne/coronavirus.shtml'
                ,'https://web.archive.org/web/20200313203657/https://www.maine.gov/dhhs/mecdc/infectious-disease/epi/airborne/coronavirus.shtml'
                ,'https://web.archive.org/web/20200314144149/https://www.maine.gov/dhhs/mecdc/infectious-disease/epi/airborne/coronavirus.shtml'
                ,'https://web.archive.org/web/20200315192432/https://www.maine.gov/dhhs/mecdc/infectious-disease/epi/airborne/coronavirus.shtml'
                ,'https://web.archive.org/web/20200316165437/https://www.maine.gov/dhhs/mecdc/infectious-disease/epi/airborne/coronavirus.shtml'
                ,'https://web.archive.org/web/20200317170745/https://www.maine.gov/dhhs/mecdc/infectious-disease/epi/airborne/coronavirus.shtml']

i=0
for x in wayback_urls:
    #Pull in summary update time
    try:
        update_time = pd.read_html(wayback_urls[i],match=matches[0],header=None)[0].columns[0][1].replace('Updated: ', '').replace(' at ',' ').strip()
    except:
        #Print error and exit if this fails
        print('Update time load failed.')
        exit(1)
    try:
        df = pd.read_html(wayback_urls[i],match=matches[0], header=list(shape_dict.values())[0]['header_row'])[0].iloc[:, 0:list(shape_dict.values())[0]['column_count']]
        print('Reading: '+str(wayback_urls[i]))
    except:
        y+=1
        i+=1
        print(str(wayback_urls[i])+' failed to load.')
    else:
        #Add Timestamp
        df['timestamp'] = update_time

        ##WRITE FILES TO Google Sheets##
        #Authenticate and workbook
        gc = pygsheets.authorize(service_file='covid-gcreds.json')
        sh = gc.open('covid-19-maine')

        #Declare target sheet
        wks = sh.worksheet('index', 0)

        #Get target sheet as dataframe, standardize columns and combine with new load
        dfr = wks.get_as_df()
        dfr_col = dfr.columns

        print(dfr.columns)

        df = df.iloc[0:,0:4]
        df.columns = dfr.columns
        df = pd.concat([df,dfr]).drop_duplicates().reset_index(drop=True)

        #Truncate table and load modified dataframe
        wks.clear()
        wks.rows = df.shape[0]
        wks.set_dataframe(df, start='A1', nan='')

        ##WRITE FILES to data.world##
        with dw.open_remote_file('darrenfishell/covid-19-me', list(shape_dict.values())[0]['filename']+'.csv') as w:
            df.to_csv(w, index=False)

        i+=1
