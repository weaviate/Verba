import os
import base64

from wasabi import msg  # type: ignore[import]

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from pathlib import Path
from pydantic import BaseModel

from goldenverba.retrieval.advanced_engine import AdvancedVerbaQueryEngine
from goldenverba import verba_manager

from goldenverba.ingestion.reader.interface import Reader
from goldenverba.ingestion.chunking.interface import Chunker
from goldenverba.ingestion.embedding.interface import Embedder


from dotenv import load_dotenv

load_dotenv()

manager = verba_manager.VerbaManager()

readers = manager.reader_get_readers()
chunker = manager.chunker_get_chunker()
embedders = manager.embedder_get_embedder()

option_cache = {
    "last_reader": list(readers.keys())[0],
    "last_document_type": "Documentation",
    "last_chunker": list(chunker.keys())[0],
    "last_embedder": list(embedders.keys())[0],
}


def create_reader_payload(key: str, reader: Reader) -> dict:
    available, message = manager.check_verba_component(reader)

    return {
        "name": key,
        "description": reader.description,
        "input_form": reader.input_form,
        "available": available,
        "message": message,
    }


def create_chunker_payload(key: str, chunker: Chunker) -> dict:
    available, message = manager.check_verba_component(chunker)

    return {
        "name": key,
        "description": chunker.description,
        "input_form": chunker.input_form,
        "units": chunker.default_units,
        "overlap": chunker.default_overlap,
        "available": available,
        "message": message,
    }


def create_embedder_payload(key: str, embedder: Embedder) -> dict:
    available, message = manager.check_verba_component(embedder)

    return {
        "name": key,
        "description": embedder.description,
        "input_form": embedder.input_form,
        "available": available,
        "message": message,
    }


verba_engine = AdvancedVerbaQueryEngine(manager.client)

# FastAPI App
app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://verba-golden-ragtriever.onrender.com",
    "http://localhost:8000",
]

# Add middleware for handling Cross Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent

# Serve the assets (JS, CSS, images, etc.)
app.mount(
    "/static/_next",
    StaticFiles(directory=BASE_DIR / "frontend/out/_next"),
    name="next-assets",
)

# Serve the main page and other static files
app.mount("/static", StaticFiles(directory=BASE_DIR / "frontend/out"), name="app")


class QueryPayload(BaseModel):
    query: str


class GetDocumentPayload(BaseModel):
    document_id: str


class LoadPayload(BaseModel):
    reader: str
    chunker: str
    embedder: str
    fileBytes: list[str]
    fileNames: list[str]
    filePath: str
    document_type: str
    chunkUnits: int
    chunkOverlap: int


@app.get("/")
@app.head("/")
async def serve_frontend():
    return FileResponse(os.path.join(BASE_DIR, "frontend/out/index.html"))


