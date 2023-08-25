# Create Document and Chunk Schema, deletes existing schemas
python WeaviateIngestion/create-schema.py

# Create Cache, delete existing cache
python WeaviateIngestion/create-cache-schema.py

# Create Suggestions, delete existing cache
python WeaviateIngestion/create-suggestion-schema.py

# Load and chunk data to import into Weaviate (Using Haystrack processing)
python WeaviateIngestion/import_weaviate.py

# Start API
uvicorn api:app --reload --host 0.0.0.0 --port 8001