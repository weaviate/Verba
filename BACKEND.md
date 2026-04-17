# Verba Backend Developer Guide

This guide is written for developers who want to contribute a new component to Verba — most commonly a new LLM provider (Generator), embedding provider (Embedder), file reader, or chunking strategy. It covers the plugin architecture, the data flow, the config system, and step-by-step walkthroughs for each component type.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [The Component Plugin System](#the-component-plugin-system)
4. [How to Add a New Generator](#how-to-add-a-new-generator)
5. [How to Add a New Embedder](#how-to-add-a-new-embedder)
6. [How to Add a New Reader](#how-to-add-a-new-reader)
7. [How to Add a New Chunker](#how-to-add-a-new-chunker)
8. [The Config System](#the-config-system)
9. [WebSocket Protocol](#websocket-protocol)
10. [Running Locally for Development](#running-locally-for-development)
11. [API Reference](#api-reference)

---

## Architecture Overview

### Component Plugin System

Verba uses a simple plugin architecture. Five component categories exist; each category has a manager class that holds a dict of registered instances. The frontend reads available components via REST, the user picks one, and its config is serialised into every subsequent request.

```
+----------------------------------------------------------+
|                        Frontend (Next.js)                |
|  - Picks Reader / Chunker / Embedder / Retriever /       |
|    Generator from dropdowns populated by /api/health     |
|    and /api/get_rag_config                               |
+---------------------------+------------------------------+
                            | REST + WebSocket
+---------------------------v------------------------------+
|                 FastAPI  (goldenverba/server/api.py)      |
|                                                          |
|  VerbaManager                                            |
|  +----------------+  +----------------+                  |
|  | ReaderManager  |  | ChunkerManager |                  |
|  +----------------+  +----------------+                  |
|  +------------------+  +------------------+              |
|  | EmbeddingManager |  | RetrieverManager |              |
|  +------------------+  +------------------+              |
|  +------------------+                                    |
|  | GeneratorManager |                                    |
|  +------------------+                                    |
|                                                          |
|  WeaviateManager  (all Weaviate I/O lives here)          |
+---------------------------+------------------------------+
                            |
+---------------------------v------------------------------+
|                      Weaviate                            |
|  Collections: VERBA_DOCUMENTS, VERBA_CONFIGURATION,      |
|               VERBA_SUGGESTIONS                          |
+----------------------------------------------------------+
```

### The Five Component Types

| Type | Base class | Purpose |
|---|---|---|
| Reader | `Reader` | Turn a file/URL upload into `Document` objects |
| Chunker | `Chunker` | Split `Document` objects into `Chunk` objects |
| Embedder | `Embedding` | Vectorise each chunk's text into `list[float]` |
| Retriever | `Retriever` | Query Weaviate and build the context string |
| Generator | `Generator` | Stream an LLM response token by token |

### Full Data Flow: File Upload to Streamed Answer

```
Browser uploads file
        |
        v
[WebSocket /ws/import_files]
        |
  BatchManager reassembles chunks into FileConfig
        |
        v
VerbaManager.import_document(client, fileConfig)
        |
        +--- ReaderManager.load()          --> list[Document]
        |    (calls Reader.load())
        |
        +--- ChunkerManager.chunk()        --> list[Document] with .chunks filled
        |    (calls Chunker.chunk())
        |
        +--- EmbeddingManager.vectorize()  --> list[Document] with chunk.vector filled
        |    (calls Embedding.vectorize()  in batches of max_batch_size)
        |    also computes PCA(3) for 3-D visualisation
        |
        +--- WeaviateManager.import_document()
             stores Document + Chunks in VERBA_DOCUMENTS collection

------- query time -------

Browser sends query text
        |
        v
[POST /api/query]
        |
  VerbaManager.retrieve_chunks()
        |
        +--- EmbeddingManager.vectorize_query()   --> query vector
        |
        +--- RetrieverManager.retrieve()           --> (documents, context_str)
             (Retriever hits Weaviate with vector + filters)
        |
        v
[WebSocket /ws/generate_stream]
        |
  GeneratorManager.generate_stream()
        |
  Generator.generate_stream()   -- async generator
        |
  yields {"message": "<token>", "finish_reason": None | "stop"}
        |
  WebSocket sends each dict to the browser in real time
```

### Production vs Local Mode

The `VERBA_PRODUCTION` environment variable controls which component lists are instantiated at startup (`goldenverba/components/managers.py`, lines 85-164).

| Value | Effect |
|---|---|
| unset / anything else | "Local" mode — all components including Ollama, SentenceTransformers |
| `"Production"` | Slimmer list; Ollama and SentenceTransformers are excluded |
| `"Demo"` | Same component list as Production but write endpoints return early |

The `production` string is exposed to the frontend via `GET /api/health` so the UI can hide destructive actions.

---

## Project Structure

```
Verba/
├── goldenverba/                   # Entire Python package
│   ├── __init__.py
│   ├── verba_manager.py           # VerbaManager + ClientManager — the orchestration layer
│   ├── components/
│   │   ├── interfaces.py          # Abstract base classes (Reader, Chunker, Embedding, Retriever, Generator)
│   │   ├── managers.py            # Manager classes + component registration lists
│   │   ├── types.py               # InputConfig Pydantic model
│   │   ├── util.py                # get_environment(), get_token() helpers
│   │   ├── document.py            # Document dataclass
│   │   ├── chunk.py               # Chunk dataclass
│   │   ├── reader/                # One file per Reader implementation
│   │   │   ├── BasicReader.py     # Default: txt, pdf, docx, csv, xlsx, …
│   │   │   ├── GitReader.py       # Clones a Git repo and reads files
│   │   │   ├── HTMLReader.py      # Fetches a URL and strips HTML
│   │   │   ├── FirecrawlReader.py # Firecrawl-based web reader
│   │   │   ├── UnstructuredAPI.py # Unstructured.io API reader
│   │   │   ├── AssemblyAIAPI.py   # AssemblyAI transcription reader
│   │   │   └── UpstageDocumentParse.py
│   │   ├── chunking/              # One file per Chunker implementation
│   │   │   ├── TokenChunker.py    # Token-count window with overlap
│   │   │   ├── SentenceChunker.py
│   │   │   ├── RecursiveChunker.py
│   │   │   ├── SemanticChunker.py # Embedding-aware chunker
│   │   │   ├── MarkdownChunker.py
│   │   │   ├── HTMLChunker.py
│   │   │   ├── CodeChunker.py
│   │   │   └── JSONChunker.py
│   │   ├── embedding/             # One file per Embedder implementation
│   │   │   ├── OpenAIEmbedder.py
│   │   │   ├── CohereEmbedder.py
│   │   │   ├── OllamaEmbedder.py
│   │   │   ├── WeaviateEmbedder.py
│   │   │   ├── VoyageAIEmbedder.py
│   │   │   ├── SentenceTransformersEmbedder.py
│   │   │   ├── UpstageEmbedder.py
│   │   │   └── LMStudioEmbedder.py
│   │   ├── generation/            # One file per Generator implementation
│   │   │   ├── OpenAIGenerator.py
│   │   │   ├── AnthrophicGenerator.py
│   │   │   ├── CohereGenerator.py
│   │   │   ├── OllamaGenerator.py
│   │   │   ├── GroqGenerator.py
│   │   │   ├── NovitaGenerator.py
│   │   │   ├── DeepSeekGenerator.py
│   │   │   ├── UpstageGenerator.py
│   │   │   └── LMStudioGenerator.py
│   │   └── retriever/
│   │       └── WindowRetriever.py # Default retriever (window expansion)
│   ├── server/
│   │   ├── api.py                 # FastAPI app, all endpoints, WebSocket handlers
│   │   ├── types.py               # Pydantic request/response models
│   │   ├── helpers.py             # LoggerManager, BatchManager
│   │   ├── cli.py                 # `verba start` / `verba reset` Click commands
│   │   └── frontend/out/          # Pre-built Next.js static files (served by FastAPI)
│   └── tests/
│       ├── document/
│       ├── chunk/
│       └── components/
├── frontend/                      # Next.js source (separate dev server in development)
├── setup.py                       # Package metadata + dependencies
├── requirements.txt               # (mirror of setup.py install_requires)
└── .env                           # Local secrets (never committed)
```

---

## The Component Plugin System

### Base Classes (`goldenverba/components/interfaces.py`)

Every component inherits from `VerbaComponent`:

```python
class VerbaComponent:
    def __init__(self):
        self.name = ""              # Unique display name (used as dict key)
        self.requires_env = []      # Env vars that must be set for availability
        self.requires_library = []  # Python packages that must be importable
        self.description = ""       # Shown in the UI
        self.config = {}            # Dict[str, InputConfig] — UI-configurable fields
        self.type = ""              # Internal type tag
```

`get_meta()` serialises the component into the dict that the frontend consumes. It calls `check_available()` which checks `requires_env` against current environment variables and `requires_library` against installed packages.

### InputConfig — Configurable UI Fields (`goldenverba/components/types.py`)

```python
class InputConfig(BaseModel):
    type: Literal["number", "text", "dropdown", "password", "bool", "multi", "textarea"]
    value: Union[int, str, bool]   # Current (or default) value
    description: str               # Help text shown below the field
    values: list[str]              # Options — only used when type == "dropdown" or "multi"
```

Each key in `self.config` becomes a labelled input in the UI. The frontend sends the complete config dict back with every request so components always receive whatever the user last set.

| `type` value | Rendered as | When to use |
|---|---|---|
| `"text"` | Single-line text box | Base URL, model name overrides |
| `"password"` | Masked input | API keys that are not in env |
| `"number"` | Numeric spinner | Token counts, temperature |
| `"dropdown"` | Select menu | Model selection (populate `values` list) |
| `"bool"` | Toggle | Feature flags |
| `"textarea"` | Multi-line text | System prompts |
| `"multi"` | Multi-select | Tag-style multi-value fields |

### How `get_meta()` Works

`VerbaManager` calls `get_meta(envs, libs)` on every registered component at connect time to build the `RAGConfig` that is returned to the frontend. `envs` is a snapshot of `os.environ` and `libs` is a dict of `{package_name: bool}` built by `VerbaManager.verify_installed_libraries()`.

A component with `requires_env = ["OPENAI_API_KEY"]` will have `"available": false` in the UI unless that variable is set, preventing the user from selecting an unusable component.

### How Components Are Registered (`goldenverba/components/managers.py`)

At module load time the file builds two sets of plain Python lists (one for local mode, one for production mode) and then the manager classes wrap them:

```python
# managers.py (simplified)
production = os.getenv("VERBA_PRODUCTION")
if production != "Production":
    generators = [
        OllamaGenerator(),
        OpenAIGenerator(),
        AnthropicGenerator(),
        # ...
    ]
else:
    generators = [
        OpenAIGenerator(),
        AnthropicGenerator(),
        # ...
    ]

class GeneratorManager:
    def __init__(self):
        self.generators: dict[str, Generator] = {
            g.name: g for g in generators
        }
```

To add a new component you: create the class file, import it at the top of `managers.py`, and append an instance to both lists.

---

## How to Add a New Generator

This walkthrough adds a fictional "Mistral" generator backed by the Mistral AI chat completions API.

### Step 1 — Create the file

```
goldenverba/components/generation/MistralGenerator.py
```

### Step 2 — Write the class

```python
import os
import json
import httpx
from goldenverba.components.interfaces import Generator
from goldenverba.components.types import InputConfig
from goldenverba.components.util import get_environment, get_token

class MistralGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.name = "Mistral"                                   # Must be unique
        self.description = "Mistral AI chat completions"
        self.context_window = 32000

        # Offer a model dropdown. Fallback to a static list if no key yet.
        api_key = get_token("MISTRAL_API_KEY")
        models = self._fetch_models(api_key) if api_key else ["mistral-small", "mistral-large-latest"]
        default_model = os.getenv("MISTRAL_MODEL", models[0])

        self.config["Model"] = InputConfig(
            type="dropdown",
            value=default_model,
            description="Select a Mistral model",
            values=models,
        )

        # Only show the API key field if the env var is not already set.
        if api_key is None:
            self.config["API Key"] = InputConfig(
                type="password",
                value="",
                description="Mistral API key — or set MISTRAL_API_KEY env var",
                values=[],
            )

    async def generate_stream(self, config: dict, query: str, context: str, conversation: list[dict] = []):
        model = config["Model"].value
        api_key = get_environment(config, "API Key", "MISTRAL_API_KEY", "No Mistral API key found")
        system_message = config["System Message"].value   # inherited from Generator base class

        messages = self.prepare_messages(query, context, conversation, system_message)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        body = {"model": model, "messages": messages, "stream": True}

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                "https://api.mistral.ai/v1/chat/completions",
                json=body,
                headers=headers,
                timeout=None,
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        if line.strip() == "data: [DONE]":
                            break
                        data = json.loads(line[6:])
                        choice = data["choices"][0]
                        delta = choice.get("delta", {})
                        if "content" in delta:
                            yield {"message": delta["content"], "finish_reason": choice.get("finish_reason")}
                        elif choice.get("finish_reason"):
                            yield {"message": "", "finish_reason": choice["finish_reason"]}

    def prepare_messages(self, query: str, context: str, conversation: list[dict], system_message: str) -> list[dict]:
        messages = [{"role": "system", "content": system_message}]
        for msg in conversation:
            messages.append({"role": msg.type, "content": msg.content})
        messages.append({"role": "user", "content": f"Answer this query: '{query}' with this context: {context}"})
        return messages

    def _fetch_models(self, api_key: str) -> list[str]:
        try:
            import requests
            r = requests.get("https://api.mistral.ai/v1/models", headers={"Authorization": f"Bearer {api_key}"})
            r.raise_for_status()
            return [m["id"] for m in r.json()["data"]]
        except Exception:
            return ["mistral-small", "mistral-large-latest"]
```

### Step 3 — Register in `managers.py`

Open `goldenverba/components/managers.py` and add two lines:

```python
# At the top with the other generator imports:
from goldenverba.components.generation.MistralGenerator import MistralGenerator

# In BOTH the local and production generator lists:
generators = [
    OllamaGenerator(),
    OpenAIGenerator(),
    MistralGenerator(),   # <-- add here
    ...
]
```

### Step 4 — Add environment variable documentation

Document the new variable in your PR description and, if relevant, in `.env.example`:

```
MISTRAL_API_KEY=your-key-here
MISTRAL_MODEL=mistral-large-latest   # optional
```

### Key rules for `generate_stream`

- It must be an `async` generator (use `yield`, not `return`).
- Every yielded dict must have exactly two keys: `"message"` (str) and `"finish_reason"` (str or `None`).
- Signal end-of-stream by yielding `{"message": "", "finish_reason": "stop"}`.
- Never raise inside the generator after streaming has begun — send a terminal chunk instead.
- `config` is a `dict[str, InputConfig]`. Access values with `config["Key"].value`.

### `get_environment` vs `get_token`

```python
from goldenverba.components.util import get_environment, get_token

# get_token: reads ONLY from os.environ, returns None if missing/empty
api_key = get_token("MISTRAL_API_KEY")          # use in __init__ to check availability

# get_environment: checks config dict first, then falls back to env var, raises if neither found
api_key = get_environment(config, "API Key", "MISTRAL_API_KEY", "No Mistral API key")
# use in generate_stream / vectorize where config is available
```

The pattern — check with `get_token` in `__init__` to decide whether to show the password field, then resolve with `get_environment` at call time — means users can either set an env var before starting Verba or paste the key directly into the UI.

---

## How to Add a New Embedder

This walkthrough adds a fictional "VoyageMini" embedder.

### Step 1 — Create the file

```
goldenverba/components/embedding/VoyageMiniEmbedder.py
```

### Step 2 — Write the class

```python
import aiohttp
from goldenverba.components.interfaces import Embedding
from goldenverba.components.types import InputConfig
from goldenverba.components.util import get_environment, get_token

class VoyageMiniEmbedder(Embedding):
    def __init__(self):
        super().__init__()
        self.name = "VoyageMini"
        self.description = "Voyage AI mini embedding model"
        self.max_batch_size = 64          # Voyage mini accepts up to 128, set conservatively

        self.config["Model"] = InputConfig(
            type="dropdown",
            value="voyage-3-lite",
            description="Voyage embedding model",
            values=["voyage-3-lite", "voyage-3"],
        )

        if get_token("VOYAGE_API_KEY") is None:
            self.config["API Key"] = InputConfig(
                type="password",
                value="",
                description="Voyage AI API key — or set VOYAGE_API_KEY env var",
                values=[],
            )

    async def vectorize(self, config: dict, content: list[str]) -> list[list[float]]:
        """
        Receives a batch of strings (already split by EmbeddingManager based on
        self.max_batch_size) and returns one embedding vector per string.
        """
        model = config["Model"].value
        api_key = get_environment(config, "API Key", "VOYAGE_API_KEY", "No Voyage API key found")

        payload = {"input": content, "model": model}
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.voyageai.com/v1/embeddings",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=60),
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return [item["embedding"] for item in data["data"]]
```

### Step 3 — Register in `managers.py`

```python
from goldenverba.components.embedding.VoyageMiniEmbedder import VoyageMiniEmbedder

embedders = [
    ...,
    VoyageMiniEmbedder(),   # <-- add here
]
```

### Embedder contract

- `vectorize(config, content)` receives a **batch** of strings (at most `self.max_batch_size` items).
- It must return `list[list[float]]` — one inner list per input string, all the same length.
- `EmbeddingManager` calls `vectorize` in parallel for each batch via `asyncio.gather`, then flattens and verifies counts.
- Set `self.max_batch_size` to the largest batch the upstream API accepts reliably.

---

## How to Add a New Reader

### Step 1 — Create the file

```
goldenverba/components/reader/MyReader.py
```

### Step 2 — Write the class

```python
import base64
from goldenverba.components.interfaces import Reader
from goldenverba.components.document import create_document
from goldenverba.server.types import FileConfig

class MyReader(Reader):
    def __init__(self):
        super().__init__()
        self.name = "MyReader"
        self.description = "Reads .xyz files"
        self.type = "FILE"                          # "FILE" or "URL"
        self.extension = [".xyz"]                   # Accepted extensions shown in UI

    async def load(self, config: dict, fileConfig: FileConfig) -> list[Document]:
        """
        Receives the FileConfig sent by the frontend.
        fileConfig.content is base64-encoded file bytes when fileConfig.isURL is False.
        Must return a list of Document objects.
        """
        raw = base64.b64decode(fileConfig.content)
        text = raw.decode("utf-8")

        # create_document is a convenience helper that populates all required fields
        return [create_document(text, fileConfig)]
```

### `FileConfig` fields relevant to readers

| Field | Type | Description |
|---|---|---|
| `filename` | `str` | Original filename |
| `extension` | `str` | File extension without leading dot |
| `content` | `str` | Base64-encoded file bytes (or raw URL string when `isURL=True`) |
| `isURL` | `bool` | True when the source is a URL rather than an uploaded file |
| `labels` | `list[str]` | User-supplied labels to attach to the document |
| `metadata` | `str` | Free-form JSON string for extra metadata |
| `overwrite` | `bool` | Whether to replace an existing document with the same name |
| `rag_config` | `dict` | Full RAG config including the reader's own config fields |

### Returning multiple documents

Readers may return more than one `Document` from a single file (e.g. a zip archive or a URL that fans out to multiple pages). When more than one document is returned, `VerbaManager` processes each concurrently via `asyncio.gather`.

### Step 3 — Register in `managers.py`

```python
from goldenverba.components.reader.MyReader import MyReader

readers = [
    BasicReader(),
    MyReader(),    # <-- add here
    ...
]
```

---

## How to Add a New Chunker

### Step 1 — Create the file

```
goldenverba/components/chunking/MyChunker.py
```

### Step 2 — Write the class

```python
from goldenverba.components.interfaces import Chunker, Embedding
from goldenverba.components.chunk import Chunk
from goldenverba.components.document import Document
from goldenverba.components.types import InputConfig

class MyChunker(Chunker):
    def __init__(self):
        super().__init__()
        self.name = "MyChunker"
        self.description = "Splits on paragraph boundaries"
        self.config["Max Paragraphs"] = InputConfig(
            type="number",
            value=3,
            description="Maximum paragraphs per chunk",
            values=[],
        )

    async def chunk(
        self,
        config: dict,
        documents: list[Document],
        embedder: Embedding | None = None,
        embedder_config: dict | None = None,
    ) -> list[Document]:
        max_p = int(config["Max Paragraphs"].value)

        for doc in documents:
            if doc.chunks:          # skip already-chunked documents
                continue
            paragraphs = doc.content.split("\n\n")
            groups = [paragraphs[i:i+max_p] for i in range(0, len(paragraphs), max_p)]
            for idx, group in enumerate(groups):
                text = "\n\n".join(group)
                doc.chunks.append(Chunk(
                    content=text,
                    chunk_id=idx,
                    start_i=0,
                    end_i=len(text),
                    content_without_overlap=text,
                ))
        return documents
```

### Chunker contract

- Receives a list of `Document` objects that already have `doc.content` and `doc.spacy_doc` populated.
- Must populate `doc.chunks` with `Chunk` instances.
- Skip documents that already have chunks (`if doc.chunks: continue`).
- `embedder` and `embedder_config` are only provided when the chunker needs to call the embedder itself (e.g. `SemanticChunker` uses them to split on embedding similarity boundaries). Most chunkers ignore them.
- Returns the same list of documents (mutated in-place is fine, or return new list).

### Step 3 — Register in `managers.py`

```python
from goldenverba.components.chunking.MyChunker import MyChunker

chunkers = [
    TokenChunker(),
    MyChunker(),    # <-- add here
    ...
]
```

---

## The Config System

### Where Config Lives

RAG configuration is persisted in the `VERBA_CONFIGURATION` Weaviate collection as a JSON blob under a fixed UUID (`VerbaManager.rag_config_uuid`). When a client connects, `VerbaManager.load_rag_config()` reads this blob and merges it with the current component definitions to produce the full `RAGConfig` sent to the frontend.

### Config Shape

The frontend always works with a `RAGConfig` object:

```
RAGConfig
  Reader:    RAGComponentClass   { selected: "Default",  components: { "Default": RAGComponentConfig, ... } }
  Chunker:   RAGComponentClass   { selected: "Token",    components: { ... } }
  Embedder:  RAGComponentClass   { selected: "OpenAI",   components: { ... } }
  Retriever: RAGComponentClass   { selected: "Window",   components: { ... } }
  Generator: RAGComponentClass   { selected: "OpenAI",   components: { ... } }
```

Each `RAGComponentConfig` carries the component's `config` dict (key → `ConfigSetting`). The `ConfigSetting` type mirrors `InputConfig` exactly — when the user edits a field and saves, the new `value` is written back into this structure and persisted via `POST /api/set_rag_config`.

### How Config Is Passed to Components

Every manager method extracts the config before calling the component:

```python
# ChunkerManager.chunk() — typical pattern
config = fileConfig.rag_config["Chunker"].components[chunker].config
await self.chunkers[chunker].chunk(config=config, documents=documents, ...)
```

Inside a component, read values with `config["Key"].value`. The value is whatever the user last set in the UI, or the default you put in `__init__`.

### Config Fields Added Conditionally

The standard pattern is to omit a config field if the corresponding env var is already set. This keeps the UI clean for users who configure via env vars:

```python
if get_token("MY_API_KEY") is None:
    self.config["API Key"] = InputConfig(type="password", ...)
```

If the env var is set, the field never appears and `get_environment(config, "API Key", "MY_API_KEY", "...")` will fall through to reading the env var directly.

---

## WebSocket Protocol

### `/ws/generate_stream` — Streaming Generation

**Client sends** (JSON text frame, validated against `GeneratePayload`):
```json
{
  "query": "What is RAG?",
  "context": "RAG stands for...",
  "conversation": [
    {"type": "user", "content": "Hello"},
    {"type": "assistant", "content": "Hi there!"}
  ],
  "rag_config": { <full RAGConfig object> }
}
```

**Server yields** (one JSON text frame per token):
```json
{"message": "Retrieval", "finish_reason": null}
{"message": "-", "finish_reason": null}
{"message": "Augmented", "finish_reason": null}
{"message": " Generation", "finish_reason": null}
{"message": "", "finish_reason": "stop", "full_text": "Retrieval-Augmented Generation"}
```

The final frame where `finish_reason == "stop"` also carries `full_text` (the entire concatenated response). On error the server sends `{"message": "<error text>", "finish_reason": "stop", "full_text": "<error text>"}`.

The connection stays open after each exchange so the user can send a follow-up query without reconnecting.

### `/ws/import_files` — Batch File Upload

Large `FileConfig` objects are split into chunks by the frontend before sending. The `BatchManager` on the server side reassembles them.

**Client sends** (one frame per batch, validated against `DataBatchPayload`):
```json
{
  "chunk": "<base64 or JSON fragment>",
  "isLastChunk": false,
  "total": 3,
  "fileID": "abc-123",
  "order": 0,
  "credentials": {"deployment": "Local", "url": "", "key": ""}
}
```

Fields:
- `total` — total number of chunks for this file transfer.
- `order` — 0-indexed position of this chunk.
- `isLastChunk` — when true and the batch is not yet complete, the BatchManager cleans up regardless (handles partial failures).
- `fileID` — unique identifier for this file upload session.

**Server sends** (status frames via `LoggerManager`):
```json
{"fileID": "abc-123", "status": "LOADING",   "message": "Loaded document.pdf", "took": 0.12}
{"fileID": "abc-123", "status": "CHUNKING",  "message": "Split into 47 chunks", "took": 0.44}
{"fileID": "abc-123", "status": "EMBEDDING", "message": "Vectorized all chunks", "took": 3.21}
{"fileID": "abc-123", "status": "INGESTING", "message": "Imported into Weaviate", "took": 0.8}
{"fileID": "abc-123", "status": "DONE",      "message": "Import completed successfully", "took": 4.6}
```

On failure: `{"fileID": "...", "status": "ERROR", "message": "<error details>", "took": 0}`.

Full status lifecycle: `READY → STARTING → LOADING → CHUNKING → EMBEDDING → INGESTING → DONE` (or `ERROR`).

When a Reader returns multiple documents (e.g. a URL reader that fans out), the server sends a `CreateNewDocument` frame so the UI can track each sub-document separately:
```json
{"new_file_id": "abc-123<title>", "filename": "page-title", "original_file_id": "abc-123"}
```

---

## Running Locally for Development

### Prerequisites

- Python 3.10, 3.11, or 3.12 (3.13+ is not supported)
- Node.js 18+ (only needed if modifying the frontend)
- A running Weaviate instance (Local embedded, Docker, or Weaviate Cloud)

### Python Environment

```bash
# Clone and create a virtual environment
git clone https://github.com/weaviate/Verba.git
cd Verba
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# Install in editable mode with dev extras
pip install -e ".[dev]"

# Install the spaCy model required by BasicReader / TokenChunker
python -m spacy download en_core_web_sm
```

### Environment Variables

Create a `.env` file in the project root (or export these in your shell):

```bash
# Weaviate connection — omit for local embedded mode
WEAVIATE_URL_VERBA=https://your-cluster.weaviate.network
WEAVIATE_API_KEY_VERBA=your-weaviate-key

# API keys for providers you want to test
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Optional: pre-select a model
OPENAI_MODEL=gpt-4o
OPENAI_EMBED_MODEL=text-embedding-3-small

# Optional: override system prompt
SYSYEM_MESSAGE_PROMPT="You are a helpful assistant."

# Optional: run in production component set (omit Ollama/SentenceTransformers)
# VERBA_PRODUCTION=Production
```

### Running the Backend Only

```bash
verba start --port 8000 --host localhost
# or equivalently:
python -m goldenverba.server.cli start --port 8000
```

With `--no-prod` (the default) uvicorn starts with `reload=True` so the server restarts on any Python file change. Access the bundled frontend at `http://localhost:8000`.

### Running the Frontend Separately (for UI development)

```bash
# Terminal 1 — backend (disable reload to avoid conflicts)
verba start --port 8000 --prod

# Terminal 2 — frontend dev server
cd frontend
npm install
npm run dev      # starts Next.js on http://localhost:3000
```

The Next.js dev server proxies API calls to port 8000 (configured in `frontend/next.config.js`).

### Resetting Weaviate Collections

```bash
# Reset only config (keeps documents)
verba reset --deployment Local

# Full wipe of all collections
verba reset --deployment Local --full_reset True

# Against a Weaviate Cloud cluster
verba reset --url https://my-cluster.weaviate.network --api_key <key> --deployment Weaviate
```

### Running Tests

```bash
pytest goldenverba/tests -v
```

Tests are currently sparse. When adding a new component, consider adding a test in `goldenverba/tests/components/`.

### Code Style

Format with Black before submitting a PR:

```bash
black goldenverba/
```

---

## API Reference

All endpoints accept and return JSON. Every endpoint except `/api/health` requires an `Origin` header matching the server's base URL (same-origin middleware). Credentials are embedded in request bodies rather than headers.

### Health and Connection

| Method | Path | Request body | Response |
|---|---|---|---|
| `GET` | `/api/health` | — | `{message, production, gtag, deployments, default_deployment}` |
| `POST` | `/api/connect` | `ConnectPayload {credentials, port}` | `{connected, error, rag_config, user_config, theme, themes}` |

### Configuration

| Method | Path | Request body | Response |
|---|---|---|---|
| `POST` | `/api/get_rag_config` | `Credentials` | `{rag_config, error}` |
| `POST` | `/api/set_rag_config` | `SetRAGConfigPayload {rag_config, credentials}` | `{status}` |
| `POST` | `/api/get_user_config` | `Credentials` | `{user_config, error}` |
| `POST` | `/api/set_user_config` | `SetUserConfigPayload {user_config, credentials}` | `{status, status_msg}` |
| `POST` | `/api/get_theme_config` | `Credentials` | `{theme, themes, error}` |
| `POST` | `/api/set_theme_config` | `SetThemeConfigPayload {theme, themes, credentials}` | `{status}` |

### RAG / Query

| Method | Path | Request body | Response |
|---|---|---|---|
| `POST` | `/api/query` | `QueryPayload {query, RAG, labels, documentFilter, credentials}` | `{error, documents, context}` |

### Documents

| Method | Path | Request body | Response |
|---|---|---|---|
| `POST` | `/api/get_document` | `GetDocumentPayload {uuid, credentials}` | `{error, document}` |
| `POST` | `/api/get_all_documents` | `SearchQueryPayload {query, labels, page, pageSize, credentials}` | `{documents, labels, error, totalDocuments}` |
| `POST` | `/api/delete_document` | `GetDocumentPayload {uuid, credentials}` | `{}` |
| `POST` | `/api/get_datacount` | `DatacountPayload {embedding_model, documentFilter, credentials}` | `{datacount}` |
| `POST` | `/api/get_labels` | `Credentials` | `{labels}` |
| `POST` | `/api/get_content` | `GetContentPayload {uuid, page, chunkScores, credentials}` | `{error, content, maxPage}` |
| `POST` | `/api/get_chunks` | `ChunksPayload {uuid, page, pageSize, credentials}` | `{error, chunks}` |
| `POST` | `/api/get_chunk` | `GetChunkPayload {uuid, embedder, credentials}` | `{error, chunk}` |
| `POST` | `/api/get_vectors` | `GetVectorPayload {uuid, showAll, credentials}` | `{error, vector_groups}` |

### Suggestions

| Method | Path | Request body | Response |
|---|---|---|---|
| `POST` | `/api/get_suggestions` | `GetSuggestionsPayload {query, limit, credentials}` | `{suggestions}` |
| `POST` | `/api/get_all_suggestions` | `GetAllSuggestionsPayload {page, pageSize, credentials}` | `{suggestions}` |
| `POST` | `/api/delete_suggestion` | `DeleteSuggestionPayload {uuid, credentials}` | `{}` |

### Admin

| Method | Path | Request body | Response |
|---|---|---|---|
| `POST` | `/api/reset` | `ResetPayload {resetMode, credentials}` | `{}` (resetMode: `"ALL"` \| `"DOCUMENTS"` \| `"CONFIG"` \| `"SUGGESTIONS"`) |
| `POST` | `/api/get_meta` | `Credentials` | `{error, node_payload, collection_payload}` |

### WebSockets

| Path | Direction | Description |
|---|---|---|
| `/ws/generate_stream` | Bidirectional, persistent | Send `GeneratePayload`, receive token stream |
| `/ws/import_files` | Bidirectional, persistent | Send `DataBatchPayload` chunks, receive `StatusReport` frames |

### Static Assets

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Serves `frontend/out/index.html` |
| `GET` | `/static/_next/*` | Next.js JS/CSS bundles |
| `GET` | `/static/*` | Other static files from the Next.js build |

---

## Quick-Start Checklist for a New Generator

```
[ ] Create goldenverba/components/generation/MyGenerator.py
[ ] Class inherits from Generator
[ ] Set self.name to a unique string
[ ] Set self.description
[ ] Optionally set self.context_window
[ ] Add InputConfig entries to self.config (Model dropdown, API Key password if needed)
[ ] Implement async generate_stream(self, config, query, context, conversation)
      - Must be an async generator (yield dicts)
      - Yield {"message": str, "finish_reason": None | "stop"}
      - Final yield must have finish_reason == "stop"
[ ] Implement prepare_messages() if needed
[ ] Use get_token() in __init__ and get_environment() in generate_stream
[ ] Add import to managers.py
[ ] Add instance to BOTH local and production generator lists in managers.py
[ ] Document env vars in PR description
[ ] Run: verba start and verify the generator appears in the UI dropdown
[ ] Run: pytest goldenverba/tests
[ ] Run: black goldenverba/
```
