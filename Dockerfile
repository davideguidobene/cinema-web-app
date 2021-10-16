FROM alpine

RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev

RUN apk add --no-cache \
    python3-dev \
    py3-pip \
    postgresql-dev

COPY ./requirements/requirements.txt /usr/requirements/requirements.txt

RUN pip3 install --no-cache-dir -r /usr/requirements/requirements.txt
RUN pip3 install --no-cache-dir psycopg2

RUN apk del --no-cache .build-deps

# EXPOSE 5000

CMD ["/usr/src/cinema-web-app/scripts/entrypoint.sh"]
