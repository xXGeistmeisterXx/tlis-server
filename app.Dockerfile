FROM python:rc-alpine3.13

WORKDIR /app

RUN apk add --no-cache mariadb-connector-c-dev ;\
    apk add --no-cache --virtual .build-deps \
        build-base \
        mariadb-dev ;\
    pip install mysqlclient;\
    apk del .build-deps

		RUN apk add --no-cache \
		        libressl-dev \
		        musl-dev \
		        libffi-dev && \
		    pip install --no-cache-dir cryptography==2.1.4 && \
		    apk del \
		        libressl-dev \
		        musl-dev \
		        libffi-dev

RUN apk add build-base

COPY ./app/requirements.txt /app/requirements.txt

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

RUN python -m pip install -r requirements.txt

COPY ./app /app
