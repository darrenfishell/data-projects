library(readr)
library(lettercase)

vehicles <- read_fwf("BND_vehicle_by_town.txt", fwf_widths(c(5,51,5,7,5,5),
                    c("geocode","city","make","model",
                      "year","count"))
)

vehicles$city <- str_to_title(vehicles$city)
vehicles$model <- str_to_title(vehicles$model)
vehicles$make <- str_to_title(vehicles$make)

vehicles$county_code <- substr(vehicles$geocode, start = 1, stop = 2)
vehicles$muni_code <- substr(vehicles$geocode, start = 3, stop = 5)

setwd("~/Documents/Github clones/BDN-Data/analyses/vehicle-registrations/data")

write_csv(vehicles,"vehicle-reg.csv")
