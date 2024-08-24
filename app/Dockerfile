# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app, The COPY . /app command copies the local directory into the container's /app directory.
COPY . /app/

# Copy only requirements.txt to leverage Docker cache
COPY requirements.txt /app/

# Install Falcon and Waitress
RUN pip install --no-cache-dir -r requirements.txt


# Expose the port on which the Falcon API will listen
EXPOSE 8000

CMD  ["python3", "rest_api.py"]