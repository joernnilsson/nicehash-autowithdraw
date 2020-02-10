#Download base image ubuntu 16.04
FROM debian:stretch-slim

RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-requests 

COPY nicehash_auto_withdraw.py /nicehash_auto_withdraw.py
COPY nicehash.py /nicehash.py

CMD ["/usr/bin/python3", "/nicehash_auto_withdraw.py"]
