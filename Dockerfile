FROM python:3.9 
RUN pip install poetry
RUN poetry init
RUN poetry install