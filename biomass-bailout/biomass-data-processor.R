#Processing the latest biomass data for Tableau

#Set directory to biomass folder
setwd("~/Github clones/data-projects/biomass-bailout/raw")

#Import Stored Solar data
library(readxl)
StoredSolar <- read_excel("12-31-2018.xlsx", 
                                                      sheet = "SS Actual Output", col_types = c("date", 
                                                                                                "numeric", "numeric", "numeric", 
                                                                                                "numeric", "text", "numeric", "numeric", 
                                                                                                "numeric"))
#Import ReEnergy data
library(readxl)
ReEnergy <- read_excel("12-31-2018.xlsx", 
                                                      sheet = "RE Actual Output", col_types = c("date", 
                                                                                                "numeric", "numeric", "numeric", 
                                                                                                "numeric", "numeric", "numeric", 
                                                                                                "text", "numeric", "numeric", "numeric"), 
                                                      skip = 3)

#Remove rows with Null hour records
StoredSolar <- StoredSolar[!(is.na(StoredSolar$Hour) | StoredSolar$Hour==""),]
ReEnergy <- ReEnergy[!(is.na(ReEnergy$Hour) | ReEnergy$Hour==""),]

#Merge tables
dat<-merge(x = StoredSolar, y = ReEnergy, by = c("Hour","Date"), all = TRUE)



#Write file
write.csv(dat,"stored-solar-reenergy-combined.csv")
