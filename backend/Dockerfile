# Backend Dockerfile
FROM python:3.12-slim

# Create app directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

RUN mkdir -p /app/media

# Run Django with Uvicorn
#CMD ["uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]