from fastapi import FastAPI, Request, WebSocket, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import os
from pathlib import Path

from dotenv import load_dotenv
from starlette.websockets import WebSocketDisconnect
from wasabi import msg  # type: ignore[import]
import time

from goldenverba import verba_manager
from goldenverba.server.ConfigManager import ConfigManager
from goldenverba.server.types import GetComponentPayload, ConfigPayload, SetComponentPayload, LoadPayload, QueryPayload, GeneratePayload, GetDocumentPayload, SearchQueryPayload, ImportPayload
from goldenverba.server.util import get_config, set_config, setup_managers, create_reader_payload, create_chunker_payload, create_embedder_payload, create_generator_payload, create_retriever_payload

load_dotenv()

# Check if runs in production
production_key = os.environ.get("VERBA_PRODUCTION", "")
if production_key == "True":
    msg.info("API runs in Production Mode")
    production = True
else:
    production = False

manager = verba_manager.VerbaManager()
config_manager = ConfigManager()

readers = manager.reader_get_readers()
chunker = manager.chunker_get_chunker()
embedders = manager.embedder_get_embedder()
retrievers = manager.retriever_get_retriever()
generators = manager.generator_get_generator()

setup_managers(
    manager, config_manager, readers, chunker, embedders, retrievers, generators
)
config_manager.save_config()

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


@app.get("/")
@app.head("/")
async def serve_frontend():
    return FileResponse(os.path.join(BASE_DIR, "frontend/out/index.html"))

# Define health check endpoint
@app.get("/api/health")
async def root():
    try:
        if manager.client.is_ready():
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


@app.get("/api/get_production")
async def get_production():
    return JSONResponse(
        content={
            "production": production,
        }
    )


# Get Readers, Chunkers, and Embedders
@app.get("/api/get_components")
async def get_components():
    msg.info("Retrieving components")

    data = {"readers": [], "chunker": [], "embedder": []}

    for key in readers:
        current_reader = readers[key]
        current_reader_data = create_reader_payload(manager, key, current_reader)
        data["readers"].append(current_reader_data)

    for key in chunker:
        current_chunker = chunker[key]
        current_chunker_data = create_chunker_payload(manager, key, current_chunker)
        data["chunker"].append(current_chunker_data)

    for key in embedders:
        current_embedder = embedders[key]
        current_embedder_data = create_embedder_payload(manager, key, current_embedder)
        data["embedder"].append(current_embedder_data)

    try:
        data["default_values"] = {
            "last_reader": create_reader_payload(
                manager, config_manager.get_reader(), readers[config_manager.get_reader()]
            ),
            "last_chunker": create_chunker_payload(
                manager, config_manager.get_chunker(), chunker[config_manager.get_chunker()]
            ),
            "last_embedder": create_embedder_payload(
                manager, config_manager.get_embedder(), embedders[config_manager.get_embedder()]
            ),
            "last_document_type": "Documentation",
        }
    except KeyError:
        # Reset Config
        msg.warn("Mismatched Config detected, resetting managers")
        config_manager.default_config()
        config_manager.save_config()
        setup_managers(
            manager, config_manager, readers, chunker, embedders, retrievers, generators
        )
        config_manager.save_config()
        data["default_values"] = {
            "last_reader": create_reader_payload(
                config_manager.get_reader(), readers[config_manager.get_reader()]
            ),
            "last_chunker": create_chunker_payload(
                config_manager.get_chunker(), chunker[config_manager.get_chunker()]
            ),
            "last_embedder": create_embedder_payload(
                config_manager.get_embedder(), embedders[config_manager.get_embedder()]
            ),
            "last_document_type": "Documentation",
        }

    return JSONResponse(content=data)

# Get Configuration
@app.get("/api/config")
async def retrieve_config():
    msg.info("Retrieving configuration")

    try:
        config = get_config(manager)
        return JSONResponse(status_code=200, content={"data":config, "error":""})

    except Exception as e:
        msg.warn(f"Could not retrieve configuration: {str(e)}")
        return JSONResponse(status_code=200, content={"data":{}, "error":f"Could not retrieve configuration: {str(e)}"})


