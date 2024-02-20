FROM thehale/python-poetry as base

RUN poetry --version
RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential git sqlite3 \
  && apt-get purge -y --auto-remove \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app
RUN poetry install

FROM base as main

ENV PYTHONPATH "/app"
COPY --from=base /app /app
COPY --from=base $POETRY_HOME $POETRY_HOME

EXPOSE 3020
