#!/bin/bash

REPO="SPARC-tpse/SPARC"

# Get the latest release tag
VERSION=$(curl -sL "https://api.github.com/repos/$REPO/releases/latest" | grep -m1 '"tag_name"' | cut -d'"' -f4)

if [ -z "$VERSION" ]; then
    echo "ERROR: No releases found"
    exit 1
fi

echo "Downloading SPARC MES $VERSION..."

# Base download URL
URL="https://github.com/$REPO/releases/download/$VERSION"

# Download files
wget "$URL/sparc-images-$VERSION.tar.gz"
wget "$URL/docker-compose-server.yml"
wget "$URL/run_server.sh"
wget "$URL/README.md"

chmod +x run_server.sh

echo ""
echo "Files downloaded:"
ls -lh

echo ""
echo "To deploy, run: ./run_server.sh"
