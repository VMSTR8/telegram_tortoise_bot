FROM python:3.8.9-alpine as base

WORKDIR /bot
COPY ../.. .

RUN apk update && apk add gcc musl-dev
RUN pip install wheel && pip wheel -r requirements.txt --wheel-dir=/bot/wheels

FROM python:3.8.9-alpine

COPY --from=base /bot /bot
WORKDIR /bot
RUN pip install --no-index --find-links=/bot/wheels -r requirements.txt

RUN aerich init -t database.config.TORTOISE_ORM && aerich init-db

CMD ["python3", "main.py"]
