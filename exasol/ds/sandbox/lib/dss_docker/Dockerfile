FROM ubuntu:20.04
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install --no-install-recommends --assume-yes python3 python3-pexpect
EXPOSE 8888/tcp
VOLUME /root/notebooks
