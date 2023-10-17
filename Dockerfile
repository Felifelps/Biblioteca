
FROM python:3.9-slim

#Sets workdir to the app folder
WORKDIR /app

#Creates a new virtual environment
RUN python3 -m venv .venv

#Activates the venv
ENV PATH=".venv/bin:$PATH"

#Updates pip
RUN pip install --upgrade pip

#Install poetry
RUN pip install --no-cache-dir poetry

#Copy the rest of the project files
COPY . .

#Install poetry project
RUN poetry install

#Sets python version to 3.9
RUN poetry env use 3.9

#Opens poetry shell
RUN poetry shell

#Goes to apibiblioteca directory
WORKDIR /app/apibiblioteca

#Expose the server port
EXPOSE 8080

#Starts the server
CMD ["hypercorn", "app:app", "--bind", "0.0.0.0:8080"]