FROM thehale/python-poetry as base

RUN poetry --version

FROM base as main

RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential git sqlite3 \
  && apt-get purge -y --auto-remove \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app
RUN poetry install

FROM main as runtime

ENV PYTHONPATH=$PYTHONPATH:/app
COPY --from=main /app /app

COPY --from=main $POETRY_HOME $POETRY_HOME
RUN ./bin/bootstrap