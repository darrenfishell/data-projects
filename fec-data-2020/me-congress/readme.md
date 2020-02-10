##Maine campaign finance loader
This iPython notebook contains the components for downloading data for Maine congressional candidates from three different endpoints:

-Schedule A (campaign contributions)
-Schedule E (independent expenditures)
-Schedule F (party-coordinated expenditures)

The script here is not an ode to efficiency in code by any means, but provides a template for using the API to store and output files -- in this case, to data.world.

The production version of this code has a few modifications and runs on AWS' Lambda service nightly at 12:15 p.m.

The full code for that function is not published here, but the dependencies for the script are bundled together in this <a href="https://github.com/darrenfishell/data-projects/raw/master/fec-data-2020/me-congress/pandas-dw-pygsheets.zip">ZIP file</a>, which is ready to be deployed as a Lambda layer.

##Individual contributions
To prevent double-counting from political donation collector committees -- such as ActBlue or WinRed -- the scripts filter itemized contributions to only records where the field `is_individual` is True and where the flag `memoed_subtotal` is False.

##Output
The production script writes all columns of the FEC files to a [project](https://data.world/darrenfishell/2020-election-repo) at data.world.

The script also uses the datadotworld Python plugin to check the latest FEC query against existing data, with a rudimentary check to see if there are new records.

If so, the file is updated.

A query in data.world then summarizes these tables at the contributor and candidate level.

In production, a separate script, not included here, runs 30 minutes after the FEC load to pull down a query from data.world and write that to a [Google Sheet](https://docs.google.com/spreadsheets/d/12bHf1qEtKtGGje0a3lBJJ8r-IvYcs3yl5jxbP6jNMCo/edit#gid=182007484), with a detail and a summary tab.

This facilitates automatic nightly updates in Tableau Public, which only supports automatic refreshes through Google Sheets.

##Questions
If you have questions about the data, <a href='mailto:darren.fishell@gmail.com'>email</a> or <a href="http://twitter.com/darrenfishell">Tweet at</a> Darren Fishell.
