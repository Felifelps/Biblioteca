
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

#Expose the server port
EXPOSE 8080

#Starts the server
CMD ["poetry", "run", "hypercorn", "app:app", "--bind", "0.0.0.0:8080"]