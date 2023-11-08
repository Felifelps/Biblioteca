FROM ubuntu:22.4

RUN apt-get update && \
    apt-get install -y python3.9 && \
    apt-get clean

#Sets workdir to the app folder
WORKDIR /app

RUN python -m pip install --upgrade pip

RUN python -m pip install poetry hypercorn mega.py

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && poetry install --only main

COPY . .

#Expose the server port
EXPOSE 8080

#Starts the server
CMD ["hypercorn", "app:app", "--bind", "0.0.0.0:8080"]