library(googledrive)
library(readr)
library(tidyr)
library(dplyr)
library(fuzzyjoin)

# Use Oauth token to authorize access
drive_auth("ttt.rds") # from .rds file

## Download Sheet as csv, explicit type
movie_ratings <- drive_download("Movie Mondays", type = "csv", overwrite = TRUE)


Movie_Mondays <- read_csv("Movie Mondays.csv", 
                          col_types = cols(X1 = col_date(format = "%m/%d/%Y"),
                                            X17 = col_skip(), X18 = col_skip(),
                                            X43 = col_skip(), X44 = col_skip()
                                           ,X45 = col_skip(), X46 = col_skip()
                                           ,X47 = col_skip(), X48 = col_skip()
                                           ,X49 = col_skip()), 
                          skip = 5)

colnames(Movie_Mondays)[1] <- 'Date'
colnames(Movie_Mondays)[2] <- 'Title'

# Clear ugly bottom rows
Movie_Mondays <- drop_na(Movie_Mondays,'Date')

# Bring in IMDB data
imdbtitles <- read_tsv("https://datasets.imdbws.com/title.basics.tsv.gz", locale = locale(encoding = 'ISO-8859-1'))

# Filter to only 'movies' and remove duplicate rows
imdbtitles <- imdbtitles[imdbtitles$titleType=='movie', ]
imdbtitles <- imdbtitles[!duplicated(imdbtitles), ]

#Make title fields lowercase (for join)
imdbtitles$primaryTitle <- tolower(imdbtitles$primaryTitle)
Movie_Mondays$Title <- tolower(Movie_Mondays$Title)

#Special filters for bad IMDB matches -- Icarus and Coco
imdbtitles <- filter(imdbtitles,
                        #Coco
                        tconst != 'tt7002100' &
                        #Icarus
                        tconst != 'tt6687948'
                        )


# Left join data to movie ratings, based on title and year
joined <- Movie_Mondays %>% left_join(imdbfull, by = c("Title" = "primaryTitle", "Year" = "startYear"))

# Deauthorize googledrive
drive_deauth(clear_cache = TRUE, verbose = TRUE)