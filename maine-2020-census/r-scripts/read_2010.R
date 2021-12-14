#Load 2010 files

library(stringr)

header_file_path <- "../raw-data/me2010/megeo2010.pl"
part1_file_path  <- "../raw-data/me2010/me000012010.pl"

header_2010 <- read.delim(header_file_path, header=FALSE, colClasses="character", sep="")
part1_2010  <- read.delim(part1_file_path,  header=FALSE, colClasses="character", sep=",")


colnames(part1_2010) <- c("FILEID", "STUSAB", "CHARITER", "CIFSN", "LOGRECNO", 
                     paste0("P00", c(10001:10071, 20001:20073)))




header_2010 <- read.fwf(header_file_path,  
                        c(6, 2, 3, 2, 3, 2, 7, 1, 1, 2, 3, 2, 2, 5, 2, 2, 5, 2, 2, 6, 1, 4, 2, 5, 2, 2)
                        , header=FALSE)

colnames(header_2010) <- c("FILEID", "STUSAB", "SUMLEV", "GEOCOMP", "CHARITER", "CIFSN", "LOGRECNO", "REGION", "DIVISION", 
                           "STATE", "COUNTY", "COUNTYCC", "COUNTYSC", "COUSUB", "COUSUBCC", "COUSUBSC", "PLACE"
                           ,"PLACECC", "PLACESC", "TRACT", "BLKGRP", "BLOCK", "IUC", "CONCIT"
                           ,"CONCITCC", "CONCITSC")

colnames(header_2010)

header_2010 <- header_2010 %>% 
                mutate(GEOCODE = paste0(
                                    str_replace_na(STATE, replacement=''), 
                                    str_replace_na(str_pad(COUNTY, 3, "left", pad = "0"), replacement=''),
                                    str_replace_na(str_pad(COUSUB, 5, "left", pad = "0"), replacement=''),
                                    sep="")) %>% 
                filter(., SUMLEV == 60)


header_2010$LOGRECNO <- as.character(header_2010$LOGRECNO)

header_2010$COUSUB <- as.character(header_2010$COUSUB)

header_2010$SUMLEV <- as.character(header_2010$SUMLEV)

