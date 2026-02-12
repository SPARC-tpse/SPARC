#!/bin/bash

# SPARC MES Server Deployment Script

set -e  # Exit on error

echo "==================================="
echo "SPARC MES Deployment Script"
echo "==================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed!"
    echo "Please install Docker first: https://docs.docker.com/engine/install/"
    exit 1
fi

# Check if docker compose is available
if ! docker compose version &> /dev/null; then
    echo "ERROR: Docker Compose is not available!"
    echo "Please install Docker Compose plugin"
    exit 1
fi

# Stop and remove existing containers
echo "Stopping existing containers..."
sudo docker compose -f docker-compose-server.yml down 2>/dev/null || true

# Clean up old Docker resources (optional - uncomment if you want full cleanup)
echo "Cleaning up old Docker resources..."
sudo docker container prune -f
sudo docker image prune -a -f
# sudo docker volume prune -f

# Load Docker images from tarball if it exists
if [ -f sparc-images-*.tar.gz ]; then
    echo "Loading Docker images from tarball..."
    gunzip -c sparc-images-*.tar.gz | sudo docker load
    echo "Docker images loaded successfully!"
else
    echo "WARNING: No image tarball found, Docker will build/pull images"
fi

# Start services
echo "Starting SPARC MES services..."
sudo docker compose -f docker-compose-server.yml up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Run database migrations
echo "Running database migrations..."
sudo docker compose -f docker-compose-server.yml exec -T backend python manage.py migrate

# Create superuser (optional - comment out if you don't want this automated)
echo ""
echo "==================================="
echo "Create Django superuser"
echo "==================================="
sudo docker compose -f docker-compose-server.yml exec backend python manage.py createsuperuser --noinput --username admin --email admin@example.com 2>/dev/null || echo "Superuser already exists or creation skipped"

echo ""
echo "==================================="
echo "SPARC MES is now running!"
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo "==================================="
echo ""
echo "Useful commands:"
echo "  View logs:    sudo docker compose -f docker-compose-server.yml logs -f"
echo "  Stop:         sudo docker compose -f docker-compose-server.yml down"
echo "  Restart:      sudo docker compose -f docker-compose-server.yml restart"
echo "  Show status:  sudo docker ps"
