FROM python:3-slim as base

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1

FROM base AS dependencies

RUN set -xe \
    && pip install pipenv \
    && apt-get update \
    && apt-get install -y --no-install-recommends gcc

COPY Pipfile .
COPY Pipfile.lock .

RUN set -xe \
    && PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

FROM base AS runtime

COPY --from=dependencies /.venv /.venv

ENV PATH "/.venv/bin:$PATH"

RUN set -xe \
	&& groupadd --gid 2000 --system app \
	&& adduser -uid 2000 --gecos '' --disabled-password --gid 2000 app \
	&& apt-get update \
	&& apt-get upgrade -y \
    && apt-get purge -y --auto-remove \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /home/app

VOLUME /home/app/data

USER app

COPY . .

ENTRYPOINT ["python", "-m", "daily_vocabulary"]
