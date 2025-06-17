FROM hertzg/rtl_433:latest
WORKDIR /home/yats/
RUN apk add --update --no-cache python3
COPY temp_simplified.py .
COPY config.ini .
COPY temp.sh .
RUN chmod +x ./temp.sh
ENTRYPOINT ["./temp.sh"]