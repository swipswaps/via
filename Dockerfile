FROM python:2.7
MAINTAINER Hypothes.is Project and Ilya Kreymer

# install Node
# (adapted from https://github.com/nodejs/docker-node/blob/master/5.1/Dockerfile)
ENV NODE_VERSION v5.1.0
ENV NODE_PACKAGE node-$NODE_VERSION-linux-x64.tar.gz
RUN curl -SLO https://nodejs.org/dist/$NODE_VERSION/$NODE_PACKAGE
RUN tar -xzf $NODE_PACKAGE -C /usr/local --strip-components=1
RUN rm -rf $NODE_PACKAGE

# build client JS
COPY via-client /src/via-client/
WORKDIR /src/via-client
RUN npm install
RUN ./node_modules/.bin/webpack

# install Via
WORKDIR /src/
ADD requirements.txt /src/
RUN pip install -r requirements.txt
COPY . /src/

EXPOSE 9080

CMD ./run-uwsgi.sh
