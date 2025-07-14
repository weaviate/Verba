# Changelog

All notable changes to this project will be documented in this file.

## [2.1.3] More data types

## Added

- Added `OLLAMA_MODEL` and `OLLAMA_EMBED_MODEL` environment variables (https://github.com/weaviate/Verba/pull/372)
- Hiding `Getting Started` display after showing once
- Added support for `csv` `xlsx` `xls` for the `DefaultReader`

## [2.1.2] Adding Novita!

## Added

- Added Novita Generator (https://www.novita.ai/)
- Added basic tests for Document class

## Fixed

- spaCy Language Issues (https://github.com/weaviate/Verba/issues/359#issuecomment-2612233766) (https://github.com/weaviate/Verba/issues/352)

## [2.1.1] More Bugs!

## Added

- Dynamic model name retrieval for OpenAI Generator based on OpenAI URL and API Key (https://github.com/weaviate/Verba/issues/123) (https://github.com/weaviate/Verba/issues/362)

## [2.1.0] Fixing Bugs and Adding Friends

## Added

- Added Upstage: Reader, Embedder, Generator (https://www.upstage.ai/)
- Added new deployment type: Custom
- Added new port configuration (https://github.com/weaviate/Verba/issues/308)
- Added Groq (https://github.com/weaviate/Verba/pull/278)
- AssemblyAI Reader for audio files (https://github.com/weaviate/Verba/pull/283)
- Language Detection for languages like chinese, english, french, german and dutch (https://github.com/weaviate/Verba/pull/302)
- Improve Markdown Chunking (https://github.com/weaviate/Verba/pull/323)
- Upgrade to latest Weaviate Client
- Added Ollama to Docker Compose
- Added Verba to Docker Hub
- Added default deployment to skip login screen (https://github.com/weaviate/Verba/issues/305)

## Fixed

- Catch Exception when trying to access the OpenAI API Embedding endpoint to retrieve model names
- Fixed reading empty string as environment variables (https://github.com/weaviate/Verba/pull/300)
- Fixed default Unstructed URL (https://github.com/weaviate/Verba/pull/295)
- Changed Collection names to prevent conflicts with other older Verba version generated collections
- Ensure Ollama URL is parsed correctly (https://github.com/weaviate/Verba/pull/327)
- Fixing typos (https://github.com/weaviate/Verba/pull/329)
- System Message is now a textarea in the frontend (https://github.com/weaviate/Verba/issues/334)
- Race Condition when multiple requests try to create same client (https://github.com/weaviate/Verba/issues/335)
- Fix wrong data types when querying additional chunks
- Remove legacy code (https://github.com/weaviate/Verba/issues/284)
- Change Python version range below 3.13
- Firecrawl Reader missing metadata (https://github.com/weaviate/Verba/issues/280)

## [2.0.0] Importastic

## Added

- Async Ingestion with realtime logging
- Migrated to Weaviate v4 Client
- Added new File Selection Interface
- Add Directory Upload
- Control Settings per file/url individually
- Import indivdual files or all
- Overwrite existing files
- Add multiple labels to documents
- More configuration for readers, chunkers, and embedders
- Improved Document Search UI
- Add Config Validation
- Add HTML Reader
- Add Recursive Chunker
- HTML Chunker
- Markdown Chunker
- Code Import
- Code Chunking
- Semantic Chunking
- Label Filter
- Document Filter (Add document to chat)
- Add more themes
- Reworked Admin Interface
- Added Suggestion View
- Reworked Suggestion logic
- Added VoyageAI
- Added custom metadata
- Added DocumentExplorer with

  - Content View
  - Chunk View
  - Vector View
    - Visualize vectors of chunks of one or multiple documents
    - PCA

-

## [1.0.3]

## Added

- Cancel Generation Button
- Added .docx support
- Added Documentation for JSON Files
- Added GitLabReader (https://github.com/weaviate/Verba/pull/151)
- Improved HuggingFace Embedding Models thanks to @tomaarsen
- MixedBreadEmbedder
- AllMPNetEmbedder

## Fixed

- Check error logs coming from Ollama and send it to the frontend
- Check If Chunks Are NoneType

## [1.0.2]

## Added

- Readme Variable: OPENAI_BASE_URL

## Fixed

- https://github.com/weaviate/Verba/pull/173
- https://github.com/weaviate/Verba/pull/163
- https://github.com/weaviate/Verba/pull/148

## [1.0.0] - Beautiful Verba Update

### Added

- Added DaisyUI
- Optimized frontend codebase
- Fully Reworked Verba Design
  - Fully Responsive, optimized for all screen sizes
- Customization Capabilities
  - Added Default, Darkmode, Weaviate themes
  - Full text, color, image customization
- Improve Chat Interface
  - Better formatting of markdown + code
  - Keep conversations saved in localBrowser storage
  - Better Debugging by providing more information about current states
- Improve Document Viewer Interface
  - Add Pagination
  - Add Sorting
  - Use Aggregation for Filtering
- Improve Status Overview
  - Reworked Frontend + Optimize Code
  - Sort status entries
  - Improve Loading Speed by using Aggregation
- Improve Component Selection for both Ingestion and RAG
  - Added new configuraiton that will be passed between frontend and backend
  - Cleaned codebase, merged interfaces and managers to single files
  - Added clean endpoints for better code readability
  - Reworked on interfaces
- Added better console and logging for ingestion
- More Configuration
  - Enable/Disable Caching and Autocomplete Suggestions
  - Improved verba_config.json
- Ability to enable/disable caching + autosuggestions
- Add Google Gemini as new Embedder and Generator
- Added .CSV support (all file types available in Unstructured IO)
- More test data
- Add Ollama as Generator and Embedding Component
- Add Support for Cohere R+
- Improved WindowRetriever Context Generation
- Show RAW Context in Frontend + Save in LocalStorage
- Save Settings and Configuration in Weaviate

### Changed

- Changed to AppRouter framework
- Changed frontend project structure
- Changed backend project structure
- Removed Llama Generator Component

### Fixed

- Using Accelerator Library

## [0.4.0] - 11.04.2024

### Added

- Improved Docker Documentation
- Improved Docker Settings
- New Environment Variables for OpenAI proxies: OpenAI_BASE_URL (LiteLLM support) (https://github.com/weaviate/Verba/issues/56)
- Increased version

### Changed

- Removed spaCy from project

### Fixed

- Python not working on version 3.12, 3.11, and 3.9
- GitHub Links on README
- Fix Docker Default Vectorizer (https://github.com/weaviate/Verba/issues/50)
- Fix requirements.txt spelling error
- Minor Bug fixes

## [0.3.1] - 15.11.2023

### Added

- PDFReader powered by PyPDF2
- TokenChunker powered by tiktoken
- Ruff Linting (set as pre-commit)
- Markdown Formatting for chat messages (https://github.com/weaviate/Verba/issues/48)

### Fixed

- Added missing dependencies
- Fixed restart bug
- Fixed MiniLM Cuda to_device bug (https://github.com/weaviate/Verba/issues/41)
- Fixed Config Issues (https://github.com/weaviate/Verba/issues/51)
- Fixed Weaviate Embedded Headers for Cohere

## [0.3.0] - 12.09.2023

### Added

- Refactor modular architecture
- Add ability to import data through the frontend, CLI, and script
- Add Readers (SimpleReader, PathReader, GithubReader, PDFReader)
- Add Chunkers (WordChunker, SentenceChunker)
- Add Embedders (ADAEmbedder,SentenceTransformer, Cohere)
- Add Generators (GPT3, GPT4, LLama, Cohere)
- Status Page
- Reset functionality
- Streaming Token Generation
- Lazy Document Loading
- Add Copy and Cached Tag
- Improved Semantic Cache
- Added LLama 2 and Cohere support
- Added new OpenAI models
- Improved Documentation
- Added technical docs and contribution guidelines

### Fixed

- Error handling for data ingestion (handling chunk size)
- Schmea handling on startup

### Changed

- Removed Simple- and AdvancedEngine logic

## [0.2.3] - 05.09.2023

### Added

- OpenAI API documentation example dataset

## [0.2.2] - 31.08.2023

### Release!

- First version of Verba released! (many to come :)

### Added

- Verba favicon

### Fixed

- Add static files to package
- Weaviate Embedded not shutting down

## [0.1.0] - 29.08.2023

### Added

- Prepare Verba for first release
