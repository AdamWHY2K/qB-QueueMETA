# Use a lightweight base image with Python
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script
COPY qB-QueueMETA.py .

# Entrypoint to allow passing args via `command:` in Compose
ENTRYPOINT ["python", "qB-QueueMETA.py"]
