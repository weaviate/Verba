# Create BlogPost Schema, deletes existing BlogPost schema
python create-schema.py

# Load and chunk data to import into Weaviate (Using Haystrack processing)
python import-data-haystack.py

# Start API
uvicorn api:app --reload --host 0.0.0.0 --port 8000