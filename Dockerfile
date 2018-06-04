FROM python:3.6-rc-slim

RUN apt-get -y update; apt-get -qq -y install make sudo
RUN pip install tox

ADD . /root/
# expose panel
EXPOSE 8888
# expose doc
EXPOSE 8000

WORKDIR /root
RUN  make install

ENTRYPOINT ["make"]

