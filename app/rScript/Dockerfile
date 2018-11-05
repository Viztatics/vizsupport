FROM trestletech/plumber
RUN Rscript -e "install.packages('devtools')"
RUN Rscript -e "devtools::install_github('r-lib/xml2')"
RUN Rscript -e "install.packages('aws.s3', repos = c('cloudyr' = 'http://cloudyr.github.io/drat'))"
RUN Rscript -e "install.packages('RPostgreSQL')"
WORKDIR /app/
COPY import_data.r /app/
CMD ["/app/import_data.r"]