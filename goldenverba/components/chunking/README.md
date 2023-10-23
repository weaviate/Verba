02. CHUNKER

The task of the chunker is to chunk documents into smaller pieces, dependning on the type of chunker. Possible methods are chunking based on words or sentences. You can control how many units per chunk, and if you want to have an overlap.

You can create custom chunkers, the interface of a chunker expects a list of Verba documents, adds the chunks to the verba documents, and ooutputs the list wit modified documents


How to create a new Reader
1. Create a new python file within the chunker folder
2. Create a class that inherits the Chunker class
3. Implement it's methods (e.g. chunk())
4. Add your new Chunker class to the ChunkerManager
5. Add unit tests and usage examples in the chunker/tests folder with example data