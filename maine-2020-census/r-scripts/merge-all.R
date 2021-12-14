library(tidyverse)
library(magrittr)

total_pop_2020 <- part1_2020 %>%
                    select(FILEID, CHARITER, LOGRECNO, P0010001, P0010003) %>%
                    mutate(year = 2020)


total_pop_2010 <- part1_2010 %>%
                    select(FILEID, CHARITER, LOGRECNO, P0010001, P0010003) %>%
                    mutate(year = 2010)

pop_all <- union_all(total_pop_2010, total_pop_2020)

geo_subset_2010 <- header_2010 %>%  
                    select(STUSAB, SUMLEV, LOGRECNO, GEOCODE, COUSUB) %>% 
                    mutate(year = 2010)
                    

geo_subset_2020 <- header_2020 %>% 
                    select(STUSAB, SUMLEV, LOGRECNO, GEOCODE, COUSUB) %>%
                    mutate(year = 2020)

geo_subset <- union_all(geo_subset_2010, geo_subset_2020)

geo_subset$COUSUB <- str_pad(geo_subset$COUSUB, 5, "left", pad = "0")
geo_subset$LOGRECNO <- str_pad(geo_subset$LOGRECNO, 7, "left", pad = "0")

geo_subset <- geo_subset[as.integer(geo_subset$SUMLEV) == 60, ]

write.csv(geo_subset, "../data/me-geo-reference.csv")
write.csv(pop_all, "../data/2010-2020-population-compare.csv")
