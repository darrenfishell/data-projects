# Maine COVID-19 tracker
The script covid-me-scraper.py contains a basic scraper for pulling in data from two tables at the [Maine CDC's coronavirus webpage](https://www.maine.gov/dhhs/mecdc/infectious-disease/epi/airborne/coronavirus.shtml).

The scraper outputs the files to data.world and Google Sheets, to enable visualization. This repository also contains a reference population file by county, for calculating per capita rates.

_As of March 17:_ The CDC's reporting method may change as the pandemic spreads, which stands to break the scraper as written.