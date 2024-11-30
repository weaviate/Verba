# Verba with Ollama Integration on Azure

This deployment runs Verba (a web-based RAG application) integrated with Ollama for local LLM capabilities, using Weaviate as the vector database.

## Service URLs

- Verba UI: http://argon-dev.behaviorlabs.ai:8001
- Verba API: http://argon-dev.behaviorlabs.ai:8001/docs
- Weaviate: http://argon-dev.behaviorlabs.ai:8085
- Ollama API: http://argon-dev.behaviorlabs.ai:11435
- Ollama Web UI: http://argon-dev.behaviorlabs.ai:8086

## Architecture

- **Verba**: Frontend and API server for RAG operations
- **Weaviate**: Vector database for document storage and retrieval
- **Ollama**: Local LLM server with GPU acceleration
- **Ollama Web UI**: Web interface for direct interaction with Ollama

## Network Security

Current NSG rules can be inspected with:
```bash
az network nsg rule list \
    --resource-group DK_Corp \
    --nsg-name YOUR_NSG_NAME \
    --output table
```

Required ports:
- 8001: Verba UI/API
- 8085: Weaviate
- 11435: Ollama API
- 8086: Ollama Web UI

## Deployment

### Prerequisites
- Docker
- Docker Compose
- GPU with CUDA support
- Azure CLI

### Environment Setup
1. Create required directories:
```bash
mkdir -p ./ollama/ollama ./ollama/ollama-webui
```

2. Create environment file (.env.dk-carbon-staging):
```env
VERBA_PRODUCTION=Local
WEAVIATE_URL_VERBA=http://weaviate:8080
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=llama2:70b
```

### Deployment Commands

Start the services:
```bash
docker compose -f docker-compose.ollama.yml --env-file .env.dk-carbon-staging up -d
```

Monitor logs:
```bash
docker compose -f docker-compose.ollama.yml logs -f
```

Verify services:
```bash
# Check Weaviate
curl http://localhost:8085/v1/.well-known/ready

# Check Ollama
curl http://localhost:11435/api/version

# Check Verba health
curl http://localhost:8001/api/health
```

### GPU Requirements

The setup expects access to an NVIDIA GPU. Verify GPU availability:
```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

## Common Issues

1. Port conflicts:
   - Check for port availability: `sudo lsof -i :[PORT]`
   - Modify docker-compose.ollama.yml if needed

2. GPU access:
   - Verify NVIDIA drivers: `nvidia-smi`
   - Check Docker GPU support: `docker info | grep -i gpu`

## Data Persistence

- Ollama models are stored in `./ollama/ollama`
- Weaviate data persists in a Docker volume `weaviate_data`

## Monitoring

Check service status:
```bash
docker compose -f docker-compose.ollama.yml ps
```

View resource usage:
```bash
docker stats
```