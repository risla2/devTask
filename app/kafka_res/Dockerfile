#Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app, The COPY . /app command copies the local directory into the container's /app directory.
COPY . /app/

# Copy the config file into the container
#COPY app/kafka_res/config.ini app/kafka_res/config.ini

# Copy the requirements file
COPY requirements.txt .

#COPY config.ini .
# Install the dependencies

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Set the entrypoint script
CMD  ["python3", "kafka_python.py"]