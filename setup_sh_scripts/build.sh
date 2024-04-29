#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

# Replace the values in these variables with your own
REPO_URL="https://github.com/jaylenwang7/DeathStarBench.git"
REPO="DeathStarBench"
SUBDIR="socialNetwork"
DOCKER_USERNAME="jaylenwang"
DOCKER_PASSWORD="nelyajj2002"
IMAGE_NAME="social-network-microservices"
TAG="test"

# Checkout and pull the latest code from the repository
cd ~/$REPO
git checkout test
git pull origin test
cd $SUBDIR

# Build the Docker image using the Dockerfile in the repository
docker build -t $DOCKER_USERNAME/$IMAGE_NAME:$TAG .

# Login to Docker Hub
echo $DOCKER_PASSWORD | docker login --username $DOCKER_USERNAME --password-stdin

# Push the Docker image to Docker Hub
docker push $DOCKER_USERNAME/$IMAGE_NAME:$TAG