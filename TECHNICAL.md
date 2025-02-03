# Verba - Technical Documentation

This technical documentation is intended for developers who want to understand the inner workings of Verba. Please note that this document might be uncomplete and missing some parts. If you encounter any issues or have questions, please feel free to open an issue.

## FastAPI Server

Verba is served through a FastAPI server. The server is serving the static frontend files through the specified port. If you're modifying the frontend, you will need to rebuild the static files again. The frontend is sending API calls to itself which the FastAPI server handles. The server can handle multiple client connections which are handled by the `ClientManager` class.

### ClientManager

`TODO`

For handling large upload of files, the `BatchManager` class handles batches of data of a single file to merge it into a single file once all batches have been received.

### BatchManager

`TODO`

### Websocket

`TODO`

## Automated Testing

`TODO`

## FAQ

### How to control the position of context sent to the Generator to generate a response?

Every `generator` class has a `prepare_messages` method. This method is used to format the messages that are sent to the LLM. The position of the context in the messages is important because it determines where the context is placed in the conversation.

### How to upload a JSON file to Verba?

## Verba JSON Structure

A Verba Document can be created from a JSON object. The JSON object is converted to a Verba Document object and then uploaded to the vector database. Here's the general structure of a Verba Document (you can also find the implementation in the `Document.py` file):

```python
{
    "title": "string", # The title of the document
    "content": "string", # The content of the document
    "extension": "string", # The extension of the document (Optional)
    "fileSize": "number", # The size of the document in bytes (Optional)
    "labels": "array", # The labels of the document (can be empty, used for filtering)
    "source": "string", # The source of the document (can be an URL, optional)
    "meta": "object", # The meta data of the document used internally
    "metadata": "string" # Metadata information of the document, will be used in the embedding process
}
```

## Custom JSON Structure

There is currently no support for custom JSON structure. Instead the whole JSON will simply be dumped into the content field of the Verba document.
There are plans to add support for custom JSON structure in the future.
