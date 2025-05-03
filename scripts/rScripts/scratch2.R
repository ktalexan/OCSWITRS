#from the victims data frame, create a histogram of the median victim age

 ggplot(victims[victims$victim_age < 100,], aes(x = victim_age)) +
 geom_histogram(binwidth = 5) +
 labs(
     x = "Victim Age",
     y = "Count",
     title = paste("Histogram of Victim Age (n=",nrow(victims),")"
     )
 )


temp1 <- data.frame(table(age = victims[victims$victim_age < 100, ]$victim_age, as_factor(victims[victims$victim_age < 100,]$victim_degree_of_injury)))

colnames(temp1) <- c("age", "injury", "Freq")

# create a histogram of the median victim age
ggplot(temp1, aes(x = age, y = Freq, fill = injury)) +
geom_bar(stat = "identity") +
labs(
    x = "Victim Age",
    y = "Count",
    title = paste("Histogram of Victim Age by Injury (n=",nrow(victims),")"
    )
)

# from the victims data frame, select victim_age, victim_degree_of_injury, if victim_age < 100, or victim_age is not NA, or victim_degree_of_injury is not NA and create a new data frame
temp2 <- victims %>%
    filter(victim_age < 100 | !is.na(victim_age) | !is.na(victim_degree_of_injury)) %>%
    select(victim_age, victim_degree_of_injury)

# generate age group bins for the age_group variable in the temp2 data frame
temp2$age_group <- cut(temp2$victim_age, breaks = c(0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100), labels = c("0-10", "11-20", "21-30", "31-40", "41-50", "51-60", "61-70", "71-80", "81-90", "91-100"))

# Remove NA values from the age_group variable in the temp2 data frame
temp2 <- temp2[!is.na(temp2$age_group),]

# create a histogram of the median victim age by injury
ggplot(temp2, aes(x = age_group, fill = as_factor(victim_degree_of_injury))) +
geom_bar() +
labs(
    x = "Victim Age Group",
    y = "Count",
    title = paste("Histogram of Victim Age Group by Injury (n=",nrow(temp2),")"
    )
)

# create a histogram of the median victim age group by injury
ggplot(temp2, aes(x = victim_degree_of_injury, fill = age_group)) +
geom_bar() +
labs(
    x = "Injury",
    y = "Count",
    title = paste("Histogram of Victim Injury by Age Group (n=",nrow(temp2),")"
    )
)

# create a heatmap of with x the age_group, y the victim_degree_of_injury, and fill the median victim_age
ggplot(temp2, aes(x = age_group, y = as_factor(victim_degree_of_injury), fill = victim_age)) +
geom_tile() +
labs(
    x = "Victim Age Group",
    y = "Injury",
    fill = "Median Victim Age",
    title = paste("Heatmap of Victim Age Group by Injury (n=",nrow(temp2),")"
    )
)


# from the crashes data frame, use the point_x and point_y columns to create a map
ggplot(crashes, aes(x = point_x, y = point_y)) +
geom_point() +
labs(
    x = "Longitude",
    y = "Latitude",
    title = paste("Map of Crashes (n=",nrow(crashes),")"
    )
)

library(sf)

# obtain the bounding coordinates of orange county, california
oc_bounds <- st_bbox(st_union(crashes$geometry))

mydat <- runif(50)
day1 <- as.POSIXct("2012-07-13", tz = "UTC")
day2 <- day1 + 49*3600*24
pdays <- seq(day1, day2, by = "days")
lo <- loess(mydat ~ as.numeric(pdays))

# And then if you want to plot the result:
plot(pdays,mydat)
lines(pdays, lo$fitted)


lo1 <- loess(ts_year$sum_number_killed ~ as.numeric(ts_year$dt_year))
plot(ts_year$dt_year, ts_year$sum_number_killed)
lines(ts_year$dt_year, lo1$fitted)


