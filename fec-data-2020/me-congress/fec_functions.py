import pandas as pd
import requests
import config
import datadotworld as dw
import pygsheets
import http.client
import json
import time
from pandas.io.json import json_normalize

##Schedule_a API guide: https://api.open.fec.gov/developers/#/receipts/get_schedules_schedule_a_˜

##Define functions
def get_cands(state, cycle):
    state = state.split(',')
    cycle = cycle.split(',')
    end = 'https://api.open.fec.gov/v1/candidates/search'

    for state in state:
        
        for cycle in cycle:
            params = {'election_year': cycle
                      , 'state': state
                      , 'api_key': config.fec_key
                      , 'is_active_candidate': True
                      , 'has_raised_funds': True
                      }

            r = requests.get(end, params=params).json()

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

def get_committees(names):
    names = names.split(',')

    comms = []
    end = 'https://api.open.fec.gov/v1/names/committees'

    for name in names:
        params = {'q': name
            , 'api_key': config.fec_key}

        r = requests.get(end, params=params).json()

        comm = json_normalize(data=r['results'])

        comms.append(comm)

    comm_all = pd.concat(comms, sort=False, ignore_index=True).drop_duplicates()

    return comm_all


def get_itemized(cycle, cands):

    def get_unitem(cycle, commid):

        end = 'https://api.open.fec.gov/v1/committee/'
        params = {
            'api_key': config.fec_key
            , 'cycle': cycle
            , 'per_page': '100'
            , 'committee_id': commid
        }
        # Collect unitemized contributions
        r = requests.get(end + commid + '/totals', params=params).json()
        udf = json_normalize(r['results'])
        return udf

    cycle = cycle.split(',')
    end = 'https://api.open.fec.gov/v1/schedules/schedule_a/'
    ids = cands['committee_id']
    dfs = []
    udfs = []
    page_count = 0
    r_count = 0
    cand_count = len(cands)
    for_start = time.time()

    for idx, commid in enumerate(ids):
        item_page = 0

        params = {
            'per_page': '100'
            , 'sort': 'contribution_receipt_date'
            , 'api_key': config.fec_key
            , 'is_individual': 'true'
            , 'two_year_transaction_period': cycle
            , 'last_index': []
            , 'last_contribution_receipt_date': []
            , 'committee_id': commid
        }

        try:
            udfs.append(get_unitem(cycle, commid))
        except:
            continue

        # Initialize Schedule A request
        r = requests.get(end, params=params).json()
        r_count += 1

        candidate = cands['candidate_name'][idx]

        try:
            pages = r['pagination']['pages']

            while r['pagination']['last_indexes'] is not None:
                df = json_normalize(r['results'])
                dfs.append(df)

                last_index = r['pagination']['last_indexes']['last_index']
                last_date = r['pagination']['last_indexes']['last_contribution_receipt_date']

                params.update([('last_index', last_index)
                                  , ('last_contribution_receipt_date', last_date)])

                r = requests.get(end, params=params).json()
                r_count += 1
                page_count += 1
                item_page += 1

                for_duration = time.time() - for_start
                r_rate = r_count / for_duration

                if r_rate >= 1.8:
                    print(f'Hit rate {r_rate} on {candidate} page {page_count}')
                    time.sleep(.5)

        except:
            print(f'Broke on page {item_page} for {candidate}.')
            print(f'Last index: {last_index} //n Last date: {last_date} //n commid: {commid}')
            print(r['pagination']['last_indexes'])

        print(f'Reached page {item_page} of {pages} for {candidate}.')

    print(f'{page_count} pages for {cand_count} candidates')

    # After for loop, concatenate dfs
    df = pd.concat(dfs, sort=False, ignore_index=True).drop_duplicates(subset='transaction_id')
    ustore = pd.concat(udfs, sort=False, ignore_index=True).drop_duplicates()

    # Clean dataframe
    df['contributor_zip'] = df['contributor_zip'].str[:5]

    # Filter to is_individual and no memoed subtotal
    df = df[(df['is_individual'] == True) | (df['memoed_subtotal'] == False)]

    # Transform unitemized table, based on df structure
    cols = df.columns.values.tolist()
    udf = pd.DataFrame(columns=cols)

    targetcols = ['committee.name'
        , 'committee.party_full'
        , 'committee_id'
        , 'contribution_receipt_amount'
        , 'contribution_receipt_date'
        , 'fec_election_type_desc']

    sourcecols = ['committee_name'
        , 'party_full'
        , 'committee_id'
        , 'individual_unitemized_contributions'
        , 'coverage_end_date'
        , 'last_report_type_full']

    udf[targetcols] = ustore[sourcecols]

    # Add labels
    udf['contributor_name'] = 'Unitemized individual contributions'
    udf['entity_type'] = 'IND'

    # Combine dataframes
    df = pd.concat([df, udf], sort=False, ignore_index=True)

    # Parse datetime
    df['contribution_receipt_date'] = df['contribution_receipt_date'].str.split('T', expand=True)[0]

    return df


