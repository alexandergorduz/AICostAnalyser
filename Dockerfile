# Use an official Python runtime as a parent image
FROM python:3.12-slim

ENV TZ=Europe/Kiev \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy .env file
COPY .env .env

# Copy the rest of the application code
COPY . .

# Run the bot
CMD ["python", "-u", "bot.py"]