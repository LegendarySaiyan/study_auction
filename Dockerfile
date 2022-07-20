FROM python:3.10-alpine

ENV PYTHONUNBUFFERED 1

WORKDIR /opt/app

ENV POETRY_VIRTUALENVS_CREATE=0

RUN pip3 install poetry==1.1.12

ADD poetry.lock .
ADD pyproject.toml .
RUN apk add build-base
RUN pip3 install uvloop && \
    pip3 install uvicorn && \
    pip3 install Pillow && \
    pip3 install psycopg2-binary==2.9.3
RUN poetry install --no-dev --no-root

ARG APP_BUILD_TESTS
RUN if [ -n "${APP_BUILD_TESTS}" ]; then poetry install --no-root; fi

ADD ./act .