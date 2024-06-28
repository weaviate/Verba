# Changelog

All notable changes to this project will be documented in this file.

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
