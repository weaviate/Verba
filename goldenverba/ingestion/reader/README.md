01. READER 

The task of the Reader is to import different data sources and convert them into a Verba Document.

The Verba Document contains the document text, name, origin, link and other meta data. The Verba Document is one of the essential building block of Verba.
You can serialize and deserialize Verba documents into .verba binary files if needed

You can create different Readers that load data from different sources, for example, PDFReader, GithubReader, NotionReader, etc.
All Readers must inherit the interface Reader class and implement its method. It's important that the outputs of the require methods are aligning with custom Reader. The ReaderManager manages and contains all useable readers, you can use the Manager to control which Reader should be used. The ReaderManager is used in the Verba Manager which orchestrates the whole end-to-end pipeline.


How to create a new Reader
1. Create a new python file within the reader folder
2. Create a class that inherits the Reader class
3. Implement it's methods (e.g. load())
4. Add your new Readerclass to the ReaderManager
5. Add unit tests and usage examples in the reader/tests folder with example data