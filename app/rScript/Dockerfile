FROM trestletech/plumber
RUN Rscript -e "install.packages('devtools')"
WORKDIR /app/
COPY import_data.r /app/
CMD ["/app/import_data.r"]