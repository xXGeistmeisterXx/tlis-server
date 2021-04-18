FROM mariadb:10.5.9-focal

COPY ./db/ /docker-entrypoint-initdb.d/
