# taxi data summaries
library(data.table)

# Data read
# setwd("~/Documents/Princeton/Senior Year/Thesis/Sandbox")
setwd("~/Desktop/ThesisWork/thesis/csv/raw/")

# Make one-weekish sample
rawdata <- fread("yellow_tripdata_2016-01.csv") # uncomment for large dataread
setorder(rawdata, "tpep_pickup_datetime")
# fwrite(rawdata, "yellow_tripdata_2016-01.csv") # whole month


# one_week <- subset(
#                     rawdata,
#                     (
#                       tpep_pickup_datetime %like% "2016-01-24" & tpep_dropoff_datetime %like% "2016-01-25"
#                     )
#                     | tpep_pickup_datetime %like% "2016-01-25"
#                     | tpep_pickup_datetime %like% "2016-01-26"
#                     | tpep_pickup_datetime %like% "2016-01-27"
#                     | tpep_pickup_datetime %like% "2016-01-28"
#                     | tpep_pickup_datetime %like% "2016-01-29"
# 
#                   )
# 
# fwrite(one_week, "yellow_tripdata_2016-01-week.csv")




two_week <- subset(
  rawdata,
  (
    tpep_pickup_datetime %like% "2016-01-10" & tpep_dropoff_datetime %like% "2016-01-11"
  )
  | tpep_pickup_datetime %like% "2016-01-11"
  | tpep_pickup_datetime %like% "2016-01-12"
  | tpep_pickup_datetime %like% "2016-01-13"
  | tpep_pickup_datetime %like% "2016-01-14"
  | tpep_pickup_datetime %like% "2016-01-15"
  | tpep_pickup_datetime %like% "2016-01-16"
  | tpep_pickup_datetime %like% "2016-01-17"
  | tpep_pickup_datetime %like% "2016-01-18"
  | tpep_pickup_datetime %like% "2016-01-19"
  | tpep_pickup_datetime %like% "2016-01-20"
  | tpep_pickup_datetime %like% "2016-01-21"
  | tpep_pickup_datetime %like% "2016-01-22"
  | tpep_pickup_datetime %like% "2016-01-23"
  | tpep_pickup_datetime %like% "2016-01-24"
)

fwrite(two_week, "yellow_tripdata_2016-01-twoweek.csv")

# one_week_cleaned <- fread("../cleaned/yellow_tripdata_2016-01-twoweek_cleaned.csv")
# one_week_cleaned <- one_week_cleaned[order(oSec)]


jan13 = subset(rawdata, tpep_pickup_datetime %like% "2016-01-13")
fwrite(jan13, "yellow_tripdata_2016-01-13.csv")

jan13cont = subset(rawdata,   (
  tpep_pickup_datetime %like% "2016-01-12" & tpep_dropoff_datetime %like% "2016-01-13"
)
| tpep_pickup_datetime %like% "2016-01-13"
)
fwrite(jan13cont, "yellow_tripdata_2016-01-13-cont.csv")




# clean_week <- fread("../cleaned/yellow_tripdata_2016-01-week_cleaned.csv")
#1036800
# clean_week$dSec <- clean_week$dSec - 1036800
# clean_week$oSec <- clean_week$oSec - 1036800



# thin <- subset(rawdata, TRUE, select = c(tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude, trip_distance))
# fwrite(thin, "yellow_tripdata_2016-01_thin.csv")

# 
# # Cleans up data
# valid_locations <- function (data) {
#   d <- subset(data, pickup_latitude != 0.00000) # eliminates broken locations
#   d <- subset(d, pickup_longitude < -73.90 & pickup_longitude > -74.03) # eliminates outlier locations
#   d <- subset(d, pickup_latitude < 40.92 & pickup_latitude > 40.68) # eliminates outlier locations
#   d <- head(d, 100000) # only on a certain day
#   return(d)
# }
# 
# # Map a geographical coordinate to a pixel
# map_to_pixel <- function(x, shift) {
#   scalar <- 2000
#   y <- (x + shift)*scalar
#   return(floor(y))
# }
# 
# gen_pixel_loc_data <- function(data) {
#   data$pickup_y <- sapply(data$pickup_latitude, map_to_pixel, shift = -1*min(data$pickup_latitude))
#   data$pickup_x <- sapply(data$pickup_longitude, map_to_pixel, shift = -1*min(data$pickup_longitude))
#   return(subset(data, TRUE, c(pickup_x, pickup_y)))
# }
# 
# # data_big <- valid_locations(rawdata) # uncomment for large subset op
# data <- head(data_big, 10000)
# 
# plot(data$pickup_longitude, data$pickup_latitude, 
#      xlab = "Longitude", ylab = "Latitude", 
#      main = "NYC Pickup Locations",
#      pch = 16, col = "darkgreen")
# 
# pickup_data <- gen_pixel_loc_data(data)
# 
# # plot(pickup_data$pickup_y)
# # plot(pickup_data$pickup_x)
# 
# pixel_plot <- function(data) {
#   p <- plot(data$pickup_x, data$pickup_y, 
#        xlab = "xPixel : Longitude Mapping", ylab = "yPixel : Latitude Mapping", 
#        main = "NYC Pickup Locations",
#        pch = 16, col = "darkgreen")
#   return(p)
# }
# 
# pixel_plot(pickup_data)
# 
# freq <- as.data.frame(table(pickup_data))
# 
# 




# one_day <- subset(rawdata, tpep_pickup_datetime %like% "2016-01-01")
# 
# pickup_time <- one_day[,c(tpep_pickup_datetime), lapply(.SD, function(x) x)]
# 
# 
# dt.out = dt[, list(v1 = sum(v1),  lapply(.SD,mean)), by = grp, .SDcols = sd.cols]
# 
# tail(one_day)
# as.numeric(as.duration(ymd_hms("2016-01-01 00:00:00") - now()))
# 
# 
# df$date2 = mdy(df$Date)
# df$time2 = hms(df$Time)
# df$date_time = paste(df$date2, df$time2, sep = " ")
# df$date_time = ymd_hms(df$date_time)
# df$start_time = ymd_hms("2016-01-09 15:23:26", tz="UTC")
# df$clock = as.duration(df$date_time - df$start_time)