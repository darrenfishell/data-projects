import os
import pandas as pd
import requests
import time

from pandas.io.json import json_normalize

base_url = 'https://publicfiles.fcc.gov/api/service/'

def throttled_request(url):
    wait_time = 0.5

    r = requests.get(url=url).json()
    status = r['status']

    while status != 'OK':
        wait_time *= 1.5
        print(f'API rate limit exceeded. Waiting {wait_time}s.')
        time.sleep(wait_time)
        r = requests.get(url=url).json()
        status = r['status']

    payload = r['results']
    df = json_normalize(data=payload)

    return df

def station_getter():
    tail = 'facility/getall.json'
    mediums = ['tv', 'am', 'fm']

    dfs = []

    for medium in mediums:
        url = os.path.join(base_url, medium, tail)
        r = requests.get(url=url).json()
        payload = r['results']
        facilities = json_normalize(data=payload, record_path='facilityList')
        facilities['medium'] = medium
        dfs.append(facilities)

    df = pd.concat(dfs, sort=False, ignore_index=True).drop_duplicates()

    df = df[df['activeInd'] == 'Y']

    return df

def get_facility_detail(facilities, states):

    lkp_dict = dict(zip(facilities.iloc[:, 0], facilities.iloc[:, 4]))
    count = len(lkp_dict)
    i = 0
    dfs = []

    for key, medium in lkp_dict.items():
        tail = 'facility/'
        url = os.path.join(base_url, medium, tail, 'id/', f'{key}.json')

        df = throttled_request(url)

        state = df['facility.communityState'].iloc[0]

        if state in states:
            dfs.append(df)
            print(f'Loaded facility: {key}')

        i+=1

        if i % 10 == 0:
            print(f'Index: {i} of {count}')

    df = pd.concat(dfs, sort=False, ignore_index=True).drop_duplicates()

    return df






