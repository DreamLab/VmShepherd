FROM python:3.6-rc-slim

ADD . /root/
# expose panel
EXPOSE 8888

WORKDIR /root
RUN python setup.py install

ENTRYPOINT ["vmshepherd"]

