#* Echo back the input,for testing the service is ready or not
#* @param msg The message to echo
#* @get /echo
function(msg=""){
  list(msg = paste0("The message is: '", msg, "'"))
}

#* @get /s3test
function(){
  library("aws.s3")
  bucketlist()
  save_object("Funding/M/201801~201806/s3.xlsx", file = "~/s3.xlsx", bucket = "3rdcompany")
}

#* @get /psqltest
function(){
  library("RPostgreSQL")
  drv <- dbDriver("PostgreSQL")
	# creates a connection to the postgres database
	# note that "con" will be used later in each connection to the database
  con <- dbConnect(drv, dbname = "vizdatabase",
	                 host = "ec2-18-234-58-200.compute-1.amazonaws.com", port = 5432,
	                 user = "viz", password = "VizPostgres4rrr")
  df_postgres <- dbGetQuery(con, "SELECT * from viz_rules")
  df_postgres
}