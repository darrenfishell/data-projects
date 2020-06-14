import requests
import config
from fec_functions import *

end = 'https://api.open.fec.gov/v1/schedules/schedule_a/'
page_count = 0
state = 'ME'
cycle = '2020'

cands = get_cands(state, cycle)
ids = cands['committee_id']


for idx, commid in enumerate(ids):

    udf=[]
    end = 'https://api.open.fec.gov/v1/committee'
    params = {
        'api_key': config.fec_key
        , 'cycle': cycle
        , 'per_page': '100'
    }

    candidate = cands['candidate_name'][idx]
    path = os.path.join(end,commid,'totals')
    print(path)

    # Collect unitemized contributions
    r = requests.get(os.path.join(end,commid,'totals'), params=params).json()
    udf = json_normalize(r['results'])
    print(candidate)
    print(udf.head())



# for idx, commid in enumerate(ids):
#
#     params = {
#     'per_page': '100'
#     , 'sort': 'contribution_receipt_date'
#     , 'api_key': 'egxSs7endLz5xMuoprm5zfVZCeoyeZbO5D6HFzJz'
#     , 'is_individual': 'true'
#     , 'two_year_transaction_period': cycle
#     , 'last_index': []
#     , 'last_contribution_receipt_date': []
#     , 'committee_id': commid
#     }
#
#     # Initialize Schedule A request
#     r = requests.get(end, params=params).json()
#
#     try:
#         while r['pagination']['last_indexes'] is not None:
#             # print(r['results'])
#
#             last_index = r['pagination']['last_indexes']['last_index']
#             last_date = r['pagination']['last_indexes']['last_contribution_receipt_date']
#             params.update([('last_index', last_index)
#                               , ('last_contribution_receipt_date', last_date)])
#
#             r = requests.get(end, params=params).json()
#
#             print(json_normalize(r['results']).head())
#     except:
#         continue