#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Vijil Verba RAG Setup Script ===${NC}"
echo "Setting up Ollama (Local), Weaviate, and Verba..."

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Check if Docker Desktop is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker Desktop not found. Installing...${NC}"
    # Download the latest Docker.dmg
    curl -o Docker.dmg https://desktop.docker.com/mac/main/arm64/Docker.dmg
    
    # Mount the DMG
    hdiutil attach Docker.dmg
    
    # Copy the app to Applications folder
    cp -R "/Volumes/Docker/Docker.app" /Applications/
    
    # Unmount the DMG
    hdiutil detach "/Volumes/Docker"
    
    # Clean up
    rm Docker.dmg
    
    echo -e "${GREEN}Docker Desktop installed. Please start Docker Desktop and then run this script again.${NC}"
    echo "After Docker Desktop is running, run this script again."
    open "/Applications/Docker.app"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}Docker is not running and will be started. Please run the installer again.${NC}"
    open "/Applications/Docker.app"
    exit 1
fi

echo -e "${GREEN}Docker is running.${NC}"

# Install Ollama if not installed
if ! command_exists ollama; then
    echo -e "${RED}Ollama is not installed. Installing Ollama...${NC}"
    curl -fsSL https://ollama.com/install.sh | sh

    if command_exists ollama; then
        echo -e "${GREEN}Ollama installed successfully.${NC}"
    else
        echo -e "${RED}Failed to install Ollama. Please install manually.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}Ollama is already installed.${NC}"
fi

# Ensure Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo -e "${BLUE}Starting Ollama...${NC}"
    ollama serve &>/dev/null &
    sleep 5
fi

# Find an available port starting from 3000
find_available_port() {
    local port=8000
    while lsof -i :$port >/dev/null 2>&1; do
        echo "Port ${port} is in use, trying next port..."
        port=$((port + 1))
    done
    echo $port
}

UI_PORT=$(find_available_port)
echo -e "${GREEN}Using port ${UI_PORT} for Verba${NC}"

# Pull the required Ollama model only if no models exist
MODEL_NAME="llama3.2:1b"
if ollama list | grep -q .; then
    echo -e "${GREEN}At least one Ollama model is already installed.${NC}"
else
    echo -e "${BLUE}No Ollama models found. Pulling default model: $MODEL_NAME...${NC}"
    ollama pull "$MODEL_NAME"
fi

# Create the Docker network if it doesn't exist
if ! docker network inspect ollama-docker &> /dev/null; then
    echo "Creating docker network 'ollama-docker'..."
    docker network create ollama-docker
    echo -e "${GREEN}Network created.${NC}"
else
    echo -e "${GREEN}Network 'ollama-docker' already exists.${NC}"
fi

# Stop and remove existing containers
for container in verba-vijil; do
    if docker ps -a | grep -q $container; then
        echo "Stopping and removing existing $container..."
        docker stop $container
        docker rm $container
    fi
done

sleep 10

# echo "Starting Transformers Inference API..."
# docker run -d --name t2v-transformers \
#     --network ollama-docker \
#     -p 8081:8080 \
#     cr.weaviate.io/semitechnologies/transformers-inference:sentence-transformers-all-MiniLM-L6-v2

# **Run Weaviate**
# echo "Starting Weaviate..."
# docker run -d --name weaviate \
#     --network ollama-docker \
#     -p 8080:8080 \
#     -v weaviate_data:/var/lib/weaviate \
#     --restart on-failure:0 \
#     -e QUERY_DEFAULTS_LIMIT=25 \
#     -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
#     -e PERSISTENCE_DATA_PATH="/var/lib/weaviate" \
#     -e ENABLE_MODULES="text2vec-transformers" \
#     -e TRANSFORMERS_INFERENCE_API="http://t2v-transformers:8080" \
#     semitechnologies/weaviate:1.25.10

# **Run Verba**
echo "Starting Verba..."
docker run -d --name verba-vijil \
    --network ollama-docker \
    -p ${UI_PORT}:8000 \
    -v ./data:/data \
    -e OLLAMA_URL="http://host.docker.internal:11434" \
    -e OLLAMA_MODEL=$MODEL_NAME \
    -e DEFAULT_DEPLOYMENT="Local" \
    --restart always \
    ansharora23/verba-vijil:mac

# **Check running services**
echo -e "${BLUE}Checking if services are running...${NC}"

for service in verba-vijil; do
    if docker ps | grep -q "$service"; then
        echo -e "${GREEN}✓ $service is running${NC}"
    else
        echo -e "${RED}✗ $service failed to start${NC}"
    fi
done

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${BLUE}Verba API is available at: http://localhost:${UI_PORT}${NC}"
# echo -e "${BLUE}Weaviate is available at: http://localhost:8080${NC}"

sleep 15

# Open browser
echo "Opening browser..."
open "http://localhost:${UI_PORT}"

echo -e "${BLUE}=== Additional Information ===${NC}"
echo "- To stop the services: docker stop weaviate verba-vijil"
echo "- To start the services: docker start weaviate verba-vijil"
echo "- Verba data is stored in the 'weaviate_data' Docker volume"
echo "- Verba is running on port: ${UI_PORT}"