@app.post("/api/get_component")
async def get_component(payload: GetComponentPayload):
    msg.info(f"Retrieving {payload.component} components")

    data = {"components": []}

    if payload.component == "embedders":
        data["selected_component"] = create_embedder_payload(
            manager.embedder_manager.selected_embedder,
            manager.embedder_manager.selected_embedder,
        )

        for key in embedders:
            current_embedder = embedders[key]
            current_embedder_data = create_embedder_payload(key, current_embedder)
            data["components"].append(current_embedder_data)

    elif payload.component == "retrievers":
        data["selected_component"] = create_retriever_payload(
            manager.retriever_manager.selected_retriever.name,
            manager.retriever_manager.selected_retriever,
        )

        for key in retrievers:
            current_retriever = retrievers[key]
            current_retriever_data = create_retriever_payload(key, current_retriever)
            data["components"].append(current_retriever_data)

    elif payload.component == "generators":
        data["selected_component"] = create_generator_payload(
            manager.generator_manager.selected_generator.name,
            manager.generator_manager.selected_generator,
        )

        for key in generators:
            current_generator = generators[key]
            current_generator_data = create_generator_payload(key, current_generator)
            data["components"].append(current_generator_data)

    return JSONResponse(content=data)


@app.post("/api/set_component")
async def set_component(payload: SetComponentPayload):
    if production:
        return JSONResponse(content={})

    msg.info(f"Setting {payload.component} to {payload.selected_component}")

    if payload.component == "embedders":
        manager.embedder_manager.set_embedder(payload.selected_component)
        config_manager.set_embedder(payload.selected_component)

    elif payload.component == "retrievers":
        manager.retriever_manager.set_retriever(payload.selected_component)
        config_manager.set_retriever(payload.selected_component)

    elif payload.component == "generators":
        manager.generator_manager.set_generator(payload.selected_component)
        config_manager.set_generator(payload.selected_component)

    config_manager.save_config()

    return JSONResponse(content={})


# Get Status meta data
@app.get("/api/get_status")
async def get_status():
    msg.info("Retrieving status")

    try:

        schemas = manager.get_schemas()
        sorted_schemas = dict(sorted(schemas.items(), key=lambda item: item[1], reverse=True))

        sorted_libraries = dict(sorted(manager.installed_libraries.items(), key=lambda item: (not item[1], item[0])))
        sorted_variables = dict(sorted(manager.environment_variables.items(), key=lambda item: (not item[1], item[0])))

        data = {
            "type": manager.weaviate_type,
            "libraries": sorted_libraries,
            "variables": sorted_variables,
            "schemas": sorted_schemas,
            "error": ""
        }

        return JSONResponse(content=data)
    except Exception as e:
        data = {
            "type": "",
            "libraries": {},
            "variables": {},
            "schemas": {},
            "error": f"Status retrieval failed: {str(e)}"
        }
        msg.fail(f"Status retrieval failed: {str(e)}")
        return JSONResponse(content=data)


# Reset Verba
@app.get("/api/reset")
async def reset_verba():
    if production:
        return JSONResponse(status_code=200, content={})

    msg.info("Resetting verba")

    manager.reset()

    return JSONResponse(status_code=200, content={})


# Reset Verba
@app.get("/api/reset_cache")
async def reset_cache():
    if production:
        return JSONResponse(status_code=200, content={})
    msg.info("Resetting cache")

    manager.reset_cache()

    return JSONResponse(status_code=200, content={})


# Reset Verba suggestions
@app.get("/api/reset_suggestion")
async def reset_suggestion():
    if production:
        return JSONResponse(status_code=200, content={})
    msg.info("Resetting suggestions")

    manager.reset_suggestion()

    return JSONResponse(status_code=200, content={})

