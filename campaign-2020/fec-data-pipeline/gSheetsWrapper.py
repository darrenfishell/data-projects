import pygsheets

class sheetsWriter:

    def __init__(self):
        self.gc = pygsheets.authorize(service_file='gcreds.json')

    def write_to_sheets(self, **kwargs):

        sheet = kwargs.get('sheet', None)
        tab = kwargs.get('tab', None)
        df = kwargs.get('data', None)

        # Prepare to load into Google Sheets
        sh = self.gc.open(sheet)
        wks = sh.worksheet('title', tab)

        rows = df.shape[0]
        cols = df.shape[1]

        cells = rows * cols

        if cells <= 5000000:
            wks.clear()
            # wks.rows = df.shape[0]
            wks.set_dataframe(df, start='A1', nan='')

            msg = f'Wrote query for {tab} to Google Sheet {sheet}.'

        else:
            msg = f'Write to {tab} of {sheet} failed.'

        print(msg)

