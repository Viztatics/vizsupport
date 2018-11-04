FROM trestletech/plumber
RUN Rscript -e "install.packages('devtools')"
WORKDIR /app/
COPY rmongo.r /app/
CMD ["/app/import_data.r"]