FROM --platform=amd64 python:3.8.13-slim-bullseye

WORKDIR /app 

COPY . .  

RUN apt-get update
RUN apt-get -y install python3-dev libgtk-3-dev poppler-utils
RUN cd pips && python3 -m pip install ./*.whl
RUN python3 -m pip install -r ./requirements.txt
RUN python3 -m pip install flit
RUN cd ./WeasyPrint && python3 -m pip install . 
RUN cd ./genalog && python3 -m pip install . 

ENTRYPOINT [ "/bin/bash" ]