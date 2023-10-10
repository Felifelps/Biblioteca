
FROM python:3.9-slim

# Copy requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN python -m venv .venv
RUN .venv/Scripts/Activate.ps1
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files
COPY . .

# Expose the server port
EXPOSE 8080

# Command to start the server
CMD ["hypercorn", "--bind", "0.0.0.0:8080", "app:app"]