# Define health check endpoint
@app.get("/api/health")
async def root():
    try:
        if verba_engine.get_client().is_ready():
            return JSONResponse(
                content={
                    "message": "Alive!",
                }
            )
        else:
            return JSONResponse(
                content={
                    "message": "Database not ready!",
                },
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
    except Exception as e:
        msg.fail(f"Healthcheck failed with {str(e)}")
        return JSONResponse(
            content={
                "message": f"Healthcheck failed with {str(e)}",
            },
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


# Define health check endpoint
@app.get("/api/get_google_tag")
async def get_google_tag():
    tag = os.environ.get("VERBA_GOOGLE_TAG", "")

    if tag:
        msg.good("Google Tag available!")

    return JSONResponse(
        content={
            "tag": tag,
        }
    )


# Get Readers, Chunkers, and Embedders
@app.get("/api/get_components")
async def get_components():
    msg.info("Retrieving components")

    data = {"readers": [], "chunker": [], "embedder": []}

    for key in readers:
        current_reader = readers[key]
        current_reader_data = create_reader_payload(key, current_reader)
        data["readers"].append(current_reader_data)

    for key in chunker:
        current_chunker = chunker[key]
        current_chunker_data = create_chunker_payload(key, current_chunker)
        data["chunker"].append(current_chunker_data)

    for key in embedders:
        current_embedder = embedders[key]
        current_embedder_data = create_embedder_payload(key, current_embedder)
        data["embedder"].append(current_embedder_data)

    data["default_values"] = {
        "last_reader": create_reader_payload(
            option_cache["last_reader"], readers[option_cache["last_reader"]]
        ),
        "last_chunker": create_chunker_payload(
            option_cache["last_chunker"], chunker[option_cache["last_chunker"]]
        ),
        "last_embedder": create_embedder_payload(
            option_cache["last_embedder"], embedders[option_cache["last_embedder"]]
        ),
        "last_document_type": option_cache["last_document_type"],
    }

    return JSONResponse(content=data)


# Get Status meta data
@app.get("/api/get_status")
async def get_status():
    msg.info("Retrieving status")

    data = {
        "type": manager.weaviate_type,
        "libraries": manager.installed_libraries,
        "variables": manager.environment_variables,
        "schemas": manager.get_schemas(),
    }

    return JSONResponse(content=data)


# Reset Verba
@app.get("/api/reset")
async def reset_verba():
    msg.info("Resetting verba")

    manager.reset()

    return JSONResponse(status_code=200, content={})


# Receive query and return chunks and query answer
@app.post("/api/load_data")
async def load_data(payload: LoadPayload):
    manager.reader_set_reader(payload.reader)
    manager.chunker_set_chunker(payload.chunker)
    manager.embedder_set_embedder(payload.embedder)

    global option_cache

    option_cache["last_reader"] = payload.reader
    option_cache["last_document_type"] = payload.document_type
    option_cache["last_chunker"] = payload.chunker
    option_cache["last_embedder"] = payload.embedder

    # Set new default values based on user input
    current_chunker = manager.chunker_get_chunker()[payload.chunker]
    current_chunker.default_units = payload.chunkUnits
    current_chunker.default_overlap = payload.chunkOverlap

    msg.info(
        f"Received Data to Import: READER({payload.reader}, Documents {len(payload.fileBytes)}, Type {payload.document_type}) CHUNKER ({payload.chunker}, UNITS {payload.chunkUnits}, OVERLAP {payload.chunkOverlap}), EMBEDDER ({payload.embedder})"
    )

    if payload.fileBytes or payload.filePath:
        try:
            documents = manager.import_data(
                payload.fileBytes,
                [],
                [payload.filePath],
                payload.fileNames,
                payload.document_type,
                payload.chunkUnits,
                payload.chunkOverlap,
            )

            if documents == None:
                return JSONResponse(
                    content={
                        "status": 200,
                        "status_msg": f"Succesfully imported {document_count} documents and {chunks_count} chunks",
                    }
                )

            document_count = len(documents)
            chunks_count = sum([len(document.chunks) for document in documents])

            return JSONResponse(
                content={
                    "status": 200,
                    "status_msg": f"Succesfully imported {document_count} documents and {chunks_count} chunks",
                }
            )
        except Exception as e:
            msg.fail(f"Loading data failed {str(e)}")
            return JSONResponse(
                content={
                    "status": "400",
                    "status_msg": str(e),
                }
            )
    return JSONResponse(
        content={
            "status": "200",
            "status_msg": "No documents received",
        }
    )


# Receive query and return chunks and query answer
@app.post("/api/query")
async def query(payload: QueryPayload):
    try:
        system_msg, results = verba_engine.query(
            payload.query, os.environ["VERBA_MODEL"]
        )
        msg.good(f"Succesfully processed query: {payload.query}")

        return JSONResponse(
            content={
                "system": system_msg,
                "documents": results,
            }
        )
    except Exception as e:
        msg.fail(f"Query failed")
        print(e)
        return JSONResponse(
            content={
                "system": f"Something went wrong! {str(e)}",
                "documents": [],
            }
        )


# Retrieve auto complete suggestions based on user input
@app.post("/api/suggestions")
async def suggestions(payload: QueryPayload):
    try:
        suggestions = verba_engine.get_suggestions(payload.query)

        return JSONResponse(
            content={
                "suggestions": suggestions,
            }
        )
    except Exception as e:
        return JSONResponse(
            content={
                "suggestions": [],
            }
        )


# Retrieve specific document based on UUID
@app.post("/api/get_document")
async def get_document(payload: GetDocumentPayload):
    msg.info(f"Document ID received: {payload.document_id}")

    try:
        document = manager.retrieve_document(payload.document_id)
        msg.good(f"Succesfully retrieved document: {payload.document_id}")
        return JSONResponse(
            content={
                "document": document,
            }
        )
    except Exception as e:
        msg.fail(f"Document retrieval failed: {str(e)}")
        return JSONResponse(
            content={
                "document": {},
            }
        )


## Retrieve all documents imported to Weaviate
@app.post("/api/get_all_documents")
async def get_all_documents():
    msg.info(f"Get all documents request received")

    try:
        documents = manager.retrieve_all_documents()
        msg.good(f"Succesfully retrieved document: {len(documents)} documents")
        return JSONResponse(
            content={
                "documents": documents,
            }
        )
    except Exception as e:
        msg.fail(f"All Document retrieval failed: {str(e)}")
        return JSONResponse(
            content={
                "documents": [],
            }
        )


## Search for documentation
@app.post("/api/search_documents")
async def search_documents(payload: QueryPayload):
    try:
        documents = verba_engine.search_documents(payload.query)
        return JSONResponse(
            content={
                "documents": documents,
            }
        )
    except Exception as e:
        msg.fail(f"All Document retrieval failed: {str(e)}")
        return JSONResponse(
            content={
                "documents": [],
            }
        )
