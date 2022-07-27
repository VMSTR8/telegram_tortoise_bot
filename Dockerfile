FROM --platform=$BUILDPLATFORM python:3.8.9-alpine as base

WORKDIR /bot
COPY . .

RUN apk update && apk add gcc musl-dev && pip install wheel
RUN if [[ "$BUILDPLATFORM" == "linux/amd64" ]]; then pip3 wheel -r requirements.txt --wheel-dir=/bot/wheels; else \
    rm /usr/bin/lsb_release && pip3 wheel -r requirements.txt --wheel-dir=/bot/wheels; fi

FROM python:3.8.9-alpine

COPY --from=base /bot /bot
WORKDIR /bot

RUN pip3 install --no-index --find-links=/bot/wheels -r requirements.txt

ENTRYPOINT ["/bot/entrypoint.sh"]
