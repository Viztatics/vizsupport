FROM trestletech/plumber

ARG AWS_ACCESS_KEY
ENV AWS_ACCESS_KEY=$AWS_ACCESS_KEY

ARG AWS_SECRET_ACCESS_KEY
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY

RUN apt install libcurl4-openssl-dev -y --no-install-recommends
RUN apt install build-essential libcurl4-gnutls-dev libxml2-dev libssl-dev -y --no-install-recommends
RUN apt-get update
RUN apt-get install libpq-dev -y --no-install-recommends
RUN Rscript -e "install.packages('devtools')"
RUN Rscript -e "devtools::install_github('r-lib/xml2')"
RUN Rscript -e "install.packages('aws.s3', repos = c('cloudyr' = 'http://cloudyr.github.io/drat'))"
RUN Rscript -e "install.packages('RPostgreSQL')"
WORKDIR /app/
COPY import_data.r /app/
CMD ["/app/import_data.r"]