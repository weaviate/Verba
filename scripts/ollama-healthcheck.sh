#!/bin/sh
set -x
if curl -s http://localhost:11434/ | grep -q "Ollama is running"; then
    echo "Ollama is running and responding!"
    exit 0
else
    echo "Ollama health check failed"
    exit 1
fi