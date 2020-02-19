## Comparing retail supply to the standard offer

These raw files and Tableau Prep workflow produce a file that can be used for analysis of retail power supplier prices in Maine, by year.

This builds on past work I did for the [Power Grab series](http://bangordailynews.com/series/powergrab/), published by the Bangor Daily News, standardizing and improving on the data processing behind that work.

The largest change is that the reports now assess variance from the standard offer based on going rates in each of Maine's two regional utility grids: [ISO-New England](http://bangordailynews.com/series/powergrab/) and the [Northern Maine Independent System Administrator](https://www.nmisa.com/), which is a part of the grid operated by the New Brunswick System Operator (NBSO).

### Raw files

This workflow ingests files from three sources:

* The "Sales to Ultimate Customers" file from the [U.S. Energy Information Administration's Form-861](https://www.eia.gov/electricity/data/eia861/).
* [Customer migration statistics](https://www.maine.gov/mpuc/electricity/choosing_supplier/migration_statistics.shtml) from the Maine Public Utilities Commission, which breaks out monthly totals of customers and load served by the standard offer and retail suppliers for each utility and customer size. The file for load provides an estimated daily average, which is annualized in a second, "high-cost scenario" that considers residential and small business customers.
* Historical standard offer power rates compiled from the [Maine Public Utilities Commission's website](https://www.maine.gov/mpuc/electricity/standard_offer_rates/index.html).

### The workflows

There are two workflows used to process these files.

The first handles the customer migration statistics, transforming the file into a more machine-friendly format for analysis of the share of customers and the share of power load served by retail suppliers and the standard offer, at each level of detail in the data source (customer size, utility, and month).

The second workflow processes the Form-861 files and the table of historical standard offer prices.

This workflow produces two outputs: (1) an estimate of the premium paid to retail suppliers based entirely on the standard offer information and the Form-861 data and (2) a higher estimate of the premium paid using the load data supplied by the Maine Public Utilities Commission.

The usage data from the MPUC and the EIA vary in the universe of customers they consider. The EIA data only represents residential customers.

The PUC data only shows customers in the small class, which includes some small business customers. Those customers typically pay the same rates as residential customers, which is why I've extended this analysis as a high range of the premium paid.

The MPUC's official report only considered the EIA data and the figures for residential customers.

### The process

#### Residential scenario

The first Tableau Prep workflow, `standard-offer-load-shares.tfl`, deals only with the MPUC migration data.

It produces two summary files, one that shows the retail supplier (CEP load) by month for each utility region; another breaks out the power load served through the standard offer, by month and utility.

These two files are fed into the second workflow, `cep-price-comparison.tfl`.

This file ingests the standard offer prices and assigns a region to each of Maine's three major utility districts: Central Maine Power, Emera Maine's Bangor Hydro District and Emera Maine's Maine Public Service District.

The monthly standard offer rates table is joined with the table summarizing the load served by each utility. Those load totals are then multiplied with the price information to generate a weighted average standard offer price for the whole state (ISONE and NBSO) and for ISONE, which contains two different rates through CMP and Emera Maine's Bangor Hydro District.

The weighted standard offer table is then joined with the supplier information, which indicates the regional grid supplied (ISONE or NBSO), but not the utility.

This level of detail is a key difference from past analyses, which estimated the price difference based on a statewide weighted average alone. In years where the NBSO standard offer was higher than the ISONE standard offer, this reduced the estimate of Electricity Maine's above-market costs.

These tables produce the "low-cost scenario" estimate, which simply calculates the difference between the weighted standard offer rate and the average annual supplier rate and then multiplies that by the load served by the retail supplier in a given year.

This produces our final "what-if" number for each supplier: how would the cost have differed if all of that electricity was instead purchased at the weighted standard offer rate?

#### Residential + small business scenario

The second scenario considers a summary of all retail supplier data at the regional grid level -- ISO or NBSO.

The summary table shows only the MWh and revenue from retail suppliers, by year and regional grid.

This summary information then generates an annual average retail supplier price, by year and regional grid.

This is then joined with two files -- one showing annual CEP load by utility, annualized from the MPUC file showing retail supplier load for "small class" customers, which includes small businesses and residential customers.

It should be noted that the source file reflects an average daily load by customer class. That number is extrapolated out to a yearly value.

It is also joined with the same weighted standard offer price file used in the low-cost estimate.

This load data then gives a higher estimate of retail supply usage than the EIA source, which only includes residential customers.

The same comparison is then made at the regional utility level, comparing the average retail price to the weighted average or average standard offer price by regional utility.

The "what-if" scenario in this case then asks: what if all power in the small class for those years were purchased at the standard offer price?
