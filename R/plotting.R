# General Plotting
library(ggplot2) 
library(stargazer)
setwd("~/Desktop/ThesisWork/thesis/graphs/")

fleet_size_list = c(5500, 5750, 6000, 6250, 6500, 6750, 7250, 7000, 7500, 7750,
                    8000, 8250, 8500, 8750, 9000, 9250, 9500, 9750, 10000, 10250,
                    10500, 10750, 11000, 11250, 11500, 11750, 12000, 12250, 12500, 12750,
                    15000, 15500, 16000, 16500, 17000, 17500, 18000, 18500, 19000, 19500,
                    20000, 22500, 25000, 27500, 30000, 32500, 35000, 37500, 40000, 42500
                    )
waiting = c(172.207, 172.072, 171.996, 171.85, 171.761, 171.642, 171.389, 171.519, 171.279, 171.166,
                 171.076, 170.981, 170.826, 170.762, 170.594, 170.526, 170.403, 170.319, 170.185, 170.091,
                 169.988, 169.868, 169.763, 169.648, 169.523, 169.421, 169.317, 169.218, 169.088, 168.981,
                 167.976, 167.755, 167.529, 167.29, 167.061, 166.768, 166.497, 166.203, 165.944, 165.703,
                 165.382, 163.984, 162.845, 161.82, 160.807, 159.797, 158.773, 157.652, 156.601, 155.512 
                 )
reposition_distance = c(1.2301149, 1.2102865, 1.1948250, 1.1754560, 1.1576281, 1.1410929, 1.1129074, 1.1262216, 1.0941527, 1.0786965,
                        1.0651019, 1.0489833, 1.0348172, 1.0208086, 1.0092171, 0.9964958, 0.9835983, 0.9718386, 0.9572424, 0.9477182,
                        0.9366021, 0.9235550, 0.9129838, 0.9011145, 0.8898222, 0.8806024, 0.8686077, 0.8614765, 0.8516318, 0.8438916,
                        0.7691293, 0.7534941, 0.7398915, 0.7232521, 0.7105015, 0.6961964, 0.6805079, 0.6677225, 0.6569110, 0.6445342,
                        0.632, 0.57, 0.506, 0.447, 0.395, 0.35, 0.312, 0.277, 0.25, 0.225
                        )
avo = c(1.491, 1.494, 1.497, 1.501, 1.504, 1.507, 1.512, 1.509, 1.516, 1.518,
        1.52, 1.523, 1.526, 1.529, 1.532, 1.533, 1.536, 1.538, 1.541, 1.542,
        1.544, 1.547, 1.548, 1.551, 1.552, 1.555, 1.557, 1.558, 1.56, 1.561,
        1.576, 1.579, 1.582, 1.585, 1.587, 1.591, 1.595, 1.598, 1.601, 1.603,
        1.607, 1.624, 1.639, 1.651, 1.66, 1.669, 1.676, 1.683, 1.687, 1.692
        )

# AVO analysis
x = fleet_size_list
m_avo<-nls(avo~a*x^b)
summary(m_avo)
cor(avo,predict(m_avo))
plot(x,avo)
lines(x,predict(m_avo),lty=2,col="red",lwd=3)

# waiting analysis
m_waiting <- lm(waiting~x)
summary(m_waiting)
cor(waiting, predict(m_waiting))
plot(x, waiting)
lines(x,predict(m_waiting),lty=2,col="red",lwd=3)

# REP analysis
m_rep <- nls(reposition_distance~a*x^(b))
summary(m_rep)
cor(reposition_distance, predict(m_rep))
plot(x, reposition_distance)
lines(x,predict(m_rep),lty=2,col="red",lwd=3)

# waiting
ggplot() +
  geom_point(aes(fleet_size_list, waiting)) +
  labs(
    title = "Per Occupant Waiting Time",
    x = "Fleet Size",
    y = "Time (Seconds)"
  ) +
  theme(plot.title = element_text(hjust = 0.5)) +
  geom_smooth(aes(fleet_size_list, predict(m_waiting)))

# AVO
ggplot() +
  geom_point(aes(fleet_size_list, avo)) +
  labs(
    title = "Average Vehicle Occupancy (AVO)",
    x = "Fleet Size",
    y = "AVO"
  ) +
  theme(plot.title = element_text(hjust = 0.5)) +
  geom_smooth(aes(fleet_size_list, predict(m_avo))) 


# Rep
ggplot() +
  geom_point(aes(fleet_size_list, reposition_distance)) +
  labs(
    title = "Average Repositioning Distance Per Trip Request",
    x = "Fleet Size",
    y = "Distance (pixel-units)"
  ) +
  theme(plot.title = element_text(hjust = 0.5)) +
  geom_smooth(aes(fleet_size_list, predict(m_rep)))

rm(list = ls())

