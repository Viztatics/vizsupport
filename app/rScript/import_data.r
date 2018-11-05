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