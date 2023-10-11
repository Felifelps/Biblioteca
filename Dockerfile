
FROM python:3.9-slim

#Sets workdir to the app folder
WORKDIR /app

#Creates a new virtual environment
RUN python3 -m venv .venv

#Activates the venv
ENV PATH=".venv/bin:$PATH"

#Copy requirements file
COPY requirements.txt requirements.txt

#Updates pip
RUN pip install --upgrade pip

#Install dependences
RUN pip install --no-cache-dir -r requirements.txt

#Copy the rest of the project files
COPY . .

#Expose the server port
EXPOSE 8080

#Starts the server
CMD ["hypercorn", "app:app", "--bind", "0.0.0.0:8080"]