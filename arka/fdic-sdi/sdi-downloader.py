"""
Grabs the entire Federal Deposit Insurance Corporation (FDIC) Statistics on
Depository Institutions (SDI) data set.

Note that this is a large data set! There are roughly 85 zip files each of
which is between 40 and 84 MB.

"""
import pandas as pd
import requests

base_url = 'https://www5.fdic.gov/sdi/Resource/AllReps/All_Reports_'

# use pandas to construct a list of quarterly dates
present = '20181231'
datetimes = pd.date_range('19921231', end=present, freq='Q')
dates = datetimes.format(formatter=lambda t: t.strftime('%Y%m%d'))

for date in dates:

    # ...construct the url...
    tmp_url = base_url + date + '.zip'

    # ...make the connection and grab the zipped files...
    tmp_buffer = requests.get(tmp_url)

    # ...save them to disk...
    with open('All_Reports_' + date + '.zip', 'wb') as tmp_zip_file:
        tmp_zip_file.write(tmp_buffer.content)

    print('Done with files for ' + date + '!')