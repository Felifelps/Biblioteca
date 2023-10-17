
FROM python:3.9-slim

#Sets workdir to the app folder
WORKDIR /app

#Creates a new virtual environment
RUN apt-get update && apt-get install -y curl python3-dev

RUN curl -sSL https://install.python-poetry.org | python3 -

#Copy the rest of the project files
COPY . .

#Install poetry project
RUN poetry install

#Sets python version to 3.9
RUN poetry env use 3.9

#Opens poetry shell
RUN poetry run pip install hypercorn

WORKDIR apibiblioteca

#Expose the server port
EXPOSE 8080

#Starts the server
CMD ["poetry", "run", "hypercorn", "app:app", "--bind", "0.0.0.0:8080"]