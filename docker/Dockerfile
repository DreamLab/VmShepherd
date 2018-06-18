FROM python:3.6-rc-slim
MAINTAINER PaaS Team of Dreamlab <paas@cloud.dreamlab.pl>

EXPOSE 8888

RUN useradd -d /home/shepherd -ms /bin/bash shepherd

VOLUME ["/home/shepherd"]
WORKDIR /home/shepherd

RUN pip install vmshepherd

USER shepherd

ENTRYPOINT ["/usr/local/bin/vmshepherd"]
