#Processing the latest biomass data for Tableau

#Set directory to biomass folder
setwd("~/Documents/Github clones/BDN-Data/analyses/biomass-contract")

#Load Stored Solar data
RE_Actual_Output_Table_1 <- read_csv("~/Desktop/{9D7BEF74-9C75-48C6-9C05-101A8CA0AB22} - RE Actual Output.csv", skip = 3)

#Load ReEnergy data
SS_Actual_Output_Table_1 <- read_csv("~/Desktop/{9D7BEF74-9C75-48C6-9C05-101A8CA0AB22} - SS Actual Output.csv")
#Merge tables
dat<-merge(SS_Actual_Output_Table_1, RE_Actual_Output_Table_1, by = c("Hour","Date"))

#Write file
write.csv(dat,"stored-solar-reenergy-combined.csv")
