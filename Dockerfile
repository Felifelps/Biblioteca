FROM python:3.9-slim

#Sets workdir to the app folder
WORKDIR /app

RUN python -m pip install --upgrade pip

RUN python -m pip install poetry hypercorn

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && poetry install --only main

COPY . .

#Expose the server port
EXPOSE 8080

#Starts the server
CMD ["hypercorn", "app:app", "--bind", "0.0.0.0:8080", "--workers", "1"]