def get_ies(cycle, cands):
    cycle = cycle.split(',')
    end = 'https://api.open.fec.gov/v1/schedules/schedule_e/'
    ids = cands['candidate_id']
    dfs = []

    for idx, item in enumerate(ids):

        params = {
            'per_page': '100'
            , 'api_key': config.fec_key
            , 'cycle': cycle
            , 'last_index': []
            , 'last_expenditure_date': []
            , 'candidate_id': item
        }

        r = requests.get(end, params=params).json()

        candidate = cands['candidate_name'][idx]

        try:
            pages = str(r['pagination']['pages'])
        except:
            pages = 0

        if pages == 0:
            df = json_normalize(r['results'])
            dfs.append(df)
        else:
            while r['pagination']['last_indexes'] is not None:
                df = json_normalize(r['results'])
                dfs.append(df)

                last_index = r['pagination']['last_indexes']['last_index']
                last_date = r['pagination']['last_indexes']['last_expenditure_date']

                params.update([('last_index', last_index)
                                  , ('last_expenditure_date', last_date)])

                r = requests.get(end, params=params).json()

    # After for loop, concatenate dfs
    df = pd.concat(dfs, sort=False, ignore_index=True).drop_duplicates(subset='transaction_id')

    # Clean dataframe
    df['commiteee.zip'] = df['committee.zip'].str[:5]
    df['expenditure_date'] = df['expenditure_date'].str.split('T', expand=True)[0]

    return df


def get_coordinated(cycle, cands):
    cycle = cycle.split(',')
    end = 'https://api.open.fec.gov/v1/schedules/schedule_f/'
    ids = cands['candidate_id']
    dfs = []

    for i, item in enumerate(ids):

        params = {
            'per_page': '100'
            , 'api_key': config.fec_key
            , 'two_year_transaction_period': cycle
            , 'page': 1
            , 'candidate_id': item
        }

        r = requests.get(end, params=params).json()

        current_pg = r['pagination']['page']
        all_pgs = r['pagination']['pages']

        candidate = cands['candidate_name'][i]

        for page in range(all_pgs):
            params.update([('page', page + 1)])
            r = requests.get(end, params=params).json()

            df = json_normalize(r['results'])
            dfs.append(df)

    # After for loop, concatenate dfs
    df = pd.concat(dfs, sort=False, ignore_index=True).drop_duplicates(subset='transaction_id')

    # Clean dataframe
    df['commiteee.zip'] = df['committee.zip'].str[:5]

    return df


def get_summary(cycle, cands):
    cycle = cycle.split(',')
    end = 'https://api.open.fec.gov/v1/committee/'
    ids = cands['committee_id']
    dfs = []

    for idx, id in enumerate(ids):
        params = {
            'api_key': config.fec_key
            , 'cycle': cycle
            , 'per_page': '100'
        }

        r = requests.get(end + id + '/totals', params=params).json()
        try:
            df = json_normalize(r['results'])
        except:
            continue

        dfs.append(df)

    # After for loop, concatenate dfs
    df = pd.concat(dfs, sort=False, ignore_index=True).drop_duplicates()

    return df

def write_cands(df):
    with dw.open_remote_file('darrenfishell/2020-election-repo', 'candidate_committee_lookup.csv') as w:
        df.to_csv(w, index=False)


def write_indiv(df):
    results = dw.query('darrenfishell/2020-election-repo', 'SELECT * FROM individual_congressional_contributions')
    oldlen = len(results.dataframe)
    newlen = len(df)

    test = oldlen < newlen

    if test:
        with dw.open_remote_file('darrenfishell/2020-election-repo', 'individual-congressional-contributions.csv') as w:
            df.to_csv(w, index=False)
    return test, oldlen, newlen


def write_summary(df):
    results = dw.query('darrenfishell/2020-election-repo', 'SELECT * FROM congress_financial_summaries')
    oldcash = sum(results.dataframe['receipts'])
    oldlen = len(results.dataframe)
    newcash = sum(df['receipts'])
    newlen = len(df)

    test = oldcash < newcash

    if test:
        with dw.open_remote_file('darrenfishell/2020-election-repo', 'congress_financial_summaries.csv') as w:
            df.to_csv(w, index=False)
    return test, oldlen, newlen


def write_ies(df):
    results = dw.query('darrenfishell/2020-election-repo', 'SELECT * FROM congress_independent_expenditures')
    oldlen = len(results.dataframe)
    newlen = len(df)

    test = oldlen < newlen

    if test:
        with dw.open_remote_file('darrenfishell/2020-election-repo', 'congress-independent-expenditures.csv') as w:
            df.to_csv(w, index=False)
    return test, oldlen, newlen


def write_coord(df):
    results = dw.query('darrenfishell/2020-election-repo', 'SELECT * FROM congress_party_coordinated_expenditures')
    oldlen = len(results.dataframe)
    newlen = len(df)

    test = oldlen < newlen

    if test:
        with dw.open_remote_file('darrenfishell/2020-election-repo',
                                 'congress-party-coordinated-expenditures.csv') as w:
            df.to_csv(w, index=False)
    return test, oldlen, newlen


def write_to_gsheet():
    gc = pygsheets.authorize(service_file='gcreds.json')
    conn = http.client.HTTPSConnection("api.data.world")
    headers = {'authorization': "Bearer " + config.dw_key}

    sheets_to_dw = [['maine-congress-2020', 'e2b1bde2-1e60-4d49-bd31-da5aa7ce0611', 1],
                    ['maine-congress-2020', '026e8f40-d10e-4324-8b45-80dbc0e61627', 0]]

    for idx, sheet in enumerate(sheets_to_dw):
        sheet = [x[0] for x in sheets_to_dw][idx]
        queryid = [x[1] for x in sheets_to_dw][idx]
        gsh_idx = [x[2] for x in sheets_to_dw][idx]

        # Retrieve query
        conn.request("GET", "/v0/queries/" + queryid, headers=headers)
        data = conn.getresponse().read()
        # Execute Query
        results = dw.query('darrenfishell/2020-election-repo', json.loads(data)['body']).dataframe

        # Prepare to load into Google Sheets
        sh = gc.open(sheet)
        wks = sh.worksheet('index', gsh_idx)
        wks.clear()
        wks.rows = results.shape[0]
        wks.set_dataframe(results, start='A1', nan='')