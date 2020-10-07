import os
import requests
import pandas as pd
import itertools
import time

from pandas.io.json import json_normalize

class FecFinder:

    def __init__(self):
        self.api_key = os.environ.get('FEC_KEY', None)
        self.base_url = 'https://api.open.fec.gov'
        self.version = 'v1/'
        self.cand_endpt = 'candidates/search'
        self.comm_endpt = 'committee/'
        self.ie_endpt = 'schedules/schedule_e/'
        self.coord_endpt = 'schedules/schedule_f/'
        self.indiv_endpt = 'schedules/schedule_a/'

    def year_gen(self, start_year, end_year):
        return [year for year in range(start_year, end_year + 1) if year % 2 == 0]

    def param_generator(self, **kwargs):
        """
        Generates params for all combinations of state
        and cycle, in addition to booleans.
        """

        iter_params = [
            'state'
            , 'election_year'
            , 'two_year_transaction_period'
            , 'cycle'
            , 'committee_id'
            , 'candidate_id'
        ]

        key = kwargs.get('dict', None)
        kwargs = {k: v for k, v in kwargs.items() if k in iter_params and v is not None}
        keys, values = zip(*kwargs.items())
        params = [dict(zip(keys, v)) for v in itertools.product(*values)]

        for param in params:
            param.update(key)

        return params

    def throttled_request(self, url, params):
        response = None
        ratelimit_remaining = 1000
        wait_time = 0.5
        if not ratelimit_remaining == 0:
            response = requests.get(url, params=params)
            ratelimit_remaining = int(response.headers['x-ratelimit-remaining'])

        if ratelimit_remaining == 0 or response.status_code == 429:
            while ratelimit_remaining == 0 or response.status_code == 429:
                wait_time *= 1.5
                print(f'API rate limit exceeded. Waiting {wait_time}s.')
                time.sleep(wait_time)
                response = requests.get(url, params=params)
                ratelimit_remaining = int(response.headers['x-ratelimit-remaining'])

        try:
            response = response.json()
        except:
            response = None

        return response

    def get_cands(self, **kwargs):
        """
        :params:
        election_year : str
        state : str
        is_active_candidate: boolean
        has_raised_funds: boolean

        :returns:
        List of candidates and committees
        """

        election_year = kwargs.get('election_year', None)
        state = kwargs.get('state', None)
        active_flag = kwargs.get('is_active_candidate', True)
        funds_flag = kwargs.get('has_raised_funds', True)

        url = os.path.join(self.base_url, self.version, self.cand_endpt)

        cand_fields = ['candidate_id'
            , 'name'
            , 'party_full'
            , 'incumbent_challenge_full'
            , 'office_full'
            , 'first_file_date'
            , 'last_file_date']

        comm_fields = ['candidate_ids'
            , 'cycles'
            , 'committee_id'
            , 'name']

        # Construct params dicts
        key_dict = {'api_key': self.api_key
            , 'is_active_candidate': active_flag
            , 'has_raised_funds': funds_flag}

        params = self.param_generator(dict=key_dict
                                      , state=state
                                      , election_year=election_year)

        cand_all = []

        for param in params:

            r = requests.get(url=url, params=param).json()
            page = r['pagination']['page']
            pages = r['pagination']['pages']

            while page <= pages:
                r = requests.get(url=url, params=param).json()

                page = r['pagination']['page']

                payload = r['results']

                cands = json_normalize(data=payload)[cand_fields]

                comms = json_normalize(data=payload, record_path='principal_committees')[comm_fields]

                comms['candidate_ids'] = comms['candidate_ids'].str[0]

                candidates = cands.merge(comms, left_on='candidate_id', right_on='candidate_ids')

                candidates.rename(columns={'name_x': 'candidate_name'
                                         , 'name_y': 'committee_name'}
                                         , inplace=True)

                candidates.drop(columns='candidate_ids', inplace=True)

                cand_all.append(candidates)

                page += 1

                param.update(page=page)

        cand_all = pd.concat(cand_all, sort=False, ignore_index=True).drop_duplicates(subset='committee_id')

        cand_all = cand_all.astype(str)

        cand_all.reset_index()

        return cand_all

    def sched_a_getter(self, **kwargs):

        candidates = kwargs.get('candidates', None)
        comm_ids = candidates['committee_id'].unique()
        election_year = kwargs.get('two_year_transaction_period', None)

        url = os.path.join(self.base_url, self.version, self.indiv_endpt)

        def get_unitemized():
            end = 'https://api.open.fec.gov/v1/committee/'

            key_dict = {
                'api_key': self.api_key
                , 'per_page': '100'
            }

            params = self.param_generator(dict=key_dict
                                          , cycle=election_year)

            udfs = []

            for commid in comm_ids:

                for param in params:

                    r = requests.get(end + commid + '/totals', params=param).json()

                    payload = r.get('results', None)

                    if payload:

                        df = json_normalize(data=payload)

                        udfs.append(df)

                    else:
                        continue

            udf = pd.concat(udfs, sort=False, ignore_index=True).drop_duplicates()

            return udf

        def reshape_unitemized(df, cols):

            udf = pd.DataFrame(columns=cols)

            sourcecols = ['committee_name'
                , 'party_full'
                , 'committee_id'
                , 'individual_unitemized_contributions'
                , 'coverage_end_date'
                , 'last_report_type_full']

            targetcols = ['committee.name'
                , 'committee.party_full'
                , 'committee_id'
                , 'contribution_receipt_amount'
                , 'contribution_receipt_date'
                , 'fec_election_type_desc']

            udf[targetcols] = df[sourcecols]

            udf['contributor_name'] = 'Unitemized individual contributions'
            udf['entity_type'] = 'IND'

            return df

        key_dict = {
            'per_page': '100'
            , 'sort': 'contribution_receipt_date'
            , 'api_key': self.api_key
            , 'is_individual': True
            , 'last_index': []
            , 'last_contribution_receipt_date': []
        }

        params = self.param_generator(dict=key_dict
                                      , two_year_transaction_period=election_year
                                      , committee_id=comm_ids)

        dfs = []

        for param in params:

            r = self.throttled_request(url, param)

            pages = r.get('pagination', {}).get('pages', None)

            year = param.get('two_year_transaction_period', None)

            if pages == 0:
                continue

            last_indexes = r.get('pagination', {}).get('last_indexes', None)
            pager = 0

            while last_indexes is not None:

                payload = r.get('results', None)

                dfs.append(json_normalize(payload))

                pager += 1

                last_date = r.get('pagination', {})\
                            .get('last_indexes', {})\
                            .get('last_contribution_receipt_date', None)

                last_index = r.get('pagination', {}) \
                            .get('last_indexes', {}) \
                            .get('last_index', None)

                param.update([('last_index', last_index)
                              , ('last_contribution_receipt_date', last_date)])

                r = self.throttled_request(url, param)

                last_indexes = r.get('pagination', {}).get('last_indexes', None)

            candidate = candidates.loc[candidates['committee_id'] == param.get('committee_id'), 'candidate_name'].max()

            print(f'Captured {pager} of {pages} pages for {year}, for candidate: {candidate}.')

        df = pd.concat(dfs, sort=False, ignore_index=True).drop_duplicates(subset='transaction_id')

        #Clean + filter steps
        df['contributor_zip'] = df['contributor_zip'].str[:5]
        df = df[(df['is_individual'] == True) | (df['memoed_subtotal'] == False)]

        cols = df.columns.values.tolist()
        udf = reshape_unitemized(get_unitemized(), cols)

        df = pd.concat([df, udf], sort=False, ignore_index=True)

        # Parse datetime
        df['contribution_receipt_date'] = df['contribution_receipt_date'].str.split('T', expand=True)[0]

        return df

    def sched_e_getter(self, **kwargs):

        candidates = kwargs.get('candidates', None)
        cand_ids = candidates['candidate_id'].unique()
        election_year = kwargs.get('cycle', None)

        url = os.path.join(self.base_url, self.version, self.ie_endpt)

        key_dict = {
            'per_page': '100'
            , 'api_key': self.api_key
            , 'last_index': []
            , 'last_expenditure_date': []
        }

        params = self.param_generator(dict=key_dict
                                      , two_year_transaction_period=election_year
                                      , candidate_id=cand_ids)

        dfs = []

        for param in params:

            r = self.throttled_request(url, param)

            pages = r.get('pagination', {}).get('pages', None)

            year = param.get('two_year_transaction_period', None)

            if pages == 0:
                continue

            last_indexes = r.get('pagination', {}).get('last_indexes', None)
            pager = 0

            while last_indexes is not None:

                payload = r.get('results', None)

                if payload is None:
                    break

                dfs.append(json_normalize(payload))

                pager += 1

                last_date = r.get('pagination', {}) \
                    .get('last_indexes', {}) \
                    .get('last_expenditure_date', None)

                last_index = r.get('pagination', {}) \
                    .get('last_indexes', {}) \
                    .get('last_index', None)

                param.update([('last_index', last_index)
                             , ('last_expenditure_date', last_date)])

                r = self.throttled_request(url, param)

                pagination = r.get('pagination', None)

                if pagination is None:
                    continue

                last_indexes = pagination.get('last_indexes', None)

            candidate = candidates.loc[candidates['candidate_id'] == param.get('candidate_id'), 'candidate_name'].max()

            print(f'Captured {pager} of {pages} pages for candidate in {year}: {candidate}.')

        df = pd.concat(dfs, sort=False, ignore_index=True).drop_duplicates(subset='transaction_id')

        #Cleaning steps
        df['committee.zip'] = df['committee.zip'].str[:5]
        df['expenditure_date'] = df['expenditure_date'].str.split('T', expand=True)[0]

        return df

    def sched_f_getter(self, **kwargs):

        candidates = kwargs.get('candidates', None)
        cand_ids = candidates['candidate_id'].unique()
        election_year = kwargs.get('cycle', None)
        url = os.path.join(self.base_url, self.version, self.ie_endpt)

        key_dict = {
            'per_page': '100'
            , 'api_key': self.api_key
        }

        params = self.param_generator(dict=key_dict
                                      , two_year_transaction_period=election_year
                                      , candidate_id=cand_ids)

        dfs = []

        for param in params:

            r = self.throttled_request(url, param)

            pages = r.get('pagination', None).get('pages', None)

            if pages is None:
                continue

            for page in range(1, pages):
                payload = r.get('results', None)

                if payload is None:
                    continue

                dfs.append(json_normalize(payload))

                param.update(page=page)

                r = self.throttled_request(url, param)

            candidate = candidates.loc[candidates['candidate_id'] == param.get('candidate_id'), 'candidate_name'].max()

            print(f'Captured {pages} pages for candidate: {candidate}.')

        df = pd.concat(dfs, sort=False, ignore_index=True).drop_duplicates(subset='transaction_id')

        # Cleaning steps
        df['commiteee.zip'] = df['committee.zip'].str[:5]

        return df

    def summary_getter(self, **kwargs):

        candidates = kwargs.get('candidates', None)
        comm_ids = candidates['committee_id'].unique()
        election_year = kwargs.get('cycle', None)
        url = os.path.join(self.base_url, self.version, self.comm_endpt)

        key_dict = {
            'per_page': '100'
            , 'api_key': self.api_key
        }

        params = self.param_generator(dict=key_dict
                                      , cycle=election_year)
        dfs = []

        for param in params:

            for id in comm_ids:

                url_id = os.path.join(url, id, 'totals')

                r = self.throttled_request(url_id, param)

                payload = r.get('results', None)

                if payload is None:
                    continue

                dfs.append(json_normalize(payload))

        df = pd.concat(dfs, sort=False, ignore_index=True).drop_duplicates()

        return df

