import numpy as np
import pandas as pd
import requests
import os
import pygsheets
import http.client
import datadotworld as dw
import json
from io import StringIO
from pandas.io.json import json_normalize


years = ['2020']

class MaineEthics():

    def get_lookup(self,year):
        #Initialize session
        s = requests.Session()
        cookies = requests.cookies.RequestsCookieJar()

        url = 'https://mainecampaignfinance.com/api///Organization/SearchCandidates'

        self.year = year.split(',')

        cand_q = {"ElectionYear":,
                  "pageNumber": 1,
                  "pageSize": 2147483647}

        r = s.post(url, data=json.dumps(cand_q), headers=headers).json()
        df = json_normalize(r)

        with dw.open_remote_file('darrenfishell/2020-maine-state-campaign-finance', 'candidate_lookup.csv') as w:
            df.to_csv(w, index=False)


def get_spending():





## Set Variables ##
url = 'https://mainecampaignfinance.com/api///Search/TransactionSearchInformationExpExportToCSV'
url_base = 'https://mainecampaignfinance.com'

# Can search multiple, comma-separated
election_year = '2020,2019'

# Parameters for looping through search
committee_types = {'candidate': '01'
    , 'bqc': '02'
    , 'pac': '03'
    , 'party-committee': '09'}

transaction_types = {'contributions': 'CON'
    , 'expenditures': 'EXP'
    , 'independent_expenditures': 'IE'
    , 'ballot_questions': 'All'
                     }

trans_types = list(transaction_types.values())
filenames = list(transaction_types.keys())
comm_types = list(committee_types.values())

# Data dictionary for query
data = {"ElectionYear": election_year
    , "pageNumber": '1'
    , "pageSize": '2147483647'  # Sets max responses from page (defaults to 10)
    , "ValidationRequired": '0'}

# POST headers
headers = {'Host': 'mainecampaignfinance.com'
    , 'Origin': url_base
    , 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:69.0) Gecko/20100101 Firefox/69.0'
    , 'Accept': 'application/octet-stream'
    , 'Accept-Language': 'en-US,en;q=0.5'
    , 'Accept-Encoding': 'gzip, deflate, br'
    , 'Referer': 'https://mainecampaignfinance.com/'
    , 'Content-Type': 'application/json;charset=utf-8'
    , 'Connection': 'keep-alive'
    , 'TE': 'Trailers'
    , 'Pragma': 'no-cache'
    , 'Cache-Control': 'no-cache'}

# GET SPENDING REPORTS#
# Set index
x = 0
for b in trans_types:

    data.update({"TransactionType": trans_types[x]})

    # Declare/reset df and reset index
    dfs = []
    i = 0

    for n in comm_types:
        data.update({"CommitteeType": comm_types[i]})

        r = s.post(url, data=json.dumps(data), headers=headers)
        df = pd.read_csv(StringIO(r.content.decode('utf-8')))
        df['comm_type'] = comm_types[i]
        dfs.append(df)
        i += 1

    # Combine dfs
    df = pd.concat(dfs, sort=False, ignore_index=True).drop_duplicates()

    # count = dw.query('darrenfishell/2020-maine-state-campaign-finance', 'SELECT COUNT(*) FROM '+filenames[x]).dataframe['count'][0]
    # if count < len(df):
    print('Writing file ' + filenames[x] + '.csv to data.world, at ' + str(len(df)) + ' records.')
    with dw.open_remote_file('darrenfishell/2020-maine-state-campaign-finance', filenames[x] + '.csv') as w:
        df.to_csv(w, index=False)

    # Advance to next transaction type
    x += 1



# GET QUESTION ONE COMMITTEES#
url = 'https://mainecampaignfinance.com/api///Organization/SearchAssociatedBallotQuestionCommittees'

vax_dict = {"BallotQuestionTypeId": "322"
    , "ElectionYear": "2020"
    , "pageNumber": "1"
    , "pageSize": '10'
    , "sortDir": "desc"
    , "sortedBy": ""}

r = s.post(url, data=json.dumps(vax_dict), headers=headers).json()

df = json_normalize(r)

with dw.open_remote_file('darrenfishell/2020-maine-state-campaign-finance', 'question-one-committees.csv') as w:
    df.to_csv(w, index=False)