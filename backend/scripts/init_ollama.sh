#!/bin/bash
# Wait for Ollama to be ready and pull required model

echo "Waiting for Ollama service..."
until curl -s http://ollama:11434/ > /dev/null 2>&1; do
    sleep 2
done

echo "Ollama is ready. Pulling embedding model..."
curl http://ollama:11434/api/pull -d '{
  "name": "nomic-embed-text"
}'

echo "Model ready!"