# Receive query and return chunks and query answer
@app.post("/api/import")
async def import_data(payload: ImportPayload):

    try:
        logging = []
        set_config(manager, payload.config)
        documents, logging = manager.import_data(payload.data, logging)

        return JSONResponse(
            content={
                "logging": logging,
            }
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "logging": [{"type":"ERROR","message":str(e)}],
            }
        )
    


@app.post("/api/set_config")
async def update_config(payload: ConfigPayload):

    set_config(manager, payload.config)

    return JSONResponse(
        content={
            "status": "200",
            "status_msg": "Config Updated",
        }
    )

# Receive query and return chunks and query answer
@app.post("/api/load_data")
async def load_data(payload: LoadPayload):
    if production:
        return JSONResponse(
            content={
                "status": "200",
                "status_msg": "Can't add data when in production mode",
            }
        )

    manager.reader_set_reader(payload.reader)
    manager.chunker_set_chunker(payload.chunker)
    manager.embedder_set_embedder(payload.embedder)

    config_manager.set_reader(payload.reader)
    config_manager.set_chunker(payload.chunker)
    config_manager.set_embedder(payload.embedder)
    config_manager.save_config()

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

            if documents is None:
                return JSONResponse(
                    content={
                        "status": 200,
                        "status_msg": "No documents imported",
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
    msg.good(f"Received query: {payload.query}")
    start_time = time.time()  # Start timing
    try:
        chunks, context = manager.retrieve_chunks([payload.query])

        # Sort chunks based on score in descending order
        chunks = sorted(chunks, key=lambda x: x.score, reverse=True)

        retrieved_chunks = [
            {
                "text": chunk.text,
                "doc_name": chunk.doc_name,
                "chunk_id": chunk.chunk_id,
                "doc_uuid": chunk.doc_uuid,
                "doc_type": chunk.doc_type,
                "score": chunk.score,
            }
            for chunk in chunks
        ]

        elapsed_time = round(time.time() - start_time , 2) # Calculate elapsed time
        msg.good(f"Succesfully processed query: {payload.query} in {elapsed_time}s")

        if len(chunks) == 0:
            return JSONResponse(
                content={
                    "chunks": [],
                    "took": 0,
                    "context": "",
                    "error": "Chunks could be retrieved"
                }
            )

        return JSONResponse(
            content={
                "error": "",
                "chunks": retrieved_chunks,
                "context": context,
                "took": elapsed_time
            }
        )

    except Exception as e:
        msg.fail(f"Query failed: {str(e)}")
        return JSONResponse(
            content={
                "error": f"Something went wrong! {str(e)}",
                "context": "",
                "documents": [],
            }
        )


# Receive query and return chunks and query answer
@app.post("/api/generate")
async def generate(payload: GeneratePayload):
    msg.good(f"Received generate call for: {payload.query}")
    try:
        answer = await manager.generate_answer(
            [payload.query], [payload.context], payload.conversation
        )

        msg.good(f"Succesfully generated answer: {payload.query}")

        return JSONResponse(
            content={
                "system": answer,
            }
        )

    except Exception as e:
        raise
        msg.fail(f"Answer Generation failed: {str(e)}")
        return JSONResponse(
            content={
                "system": f"Something went wrong! {str(e)}",
            }
        )


@app.websocket("/ws/generate_stream")
async def websocket_generate_stream(websocket: WebSocket):
    await websocket.accept()
    while True:  # Start a loop to keep the connection alive.
        try:
            data = await websocket.receive_text()
            # Parse and validate the JSON string using Pydantic model
            payload = GeneratePayload.model_validate_json(data)
            msg.good(f"Received generate stream call for {payload.query}")
            full_text = ""
            async for chunk in manager.generate_stream_answer(
                [payload.query], [payload.context], payload.conversation
            ):
                full_text += chunk["message"]
                if chunk["finish_reason"] == "stop":
                    chunk["full_text"] = full_text
                await websocket.send_json(chunk)

        except WebSocketDisconnect:
            msg.warn("WebSocket connection closed by client.")
            break  # Break out of the loop when the client disconnects

        except Exception as e:
            msg.fail(f"WebSocket Error: {e}")
            await websocket.send_json(
                {"message": e, "finish_reason": "stop", "full_text": e}
            )
        msg.good("Succesfully streamed answer")


# Retrieve auto complete suggestions based on user input
@app.post("/api/suggestions")
async def suggestions(payload: QueryPayload):
    try:
        suggestions = manager.get_suggestions(payload.query)

        return JSONResponse(
            content={
                "suggestions": suggestions,
            }
        )
    except Exception:
        return JSONResponse(
            content={
                "suggestions": [],
            }
        )


# Retrieve specific document based on UUID
@app.post("/api/get_document")
async def get_document(payload: GetDocumentPayload):
    # TODO Standarize Document Creation
    msg.info(f"Document ID received: {payload.document_id}")

    try:
        document = manager.retrieve_document(payload.document_id)
        document_properties = document.get("properties",{})
        document_obj = {
            "class":document.get("class","No Class"),
            "id":document.get("id",payload.document_id),
            "chunks":document_properties.get("chunk_count", 0),
            "link":document_properties.get("doc_link", ""),
            "name":document_properties.get("doc_name", "No name"),
            "type":document_properties.get("doc_type", "No type"),
            "text":document_properties.get("text", "No text"),
            "timestamp":document_properties.get("timestamp", ""),
        }

        msg.good(f"Succesfully retrieved document: {payload.document_id}")
        return JSONResponse(
            content={
                "error": "",
                "document": document_obj,
            }
        )
    except Exception as e:
        msg.fail(f"Document retrieval failed: {str(e)}")
        return JSONResponse(
            content={
                "error": str(e),
                "document": None,
            }
        )


## Retrieve all documents imported to Weaviate
@app.post("/api/get_all_documents")
async def get_all_documents(payload: SearchQueryPayload):
    # TODO Standarize Document Creation
    msg.info("Get all documents request received")
    start_time = time.time()  # Start timing

    try:
        if payload.query == "":
            documents = manager.retrieve_all_documents(payload.doc_type, payload.page, payload.pageSize)
        else:
            documents = manager.search_documents(payload.query, payload.doc_type, payload.page, payload.pageSize)

        if not documents:
             return JSONResponse(
            content={
                "documents": [],
                "doc_types": [],
                "current_embedder": manager.embedder_manager.selected_embedder,
                "error": f"No Results found!",
                "took": 0
            }
        )
            
        documents_obj = []
        for document in documents:

            _additional = document["_additional"]

            documents_obj.append({
            "class":"No Class",
            "uuid":_additional.get("id","none"),
            "chunks":document.get("chunk_count", 0),
            "link":document.get("doc_link", ""),
            "name":document.get("doc_name", "No name"),
            "type":document.get("doc_type", "No type"),
            "text":document.get("text", "No text"),
            "timestamp":document.get("timestamp", ""),
        })
            
        elapsed_time = round(time.time() - start_time , 2) # Calculate elapsed time
        msg.good(f"Succesfully retrieved document: {len(documents)} documents in {elapsed_time}s")

        doc_types = manager.retrieve_all_document_types()

        return JSONResponse(
            content={
                "documents": documents_obj,
                "doc_types": list(doc_types),
                "current_embedder": manager.embedder_manager.selected_embedder,
                "error": "",
                "took": elapsed_time
            }
        )
    except Exception as e:
        msg.fail(f"All Document retrieval failed: {str(e)}")
        return JSONResponse(
            content={
                "documents": [],
                "doc_types": [],
                "current_embedder": manager.embedder_manager.selected_embedder,
                "error": f"All Document retrieval failed: {str(e)}",
                "took": 0
            }
        )


# Retrieve specific document based on UUID
@app.post("/api/delete_document")
async def delete_document(payload: GetDocumentPayload):
    if production:
        return JSONResponse(status_code=200, content={})

    msg.info(f"Document ID received: {payload.document_id}")

    manager.delete_document_by_id(payload.document_id)
    return JSONResponse(content={})