lo2 <- loess(ts_week$sum_number_killed ~ as.numeric(ts_week$dt_year))
plot(ts_week$dt_year, ts_week$sum_number_killed)
lines(ts_week$dt_year, lo2$fitted)

lo3 <- loess(ts_month$sum_number_killed ~ as.numeric(ts_month$dt_year))
plot(ts_month$dt_year, ts_month$sum_number_killed)
lines(ts_month$dt_year, lo3$fitted)


lo10 <- loess(sum_number_killed ~ dt_year, data = ts_month)
plot(ts_month$dt_year, ts_month$sum_number_killed)
lines(ts_month$dt_year, lo10$fitted)

lo1 <- loess(sum_number_killed ~ dt_year, data = ts_week)
plot(ts_week$dt_year, ts_week$sum_number_killed)
lines(ts_week$dt_year, lo1$fitted)

lo2 <- loess(sum_number_killed ~ index, data = ts_week)

test <- ts_week
test$index <- 1:nrow(test)

lo1 <- loess(mean_number_killed ~ index, data = data.frame(index=1:nrow(ts_week), ts_week))

lo1 <- loess(mean_number_killed ~ index, data = test)


lo1 <- loess(mean_number_killed ~ rownames(ts_week), data = ts_week)

plot(test$index, test$mean_number_killed)
lines(test$index, lo1$fitted)

# get the 95 condidence intervals of lo1$fitted
lo1_ci <- predict(lo1, interval = "confidence")

data = data.frame(test, lo=lo1$fitted, lol = lo1$fitted + lo1_ci, lou = lo1$fitted - lo1_ci)

# plot the lo1 line with their confidence intervals
plot(data$index, data$mean_number_killed)
lines(data$index, data$lo, col = "red")
lines(data$index, data$lo, col = "blue")
lines(data$index, data$lou, col = "green")

plx<-predict(loess(mean_number_killed ~ index, data = test), se=T)

plx<-predict(lo1, se=T)


lo <- loess(mean_number_killed ~ rownames(ts_month), data = ts_month)
lop <- predict(lo, se = T)
locil <- lop$fit - qt(0.975, lop$df) * lop$se
lociu <- lop$fit + qt(0.975, lop$df) * lop$se


data = data.frame(
    index = 1:nrow(ts_month),
    dt_year = ts_month$dt_year,
    dt_month = ts_month$dt_month,
    mean_number_killed = ts_month$mean_number_killed,
    loess = lo$fitted,
    loess_lower95 = locil,
    loess_upper95 = lociu
)

p1 <- ggplot(data, aes(x = index, y = mean_number_killed)) +
geom_line() +
geom_line(aes(y = loess), color = "darkred", linewidth = 2) +
    geom_smooth(method="loess")


p1

p2 <- ggplot(data, aes(x = index, y = mean_number_killed)) +
    geom_line() +
    geom_smooth(method = "loess", se = TRUE, fill = "red", alpha = 0.2) +
    geom_smooth(method = "loess", se = FALSE, color = "darkred")

p2

p + 
    geom_smooth(data = filter(mydata1, method == "loess"), method = "loess", se = FALSE) +
    geom_smooth(data = filter(mydata1, method == "lm"), method = "lm", se = FALSE)



setwd(prj_dirs$codebook_path)
cb.json <- toJSON(cb, pretty = TRUE, auto_unbox = TRUE)
write(cb.json, file = "cb.json")


92340387
92340620

# find the row in crashes where the crash_id is 92340387
test<- crashes[crashes$case_id == 92340387 | crashes$case_id == 92340620,]

test$coll_time_temp <- lapply(test$coll_time, format_coll_time)

format(as.Date(test$process_date), "%Y-%m-%d %H:%M")
format(as.POSIXct(paste(crashes$coll_date, crashes$coll_time_temp), format = "%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M")

format(as.POSIXct(paste(test$coll_date, test$coll_time_temp), format = "%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M")
test$coll_date
test$coll_time_temp
paste(test$coll_date, test$coll_time_temp)
 
