FROM python:3.9-slim-bullseye AS compile-image
LABEL maintainer="Wazo Maintainers <dev@wazo.io>"

RUN python -m venv /opt/venv
# Activate virtual env
ENV PATH="/opt/venv/bin:$PATH"

RUN apt-get -q update
RUN apt-get -yq install gcc make

COPY . /usr/src/wazo-example/
WORKDIR /usr/src/wazo-example/backend
RUN pip install -r requirements.txt
RUN python setup.py install

FROM python:3.9-slim-bullseye AS build-image
COPY --from=compile-image /opt/venv /opt/venv

COPY ./backend/config /etc/wazo-example
RUN mkdir /data
COPY manifest* /data
COPY wda /data/wda
COPY portal /data/portal

EXPOSE 8888

# Activate virtual env
ENV PATH="/opt/venv/bin:$PATH"
CMD ["wazo-example"]
