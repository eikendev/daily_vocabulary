FROM python:3-alpine AS base

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1

RUN set -xe \
	&& apk update \
	&& apk upgrade \
	&& apk del --progress --purge \
	&& rm -rf /var/cache/apk/*

FROM base AS dependencies

RUN set -xe \
    && pip install pipenv \
    && apk add --no-cache build-base gcc linux-headers libffi-dev openssl-dev python3-dev rust cargo

COPY Pipfile .
COPY Pipfile.lock .

RUN set -xe \
    && PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

FROM base AS runtime

COPY --from=dependencies /.venv /.venv

ENV PATH "/.venv/bin:$PATH"

RUN set -xe \
	&& addgroup -g 82 -S app \
	&& adduser -u 82 -D -g '' -G app app

WORKDIR /home/app

VOLUME /home/app/data

USER app

COPY . .

ENTRYPOINT ["python", "-m", "daily_vocabulary"]
