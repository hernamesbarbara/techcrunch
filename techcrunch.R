library(RCurl)
library(reshape2)

f <- "http://skdatapoller.googlecode.com/svn-history/r4/trunk/DataAPIPoller/test_data/TechCrunch.csv"
df <- read.csv(url(f))
df$fundedDate <- parse_date(df$fundedDate, format="%d-%b-%y")
head(df)

companies <- df[, c(2,8, 10)]
companies <- ddply(companies, .(company, round), summarise,
                   total=sum(raisedAmt))

avgs <- ddply(df, .(company), summarise,
      avg=mean(raisedAmt))

companies <- merge(companies, avgs)[, c(1,2,4,3)]
companies <- arrange(companies, desc(total))

top <- head(companies, 25)
top$round <- as.factor(top$round)
ggplot(top, aes(x=reorder(company, desc(total)), weight=total, fill=round)) +
  geom_bar() +
  xlab('Company') +
  ylab('Total Raised') +
  scale_y_continuous(labels=dollar)


min(df$fundedDate)
subset(df, company=='On Deck')
library(stringr)
df[!is.na(str_match(df$company, "Face")), ]
