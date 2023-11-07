# Changelog

All notable changes to this project will be documented in this file.

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


