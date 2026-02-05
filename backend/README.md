# Backend API with ChromaDB

Python FastAPI backend with ChromaDB vector database integration.

## API Endpoints

### Health & Info
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /chroma/info` - Get ChromaDB collection information

### ChromaDB Operations
- `POST /chroma/add` - Add documents to the collection
  ```json
  {
    "documents": ["text1", "text2"],
    "ids": ["id1", "id2"],
    "metadatas": [{"key": "value"}, {"key": "value"}]
  }
  ```

- `POST /chroma/query` - Query documents
  ```json
  {
    "query_text": "search query",
    "n_results": 5
  }
  ```

- `DELETE /chroma/clear` - Clear all documents from collection

## Development

The backend runs on port 8000 and includes hot-reload for development.

## Data Persistence

ChromaDB data is persisted in a Docker volume named `chroma_data`.
