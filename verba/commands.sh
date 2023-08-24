# Create BlogPost Schema, deletes existing BlogPost schema
python WeaviateIngestion/create-schema.py

# Load and chunk data to import into Weaviate (Using Haystrack processing)
python WeaviateIngestion/import_weaviate.py

# Start API
uvicorn api:app --reload --host 0.0.0.0 --port 8000