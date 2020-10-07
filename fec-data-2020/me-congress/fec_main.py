from fec_functions import *
import time

def lambda_handler(event, context, get_ies=None):
    # start = time.time()
    # # Step 1: Set state(s) and cycle(s) for candidate search
    # state = 'ME'
    # cycle = '2020'
    #
    # # Query candidates and write to data.world
    # try:
    #     cands = get_cands(state, cycle)
    #     write_cands(cands)
    #     length = len(cands)
    #     print(f'Wrote {length} candidate records to data.world.')
    # except:
    #     print('Candidate lookup query failed.')
    #
    # # Get - write contribution pairs
    # getwrite = {
    #     get_itemized: write_indiv,
    #     get_summary: write_summary,
    #     get_ies: write_ies,
    #     get_coordinated: write_coord
    # }
    #
    # # Filename - input pairs
    # files_input = {
    #     'itemized contributions': [cycle, cands],
    #     'campaign summary': [cycle, cands],
    #     'independent expenditures': [cycle, cands],
    #     'party coordinated expenditures': [cycle, cands]
    # }
    #
    # # List of functions, filenames and inputs to unpack
    # files = [x[0] for x in list(files_input.items())]
    # params = [x[1] for x in list(files_input.items())]
    #
    # # Iterate over all get-write functions, with TRY
    # for idx, (get, write) in enumerate(getwrite.items()):
    #
    #     # Set filename
    #     file = files[idx]
    #
    #     # Run function r, return dataframes
    #     df = get(*params[idx])
    #
    #     # Execute write functions to write to datadotworld
    #     newtest, oldlen, newlen = write(df)
    #     newrecords = newlen - oldlen
    #
    #     if newtest:
    #         print(f'Wrote {newrecords} new records to {file}, which now has {newlen}.')
    #     else:
    #         print(f'No update to {file}, which has {newlen} records.')
    #
    # end = time.time()
    # duration = end - start
    # print(f'Script ran for {duration}')

    try:
        write_to_gsheet()
        print('Wrote to GSheets')
    except:
        print('Failed to write to GSheet')

##TESTING
test_event = {
  "key1": "value1",
  "key2": "value2",
  "key3": "value3"
}
event = []

lambda_handler(event, test_event)