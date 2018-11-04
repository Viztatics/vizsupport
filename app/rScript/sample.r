#install.packages("aws.s3")
library("aws.s3")


bucketlist()
save_object("Funding/M/201801~201806/s3.xlsx", file = "~/s3.xlsx", bucket = "3rdcompany")

#install.packages("RPostgreSQL")
library('RPostgreSQL')
pg = dbDriver("PostgreSQL")

# Local Postgres.app database; no password by default
# Of course, you fill in your own database information here.
con = dbConnect(pg, user="viz", password="XXXXXXXX",
                host="vizdatabase.cyj6c45gkflw.us-east-1.rds.amazonaws.com", port=5432, dbname="vizdatabase")
df_postgres <- dbGetQuery(con, "SELECT * from viz_rules")
df_postgres
rule_data <- data.frame(
  created_on = as.Date(c("2012-01-01","2013-09-23","2014-11-15","2014-05-11",
                         "2015-03-27")),
  changed_on = as.Date(c("2012-01-01","2013-09-23","2014-11-15","2014-05-11",
                         "2015-03-27")),
  rule = c("Rick","Dan","Michelle","Ryan","Gary"),
  file = c("file Rick","file Dan","file Michelle","file Ryan","file Gary"),
  created_by_fk = c(1,2,3,4,5),
  changed_by_fk = c(1,2,3,4,5),
  stringsAsFactors = FALSE
)
dbWriteTable(con, "viz_rules", 
             value = rule_data, append = TRUE, row.names = FALSE)
df_postgres <- dbGetQuery(con, "SELECT * from viz_rules")
df_postgres
txt <- paste("UPDATE viz_rules SET changed_by_fk=1 where id=7")
dbGetQuery(con, txt)
df_postgres <- dbGetQuery(con, "SELECT * from viz_rules")
df_postgres
sql <- "DELETE from viz_rules where id=7"
dbGetQuery(con, sql)
df_postgres <- dbGetQuery(con, "SELECT * from viz_rules")
df_postgres
dbDisconnect(con)
dbUnloadDriver(pg)