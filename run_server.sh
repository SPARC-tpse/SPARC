#!/bin/bash

# SPARC MES Server Deployment Script

set -e  # Exit on error

VERSION="${1:-latest}"

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

# ------------------------------------
# DATABASE BACKUP before touching anything
# ------------------------------------
echo "Backing up database..."
BACKUP_DIR="./db_backups"
mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql"

# Try to back up — skip gracefully if DB container isn't running yet
if sudo docker compose -f docker-compose-server.yml ps 2>/dev/null | grep -q "db\|postgres\|mysql"; then
    sudo docker compose -f docker-compose-server.yml exec -T db \
        sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > "$BACKUP_FILE" 2>/dev/null \
        && echo "Database backed up to $BACKUP_FILE" \
        || echo "WARNING: Backup failed or DB not ready — continuing anyway"
else
    echo "No running DB container found — skipping backup"
fi

# ------------------------------------
# Stop containers WITHOUT wiping volumes
# ------------------------------------
echo "Stopping existing containers (preserving volumes)..."
# NOTE: 'down' without '-v' keeps named volumes safe.
#       We intentionally do NOT pass '-v' here.
sudo docker compose -f docker-compose-server.yml down 2>/dev/null || true

# Clean up OLD containers only (NOT volumes)
echo "Cleaning up stopped containers..."
sudo docker container prune -f

# Clean up dangling images only (NOT all images, to avoid losing DB images)
echo "Cleaning up dangling images..."
sudo docker image prune -f
# Removed: 'docker image prune -a' — this was removing ALL unused images
# including ones needed to restore DB state on next run.

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
sudo docker compose -f docker-compose-server.yml up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# ------------------------------------
# Run ONLY new migrations (not --run-syncdb or fresh migrate)
# ------------------------------------
echo "Running database migrations..."
sudo docker compose -f docker-compose-server.yml exec -T backend python manage.py migrate --no-input
# '--no-input' prevents Django from prompting and stalling the script.
# 'migrate' on an existing DB only applies unapplied migrations — it won't wipe data.

# Create superuser (optional)
echo ""
echo "==================================="
echo "Create Django superuser (optional)"
echo "==================================="
echo "Would you like to create a superuser? (y/n)"
read -t 10 -r response || response="n"
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    sudo docker compose -f docker-compose-server.yml exec backend python manage.py createsuperuser
else
    echo "Skipping superuser creation"
fi

echo ""
echo "==================================="
echo "SPARC MES is now running!"
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo "==================================="
echo ""
echo "Useful commands:"
echo "  View logs:    sudo docker compose -f docker-compose-server.yml logs -f"
echo "  Stop:         sudo docker compose -f docker-compose-server.yml stop"
echo "  Restart:      sudo docker compose -f docker-compose-server.yml restart"
echo "  Show status:  sudo docker ps"
echo "  DB backups:   ls $BACKUP_DIR"