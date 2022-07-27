FROM --platform=$BUILDPLATFORM python:3.8.9-alpine as base

WORKDIR /bot
COPY . .

RUN apk update && apk add gcc musl-dev  \
    && pip install -U setuptools wheel pip
RUN pip3 wheel -r requirements.txt --wheel-dir=/bot/wheels

FROM python:3.8.9-alpine

COPY --from=base /bot /bot
WORKDIR /bot

RUN pip3 install --no-index --find-links=/bot/wheels -r requirements.txt

ENTRYPOINT ["/bot/entrypoint.sh"]
