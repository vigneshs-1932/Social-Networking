# Use the official Python image from the Docker Hub
FROM python:3.12

# Set the working directory in the container
WORKDIR /Social-Networking

# Install system dependencies, including netcat-openbsd
RUN apt-get update && apt-get install -y netcat-openbsd

# Copy and install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entrypoint script into the container
COPY ./docker_entrypoint.sh .

# Ensure the entrypoint script is executable
RUN chmod +x docker_entrypoint.sh

# Use the entrypoint script to run the Django server
ENTRYPOINT ["./docker_entrypoint.sh"]
