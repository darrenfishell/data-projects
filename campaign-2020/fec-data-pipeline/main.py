import fecWrapper
import dataDotWrapper
import gSheetsWrapper

def lambda_handler(event, context):

    fec = fecWrapper.FecFinder()
    dw = dataDotWrapper.dataDotWorld()
    gs = gSheetsWrapper.sheetsWriter()

    #FEC query params
    start_year = 2008
    end_year = 2020
    cycles = fec.year_gen(start_year, end_year)
    states = ['ME']

    dw_repo = 'maine-federal-campaign-finance-tables'
    gsheet = 'maine-congress-2020'

    #Data.World queryid: GSheet mapping
    dw_query_sheet = {
        '026e8f40-d10e-4324-8b45-80dbc0e61627': 'individual-contributors'
        , 'e2b1bde2-1e60-4d49-bd31-da5aa7ce0611': 'campaign-summaries'
    }

    #Pull in candidates
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

    df = fec.sched_e_getter(cycle=cycles, candidates=candidates)

    dw.file_merger(filename='independent_expenditures'
                   , repo=dw_repo
                   , data=df
                   , dupe_key=['committee_id', 'transaction_id'])

    # df = fec.sched_f_getter(cycle=cycles, candidates=candidates)
    #
    # dw.file_merger(filename='party_coordinated_expenditures'
    #                , repo=dw_repo
    #                , data=df
    #                , dupe_key=['candidate_id', 'transaction_id'])
    #
    # #Write data.world SQL view out to Google Sheets
    # for queryid, tab in dw_query_sheet.items():
    #
    #     df = dw.retrieve_query(queryid=queryid
    #                            , repo=dw_repo)
    #
    #     gs.write_to_sheets(sheet=gsheet
    #                        , tab=tab
    #                        , data=df)
    #
    #     print(f'Wrote query for {tab} to Google Sheet {gsheet}.')

lambda_handler(event=[], context={})