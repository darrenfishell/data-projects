from fecWrapper import *
import time

def lambda_handler(event, context):
    start = time.time()
    # Step 1: Set state(s) and cycle(s) for candidate search
    state = ['ME', 'OH', 'TN']
    cycle = '2020'

    # Query candidates and write to data.world
    try:
        cands = fecWrapper.get_cands(state=state, cycle=cycle)
        print(cands)
        length = len(cands)
        print(f'Retrieved {length} candidate records.')
    except:
        print('Candidate lookup query failed.')



##TESTING
test_event = {
  "key1": "value1",
  "key2": "value2",
  "key3": "value3"
}
event = []

lambda_handler(event, test_event)