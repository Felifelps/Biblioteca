FROM python:3.9 as requirements-stage
WORKDIR /tmp
RUN pip install poetry
RUN poetry init
RUN poetry install