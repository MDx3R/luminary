FROM python:3.11-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

COPY configs ./configs
COPY src ./src
COPY cli ./cli

CMD ["poetry", "run", "uvicorn", "cli.app.main:app", "--uds", "/run/luminary/app.sock"]
