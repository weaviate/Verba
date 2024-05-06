# Verba: The Golden RAGtriever Technical Documentation

This document provides an overview of the general modular architecture of Verba.

![Demo of Verba](https://github.com/weaviate/Verba/blob/dev/img/verba_architecture.png)

## System Architecture

Verba's system is modularly constructed, comprising five primary components: Reader, Chunkers, Embedder, Retrievers, and Generators. Each component is designed with an interface outlining its methods, input expectations, and output specifications. Component Managers oversee the operations of their respective components, ensuring smooth data flow through the system. At the core of the architecture is the Verba Manager, orchestrating the entire process from data input to answer generation.

### 1. Reader

**Purpose:**
The Reader module is responsible for loading various data formats into the Verba system.

**Input: List[FileData]**

```python

class FileData(BaseModel):
    filename: str
    extension: str
    content: str

```

**Output: List[Document]**

```python

class Document:
    def __init__(
        self,
        text: str = "",
        type: str = "",
        name: str = "",
        path: str = "",
        link: str = "",
        timestamp: str = "",
        reader: str = "",
        meta: dict = None,
    ):
        if meta is None:
            meta = {}
        self._text = text
        self._type = type
        self._name = name
        self._path = path
        self._link = link
        self._timestamp = timestamp
        self._reader = reader
        self._meta = meta
        self.chunks: list[Chunk] = []

```

### 2. Chunkers

**Purpose:**
Chunkers segment larger documents into smaller, manageable chunks suitable for vectorization and retrieval.

**Input & Output: List[Document]**

```python

class Chunk:
    def __init__(
        self,
        text: str = "",
        doc_name: str = "",
        doc_type: str = "",
        doc_uuid: str = "",
        chunk_id: str = "",
    ):
        self._text = text
        self._doc_name = doc_name
        self._doc_type = doc_type
        self._doc_uuid = doc_uuid
        self._chunk_id = chunk_id
        self._tokens = 0
        self._vector = None
        self._score = 0

```

> The Document Class contains a list of chunks, the Chunker will append the chunks into that list. It will skip chunking if the document already contains chunks.

### 3. Embedders

**Purpose:**
The Embedder takes the chunked data, transforms it into vectorized form, and ingests it into Weaviate.

**Input: List[Document]**

### 4. Retrievers

**Purpose:**
Retrievers are tasked with locating the most relevant chunks based on user queries using vector search methodologies.

**Output: List[Chunk]**

### 5. Generators

**Purpose:**
Generators synthesize answers by utilizing the retrieved chunks and the context of user queries.

**Input: str**
**Output: str**

## Core Component: Verba Manager

### Overview

The Verba Manager is the heart of the system, holding all Component Managers and facilitating the data flow from reading to answer generation.

### Interaction with FastAPI

The FastAPI application serves as the interface to the frontend and interacts solely with the Verba Manager.
This encapsulation ensures a clean and maintainable codebase where the API endpoints communicate with a single point of reference within the Verba ecosystem.