roundB <- read.csv("../python/out/out-roundb.csv", header = FALSE)
names(roundB) <- c('N', 'fleet_size', 'vehicle_size', 'DD', 'FREQ_LEVRS', 'superpixel',
                   'MAX_CIRCUITY', 'MAX_STOPS', 'BETA_INITIAL', 'BETA_OBS', 'waiting', 
                    'reposition_distance', 'avo', 'avg_circuity')

# Round B Plots

## Waiting
ggplot(roundB) +
  geom_point(aes(y = waiting, x = fleet_size, col = factor(MAX_CIRCUITY), shape = factor(MAX_STOPS))) +
  facet_grid(DD ~ ., scales = "free_y") +
  labs(
    title = "Per Occupant Waiting Time",
    x = "Fleet Size",
    y = "Time (seconds)",
    col = "Max Circuity",
    shape = "Max Stops"
  ) +
  theme(plot.title = element_text(hjust = 0.5)) 

roundB_model_waiting60 <- glm(waiting~fleet_size + MAX_STOPS + MAX_CIRCUITY, data = subset(roundB, DD == 60))
summary(roundB_model_waiting60)
roundB_model_waiting300 <- glm(waiting~fleet_size + MAX_STOPS + MAX_CIRCUITY, data = subset(roundB, DD == 300))
summary(roundB_model_waiting300)


## Repositioning
ggplot(roundB) +
  geom_point(aes(y = reposition_distance, x = fleet_size, col = factor(DD))) +
  facet_grid(factor(MAX_STOPS) ~ factor(MAX_CIRCUITY)) +
  labs(
    title = "Average Repositioning Distance Per Trip Request",
    x = "Fleet Size",
    y = "Distance (pixel-units)",
    col = "DD"
  ) +
  theme(plot.title = element_text(hjust = 0.5)) 



roundB_model_rep <- glm(reposition_distance~fleet_size + MAX_STOPS + MAX_CIRCUITY + DD, data = roundB)
summary(roundB_model_rep)

## AVO
ggplot(roundB) +
  geom_point(aes(y = avo, x = fleet_size, col = factor(MAX_CIRCUITY), shape = factor(MAX_STOPS))) +
  facet_grid(. ~ DD) +
  labs(
    title = "Average Vehicle Occupancy (AVO)",
    x = "Fleet Size",
    y = "AVO",
    col = "Max Circuity",
    shape = "Max Stops"
  ) +
  theme(plot.title = element_text(hjust = 0.5)) 
  
roundB_model_avo <- glm(avo~fleet_size + MAX_STOPS + MAX_CIRCUITY + DD, data = roundB)
summary(roundB_model_avo)


stargazer(roundB_model_avo, roundB_model_waiting60, roundB_model_waiting300, roundB_model_rep)


# len log plots
library(ggplot2) 
date_map <- function(m) {
  d <- round(((m - 31449600) / 86400))
  return(paste("1-",d,"-16", sep = ""))
}
library(data.table)
setwd("~/Desktop/ThesisWork/thesis/python/log/")
word <- "lenlog409"
lenlog <- sapply(fread(paste(word,".out",sep=""))[,6], as.numeric) # uncomment for large dataread
l = length((lenlog))
lenlog1 = lenlog[1:floor(l/2)]
lenlog2 = lenlog[(floor(l/2)+1):l]
ds <- seq(31536000,length.out = length(lenlog))
ds1 <- ds[1:floor(l/2)]
ds2 = ds[(floor(l/2)+1):l]

v1 <- seq(31536000, by = 2*86400, length.out = 16)

ggplot() +
  geom_point(aes(x = ds, y = lenlog), col = "black") +
  scale_x_continuous(breaks=v1, labels = date_map(v1)) +
  labs(x = "Date", y = "Number of Undispatched Trip Requests",
       title = "Size of Trip Buffer for Fleet Size of 20,000") +
  theme(plot.title = element_text(hjust = 0.5)) 


## I need to get the whole month... should be done cooking by tmw night... 
## Ideally, this fleet size of 20k instead of 15k should not result in that
## huge spike at the end of the month.

## it would smarter to just run it on that one bad day...

## it's only about showing that (under a ton of modeling assumptions bc this problem is huge),
## that a fixed fleet size can be sustainable over a long period of time

## everything else is "future work"

ggplot() +
  geom_point(aes(x = ds1, y = lenlog1), col = "black") +
  scale_x_continuous(breaks=v1, labels = date_map(v1)) +
  labs(x = "Date", y = "Number of Undispatched Trip Requests",
       title = "Size of Trip Buffer for Fleet Size of 20,000") +
  theme(plot.title = element_text(hjust = 0.5)) 
ggplot() +
  geom_point(aes(x = ds2, y = lenlog2), col = "black") +
  scale_x_continuous(breaks=v1, labels = date_map(v1)) +
  labs(x = "Date", y = "Number of Undispatched Trip Requests",
       title = "Size of Trip Buffer for Fleet Size of 20,000") +
  theme(plot.title = element_text(hjust = 0.5)) 


#old values are 2075792, 2073600.0

# 32400000 is 1/11 at 12AM

# 2016-01-25 00:36:32
# # time of peak is 2101459
