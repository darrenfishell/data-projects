import pandas as pd
import requests
import os
import pygsheets
import http.client
import json

#Pull in Summary and case-level tables
try:
    case_summary = pd.read_html('https://www.maine.gov/dhhs/mecdc/infectious-disease/epi/airborne/coronavirus.shtml', match='COVID-19 Testing Data')[0]
except:
    print("Load of case summary table failed.")

try:
    cases = pd.read_html('https://www.maine.gov/dhhs/mecdc/infectious-disease/epi/airborne/coronavirus.shtml', match='COVID-19 Case Tracker')[0]
except:
    print("Load of cases table failed.")

#Extract update dates into separate variables, format as date
summary_update_time = str(case_summary.keys()[0][1]).replace('Updated: ','').strip()
case_update_time = str(cases.keys()[0][1]).replace('Updated: ','').strip()

## TRANSFORM RESPONSES INTO PROPER TABLES ##

#Pull out case titles, cull dataframe, apply titles, add timestamp
cases_titles = cases.iloc[0,1:5]
cases = cases.iloc[1:,1:5]
cases.columns = cases_titles

cases['timestamp'] = case_update_time

#Case titles of Total Confirmed, Total Presumptive Positive, Total Negative
summary_titles = case_summary.iloc[0,0:3]
case_summary = case_summary.iloc[1:,0:3]
case_summary.columns = summary_titles

case_summary['timestamp'] = summary_update_time

#SEND FILES TO data.world#
with dw.open_remote_file('darrenfishell/covid-19-me', 'maine-covid-19-cases.csv') as w:
    cases.to_csv(w, index=False)

with dw.open_remote_file('darrenfishell/covid-19-me', 'maine-covid-19-summary.csv') as w:
    case_summary.to_csv(w, index=False)

##WRITE FILES TO Google Sheets##
#Authorize
gc = pygsheets.authorize(service_file='covid-gcreds.json')

#Write Cases to sheet 1
sh = gc.open('covid-19-maine')
wks = sh.worksheet('index', 0)
wks.clear()
wks.rows = cases.shape[0]
wks.set_dataframe(cases, start='A1', nan='')

#Write summary to sheet 2
sh = gc.open('covid-19-maine')
wks = sh.worksheet('index', 1)
wks.clear()
wks.rows = case_summary.shape[0]
wks.set_dataframe(case_summary, start='A1', nan='')