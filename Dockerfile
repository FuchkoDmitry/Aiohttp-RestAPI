FROM python:3.9-alpine3.14

WORKDIR /code

COPY requirements.txt requirements.txt

RUN apk add --no-cache --virtual .build-deps g++ gcc make libc-dev libffi-dev libevent-dev musl-dev \
    openssl-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps g++ gcc make libc-dev libffi-dev libevent-dev musl-dev openssl-dev

COPY app/ .

EXPOSE 8080

CMD ["python", "./main.py"]
