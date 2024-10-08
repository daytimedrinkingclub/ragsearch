# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy the rest of the application code into the container
COPY . .

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# Expose the port the app runs on (this is just for documentation, not binding)
EXPOSE ${FLASK_RUN_PORT}

# Run the gunicorn server
CMD ["gunicorn", "-b", "0.0.0.0:${FLASK_RUN_PORT}", "run:app"]