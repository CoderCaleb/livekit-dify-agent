# Use an official Python base image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy requirements first and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app
COPY . .

# Command to run your agent
CMD ["python", "agent.py"]
