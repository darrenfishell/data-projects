import pandas as pd
import requests
import config
import os
import datadotworld as dw
import pygsheets
import http.client
import json
import time
from pandas.io.json import json_normalize


class fecWrapper:

    def __init__(self):
        self.fec_key = os.environ['FEC_KEY']

    def get_cands(**kwargs):

        state = kwargs.get('state', '')
        cycle = kwargs.get('cycle', '')

        if cycle:
            print('Cycle')
        else:
            print('No cycle')

        exit()

        url = 'https://api.open.fec.gov/v1/candidates/search'

        for state in state:
            print(state)

            for cycle in cycle:
                print(cycle)
                params = {'election_year': cycle
                    , 'state': state
                    , 'api_key': config.fec_key
                    , 'is_active_candidate': True
                    , 'has_raised_funds': True
                          }

                r = requests.get(url, params=params).json()

                cand_all = []
                cands = json_normalize(data=r['results'])[['candidate_id'
                    , 'name'
                    , 'party_full'
                    , 'incumbent_challenge_full'
                    , 'office_full'
                    , 'first_file_date'
                                                           ]]

                comm = json_normalize(data=r['results'], record_path='principal_committees')
                comm = comm[['candidate_ids'
                    , 'committee_id'
                    , 'name']]

                comm['candidate_ids'] = comm['candidate_ids'].str[0]

                # Merge candidate and committee lookups
                cands = cands.merge(comm, left_on='candidate_id', right_on='candidate_ids')

                # Rename cols
                colnm = {
                    'name_x': 'candidate_name'
                    , 'name_y': 'committee_name'
                }

                cands.rename(columns=colnm, inplace=True)
                cands.drop(columns='candidate_ids', inplace=True)

                cand_all.append(cands)

        cand_all = pd.concat(cand_all, sort=False, ignore_index=True).drop_duplicates()

        return cand_all