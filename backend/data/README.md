# Data Directory

Place your CSV files in this directory. They will be accessible to the backend container at `/app/data/`.

## CSV File Loading

Once you place a CSV file here (e.g., `data.csv`), you can load it into ChromaDB using the API endpoint:

```bash
POST /chroma/load-csv?filename=data.csv
```

The API will automatically:
1. Read the CSV file
2. Process each row as a document
3. Add documents to the ChromaDB collection

## Example

```bash
curl -X POST "http://localhost:8000/chroma/load-csv?filename=your-file.csv"
```
