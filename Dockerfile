# BUILDER Stage
#
# pull base image
FROM python:3.8.3-alpine as builder
LABEL stage=builder

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

# install dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip
COPY ./requirements.txt .
# RUN pip install -r requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

# FINAL Stage
#
# pull base image
FROM python:3.8.3-alpine

# create app user
RUN mkdir -p /home/app
RUN addgroup -S app && adduser -S app -G app

# app directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# dependencies
RUN apk update && apk add libpq
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

# copy project files & fix permissions
COPY ./entrypoint.sh $APP_HOME
COPY . $APP_HOME

RUN chown -R app:app $APP_HOME 

# change user and run
USER app
ENTRYPOINT [ "/home/app/web/entrypoint.sh" ]