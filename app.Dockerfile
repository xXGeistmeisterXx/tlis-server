FROM python:rc-alpine3.13

WORKDIR /app

RUN apk add --no-cache mariadb-connector-c-dev ;\
    apk add --no-cache --virtual .build-deps \
        build-base \
        mariadb-dev ;\
    pip install mysqlclient;\
    apk del .build-deps

RUN apk add build-base

COPY ./app/requirements.txt /app/requirements.txt

RUN python -m pip install -r requirements.txt

COPY ./app /app
