FROM --platform=amd64 python:3.8.13-slim-bullseye

WORKDIR /app 

COPY . .  

RUN apt-get update
RUN apt-get -y install python3-dev libgtk-3-dev poppler-utils
# Try to install some of the large python package files from local directory
RUN if [ -d ./pips ] ; then cd pips && python3 -m pip install ./*.whl ; fi
RUN python3 -m pip install -r ./requirements.txt
RUN python3 -m pip install flit
RUN cd ./WeasyPrint && python3 -m pip install . 
RUN cd ./genalog && python3 -m pip install . 

# TODO: Change entry point
ENTRYPOINT [ "/bin/bash" ]