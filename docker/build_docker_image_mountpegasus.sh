#!/bin/bash
set -euo pipefail   # Good practice: exit on error, undefined var, and pipe failures

# Optional: remove old image only if it exists (prevents errors if it doesn't)
# docker rmi irlab-image 2>/dev/null || true

# Build the new image
docker build \
  -f Dockerfile.mountpegasus \
  --build-arg NUM_THREADS=20 \
  --rm \
  -t editpegasus-isaac-ros2-image_5_1 \
  . 

echo "Image editpegasus-isaac-ros2-image_5_1 built successfully!"

# # Build the new image
# docker build \
#   -f Dockerfile.mountpegasus \
#   --build-arg NUM_THREADS=20 \
#   --no-cache \
#   --rm \
#   -t editpegasus-isaac-ros2-image_5_1 \
#   . 

# echo "Image editpegasus-isaac-ros2-image_5_1 built successfully!"