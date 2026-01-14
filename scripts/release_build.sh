#!/bin/bash
set -e

# Sync python dependencies (updates uv.lock)
echo "Syncing uv dependencies..."
uv sync

# Install frontend dependencies (updates package-lock.json)
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Stage the lockfiles for the release commit
echo "Staging lockfiles..."
git add uv.lock frontend/package-lock.json
