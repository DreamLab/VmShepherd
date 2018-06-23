#! /bin/bash

# building a image
docker build -t vmshepherd .

# starting a container with a sample image

docker run -v $(realpath ../)/:/home/shepherd -p 8888:8888 -it vmshepherd -c config/settings.example.yaml
