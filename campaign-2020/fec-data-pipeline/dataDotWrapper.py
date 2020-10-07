import datadotworld as dw
import http.client
import json
import pandas as pd
import os

class dataDotWorld:

    def __init__(self):
        self.api_key = os.environ.get('DW_AUTH_TOKEN', None)
        self.account = 'darrenfishell'
        self.api_base = 'https://api.data.world'

    def file_merger(self, **kwargs):
        """
        Merges new records with an existing table based on a specified "dupe_key,"
        which can be a single field or a list of columns by which to drop duplicates.

        Importantly, the data type must be properly configured after the initial write
        to DataDotWorld, so that these fields are compared consistently.

        :param kwargs:
        :return:
        """

        filename = kwargs.get('filename', None) + '.csv'
        table = kwargs.get('filename', None)
        query = 'SELECT * FROM ' + table
        repo = kwargs.get('repo', None)
        dupe_key = kwargs.get('dupe_key', None)
        url = os.path.join(self.account, repo)
        df = kwargs.get('data', None)

        try:
            results = dw.query(url, query).dataframe
        except:
            results = None

        if results is None:
            with dw.open_remote_file(url, filename) as w:
                df.to_csv(w, index=False)
            print(f'Wrote {filename} to {repo}.')

        else:
            df = pd.concat([df, results], sort=False, ignore_index=True).drop_duplicates(subset=dupe_key, keep='first')
            records = len(df)
            with dw.open_remote_file(url, filename) as w:
                df.to_csv(w, index=False)
            print(f'Wrote {records} records to {filename}.')

    def retrieve_query(self, **kwargs):

        query_endpt = '/v0/queries/'
        queryid = kwargs.get('queryid', None)
        repo = kwargs.get('repo', None)

        headers = {'authorization': "Bearer " + self.api_key}
        conn = http.client.HTTPSConnection("api.data.world")

        query_url = os.path.join(self.api_base, query_endpt, queryid)
        target = os.path.join(self.account, repo)

        conn.request("GET", query_url, headers=headers)

        data = conn.getresponse().read()

        # Execute Query
        results = dw.query(target, json.loads(data)['body']).dataframe

        conn.close()

        return results
