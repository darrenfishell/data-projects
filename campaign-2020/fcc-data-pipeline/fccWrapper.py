import os
import pandas as pd
import requests
import time

from pandas.io.json import json_normalize

base_url = 'https://publicfiles.fcc.gov/api'

def get_facility(url):
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

def get_folders(url):
    wait_time = 0.5

    r = requests.get(url=url).json()
    status = r['statusCode']

    while status != 200:
        wait_time *= 1.5
        print(f'API rate limit exceeded. Waiting {wait_time}s.')
        time.sleep(wait_time)
        r = requests.get(url=url).json()
        status = r['statusCode']

    payload = r['folders']
    df = json_normalize(data=payload)

    return df

def station_getter():
    tail = 'service/facility/getall.json'
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
        tail = 'service/facility/'
        url = os.path.join(base_url, medium, tail, 'id/', f'{key}.json')

        df = get_facility(url)

        state = df['facility.communityState'].iloc[0]

        if state in states:
            dfs.append(df)
            print(f'Loaded facility: {key}')

        i+=1

        if i % 10 == 0:
            print(f'Index: {i} of {count}')

    df = pd.concat(dfs, sort=False, ignore_index=True).drop_duplicates()

    return df

def create_ref():

    df = pd.read_csv('data/me-station-detail.csv')
    ref = pd.read_csv('data/all-station-list.csv')
    df = df.merge(ref, left_on='facility.id', right_on='id')

    ref = dict(zip(df['id'], df['medium']))

    return ref

def get_public_files(dict):

    count = len(dict)
    i = 0
    dfs = []

    for id, medium in dict.items():

        pol_tail = f'manager/folder/parentFolders.json?entityId={id}&sourceService={medium}'
        more_tail = f'manager/folder/morePublicFolders.json?entityId={id}&sourceService={medium}'

        pol_url = os.path.join(base_url, pol_tail)
        more_url = os.path.join(base_url, more_tail)

        urls = [pol_url, more_url]

        for url in urls:

            df = get_folders(url)
            df = df[df['folder_name'].str.contains('Political')]

            dfs.append(df)

        i+=1

        if i % 10 == 0:
            print(f'Index: {i} of {count}')

    df = pd.concat(dfs, sort=False, ignore_index=True).drop_duplicates()

    df.to_csv('data/me-political-file-ids.csv', index=False)

    return df








