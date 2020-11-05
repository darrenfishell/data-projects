import fecWrapper
import dataDotWrapper
import gSheetsWrapper

def lambda_handler(event, context):

    fec = fecWrapper.FecFinder()
    dw = dataDotWrapper.dataDotWorld()
    gs = gSheetsWrapper.sheetsWriter()

    #FEC query params
    start_year = 2020
    end_year = 2020
    cycles = fec.year_gen(start_year, end_year)
    efile_start = '2020-07-01'
    states = ['ME']

    dw_repo = 'maine-federal-campaign-finance-tables'
    house_sheet = 'maine-house-2020'
    senate_sheet = 'maine-senate-2020'

    # #Pull in candidates
    candidates = fec.get_cands(state=states
                                , election_year=cycles
                                , is_active_candidate=True
                                , has_raised_funds=True
                                )

    # dw.file_merger(filename='candidate_committee_lkp'
    #                , repo=dw_repo
    #                , data=candidates
    #                , dupe_key='committee_id'
    #                )
    #
    # #Retrieve and write Schedule records
    # df = fec.summary_getter(cycle=cycles, candidates=candidates)
    #
    # dw.file_merger(filename='campaign_summaries'
    #                , repo=dw_repo
    #                , data=df
    #                , dupe_key='committee_id')
    #
    # df = fec.sched_a_getter(two_year_transaction_period=cycles, candidates=candidates)
    #
    # dw.file_merger(filename='itemized_contributions'
    #                , repo=dw_repo
    #                , data=df
    #                , dupe_key='transaction_id')
    #
    # df = fec.sched_e_getter(cycle=cycles, candidates=candidates)
    #
    # dw.file_merger(filename='independent_expenditures'
    #                , repo=dw_repo
    #                , data=df
    #                , dupe_key=['committee_id', 'transaction_id'])
    #
    # df = fec.sched_f_getter(cycle=cycles, candidates=candidates)
    #
    # dw.file_merger(filename='party_coordinated_expenditures'
    #                , repo=dw_repo
    #                , data=df
    #                , dupe_key=['candidate_id', 'transaction_id'])

    df = fec.efile_sched_a_getter(candidates=candidates
                                  , min_date=efile_start)

    dw.file_merger(filename='efiling-october-quarterly'
                   , repo=dw_repo
                   , data=df
                   , dupe_key='transaction_id')

    #Write data.world SQL view out to Google Sheets
    # Data.World queryid: GSheet mapping
    dw_query_sheet = {
        '026e8f40-d10e-4324-8b45-80dbc0e61627': 'individual-contributors'
        , 'e2b1bde2-1e60-4d49-bd31-da5aa7ce0611': 'campaign-summaries'
    }

    for queryid, tab in dw_query_sheet.items():

        df = dw.retrieve_query(queryid=queryid
                               , repo=dw_repo)

        house = df[df['office_full'] == 'House']
        senate = df[df['office_full'] == 'Senate']

        gs.write_to_sheets(sheet=house_sheet
                           , tab=tab
                           , data=house)

        gs.write_to_sheets(sheet=senate_sheet
                           , tab=tab
                           , data=senate)

lambda_handler(event=[], context={})