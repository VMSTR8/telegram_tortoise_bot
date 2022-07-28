FROM --platform=$BUILDPLATFORM python:3.8.8-alpine as base

WORKDIR /bot
COPY . .

RUN apk update && apk add gcc musl-dev python3-dev \
    && pip install -U setuptools wheel pip
RUN pip wheel -r requirements.txt --wheel-dir=/bot/wheels

FROM --platform=$BUILDPLATFORM python:3.8.8-alpine

COPY --from=base /bot /bot
WORKDIR /bot

RUN pip install --no-index --find-links=/bot/wheels -r requirements.txt

ENTRYPOINT ["/bot/entrypoint.sh"]
