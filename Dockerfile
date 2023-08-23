FROM python:3.9 
RUN pip install poetry
WORKDIR /
COPY poetry.lock pyproject.toml /
RUN poetry install