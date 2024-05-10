# Verba: The Golden RAGtriever Technical Documentation

## Introduction
This document provides a comprehensive overview of the technical architecture and implementation details of Verba. Verba is an open-source application engineered to leverage the capabilities of Retrieval-Augmented Generation (RAG) through a user-friendly interface. It is designed to work seamlessly with Weaviate's context-aware database and various Large Language Model (LLM) providers, offering advanced data interaction and query resolution features. Below is a detailed examination of Verba's modular components and their interactions.

![Demo of Verba](https://github.com/weaviate/Verba/blob/dev/img/verba_architecture.png)

## System Architecture
Verba's system is modularly constructed, comprising five primary components: Reader, Chunkers, Embedder, Retrievers, and Generators. Each component is designed with an interface outlining its methods, input expectations, and output specifications. Component Managers oversee the operations of their respective components, ensuring smooth data flow through the system. At the core of the architecture is the Verba Manager, orchestrating the entire process from data input to answer generation.

### 1. Reader
**Purpose:**
The Reader module is responsible for loading various data formats into the Verba system.

**Implementation:**
- Reader Manager: Manages different readers and maintains the current reader in use.
    - SimpleReader: Loads text and markdown files.
    - GithubReader: Downloads and processes text from GitHub repositories.
    - PDFReader: Imports and processes data from PDF files.

### 2. Chunkers
**Purpose:**
Chunkers segment larger documents into smaller, manageable chunks suitable for vectorization and retrieval.

**Implementation:**
- Chunker Manager: Controls the available chunking strategies and selects the appropriate chunker as needed.
    - WordChunker: Creates chunk of documents based on words 
    - SentenceChunker: Creates chunk of documents based on sentences 

### 3. Embedders
**Purpose:**
The Embedder takes the chunked data, transforms it into vectorized form, and ingests it into Weaviate.

**Implementation:**
- Embedder Manager: Manages the embedding process and the selection of the current embedding strategy.
    - ADAEmbedder: Embeds chunks based on OpenAI's ADA Model
    - MiniLMEmbedder: Embeds chunks based on Sentence Transformer
    - AllMPNetEmbedder: Embeds chunks based on Sentence Transformer
    - MixedbreadEmbedder: Embeds chunks based on Sentence Transformer
    - CohereEmbedder: Embeds chunks based on Cohere's Embedding Model

### 4. Retrievers
**Purpose:**
Retrievers are tasked with locating the most relevant chunks based on user queries using vector search methodologies.

**Implementation:**
- Retriever Manager: Oversees the retriever components and their retrieval strategies.
    - WindowRetriever: Retrieves chunks using hybrid search and adds surrounding context of chunks
    - SimpleRetriever: Retrieves chunks using hybrid search only

### 5. Generators
**Purpose:**
Generators synthesize answers by utilizing the retrieved chunks and the context of user queries.

**Implementation:**
- Generator Manager: Manages different generation strategies and maintains the currently selected generator.
    - GPT3Generator: Uses OpenAI's GPT3 model to generate responses
    - GPT4Generator: Uses OpenAI's GPT4 model to generate responses
    - CohereGenerator: Uses Cohere to generate responses
    - Llama2Generator: Uses Meta's Llama2 to generate responses

## Core Component: Verba Manager
### Overview
The Verba Manager is the heart of the system, holding all Component Managers and facilitating the data flow from reading to answer generation.

### Interaction with FastAPI
The FastAPI application serves as the interface to the frontend and interacts solely with the Verba Manager.
This encapsulation ensures a clean and maintainable codebase where the API endpoints communicate with a single point of reference within the Verba ecosystem.

## Data Flow Process
1. Data Ingestion: The selected Reader loads the data into the system.
2. Chunking: The chosen Chunker segments the data into smaller parts.
3. Vectorization: The Embedder transforms these chunks into vector representations.
4. Retrieval: Based on a user's query, the Retriever identifies the most relevant data chunks.
5. Answer Generation: The Generator composes an answer leveraging both the retrieved chunks and the contextual understanding of the query.

