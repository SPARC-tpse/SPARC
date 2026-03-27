#!/bin/bash

# SPARC MES Server Deployment Script

set -e  # Exit on error

VERSION="${1:-latest}"
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo "==================================="
echo "SPARC MES Deployment Script"
echo "Version: $VERSION"
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
sudo docker compose -f docker-compose.prod.yml down 2>/dev/null || true

# Clean up old Docker resources
echo "Cleaning up old SPARC Docker resources..."
sudo docker rm -f nuxt-frontend
sudo docker rm -f django-backend
sudo docker rm -f redis-cache
sudo docker rmi -f redis:alpine
sudo docker rmi -f sparc-backend:latest
sudo docker rmi -f sparc-frontend:latest


# Load Docker images from tarball if it exists
TARBALL=$(ls sparc-images-*.tar.gz 2>/dev/null | head -1)

if [ -f "$TARBALL" ]; then
    echo "Loading Docker images from tarball..."
    gunzip -c "$TARBALL" | sudo docker load
    echo "Docker images loaded successfully!"

    # Extract version from tarball filename
    LOADED_VERSION=$(echo "$TARBALL" | sed 's/sparc-images-\(.*\)\.tar\.gz/\1/')
    echo "Loaded version: $LOADED_VERSION"

    # Tag images as 'latest' so docker-compose can find them
    echo "Tagging images as 'latest'..."
    sudo docker tag sparc-backend:$LOADED_VERSION sparc-backend:latest
    sudo docker tag sparc-frontend:$LOADED_VERSION sparc-frontend:latest

    echo "Images tagged successfully!"
else
    echo "WARNING: No image tarball found, Docker will build/pull images"
fi

# Start services
echo "Starting SPARC MES services..."
sudo docker compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Run database migrations
echo "Running database migrations..."
sudo docker compose -f docker-compose.prod.yml exec -T backend python manage.py migrate

# Create superuser (optional)
echo ""
echo "==================================="
echo "Create Django superuser (optional)"
echo "==================================="
echo "Would you like to create a superuser? (y/n)"
read -t 10 -r response || response="n"
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    sudo docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
else
    echo "Skipping superuser creation"
fi

echo ""
echo "==================================="
echo "SPARC MES is now running!"
echo "Frontend: http://$LOCAL_IP:3000"
echo "Backend:  http://$LOCAL_IP:8000"
echo "==================================="
echo ""
echo "Useful commands:"
echo "  View logs:    sudo docker compose -f docker-compose.prod.yml logs -f"
echo "  Stop:         sudo docker compose -f docker-compose.prod.yml stop"
echo "  Restart:      sudo docker compose -f docker-compose.prod.yml restart"
echo "  Show status:  sudo docker ps"
