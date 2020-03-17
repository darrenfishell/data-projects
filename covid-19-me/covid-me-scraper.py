import pandas as pd
import requests
import string
import time
import datadotworld as dw
import os
import random
from scrapy import Selector
from datetime import date

#Pull in Summary and case-level tables
case_summary = pd.read_html('https://www.maine.gov/dhhs/mecdc/infectious-disease/epi/airborne/coronavirus.shtml', match='COVID-19 Testing Data')[0]
cases = pd.read_html('https://www.maine.gov/dhhs/mecdc/infectious-disease/epi/airborne/coronavirus.shtml', match='COVID-19 Case Tracker')[0]

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

