FROM python:3.10-alpine

ENV PYTHONUNBUFFERED 1

RUN dnf update -y && \
    dnf install -y git which && \
    dnf clean all && rm -rf /var/cache/yum

WORKDIR /opt/app

ENV POETRY_VIRTUALENVS_CREATE=0

RUN pip3 install poetry==1.1.12

ADD poetry.lock .
ADD pyproject.toml .
RUN poetry install --no-dev --no-root

ARG APP_BUILD_TESTS
RUN if [ -n "${APP_BUILD_TESTS}" ]; then poetry install --no-root; fi

ADD ./act .

ARG VERSION
RUN if [ -z "${VERSION}" ]; then echo "VERSION is empty!!!"; exit 1; fi
RUN echo "${VERSION}" > ./VERSION