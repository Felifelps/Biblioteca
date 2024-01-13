FROM python:3.9-slim

RUN python -m pip install --upgrade pip

RUN python -m pip install poetry hypercorn

RUN poetry config virtualenvs.create false && poetry install --only main

#Expose the server port
EXPOSE 8080

#Starts the server
CMD ["hypercorn", "app:app", "--bind", "0.0.0.0:8080"]