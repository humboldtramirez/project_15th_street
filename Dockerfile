FROM python:3.8-slim

# Install permanent system dependencies
RUN apt-get update \
    && apt-get install -y \
        curl \
        gcc \
        g++ \
        git \
        libffi-dev \
        libssl-dev \
        build-essential \
        wget \
    # Fix numpy compilation related to gcc
    && ln -s /usr/include/locale.h /usr/include/xlocale.h \
    # Cleanup
    && apt clean && apt autoclean && apt-get clean && apt-get autoclean \
    # Install python dependencies
    && pip install --upgrade pip && pip install pipenv \
    # Setup environment
    && adduser --system --disabled-password --no-create-home python \
    # Install MariaDB Connector/C
    && wget https://dlm.mariadb.com/2862622/Connectors/c/connector-c-3.3.4/mariadb-connector-c-3.3.4-debian-buster-amd64.tar.gz -O - | tar -zxf - --strip-components=1 -C /usr

ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=pre
ENV APP_HOME=/microservice/
ENV DATABASE_DIR=database
ENV PYMS_CONFIGMAP_FILE="$APP_HOME"config-docker.yml

COPY Pipfile* /tmp/

# Install Project
RUN mkdir $APP_HOME \
    && chown -R python $APP_HOME \
    # Database file structure
    && mkdir $DATABASE_DIR \
    && chmod 777 $DATABASE_DIR \
    && cd /tmp \
    && pipenv requirements > requirements.txt \
    && pip install -r /tmp/requirements.txt \
    && pip install gevent==21.12.0 gunicorn==20.1.0
ADD . $APP_HOME

WORKDIR $APP_HOME
EXPOSE 5000
USER python

CMD ["gunicorn", "--workers", "8", "--log-level", "INFO", "--bind", "0.0.0.0:5000", "manage:app"]