#Download base image ubuntu 16.04
FROM debian:jessie-slim

RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-requests

COPY auto-withdraw.py /auto-withdraw.py
COPY nicehash_site_api.py /nicehash_site_api.py

VOLUME ["/data"]

CMD ["/usr/bin/python3", "/auto-withdraw.py"]
