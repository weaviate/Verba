from wasabi import msg  # type: ignore[import]
import weaviate
import os

from goldenverba.ingestion.util import setup_client

from dotenv import load_dotenv

load_dotenv()


def init_schema(model: str = "gpt-3.5-turbo"):
    msg.divider("Creating Document and Chunk class")

    client = setup_client()

    if not client:
        msg.fail("Could not get client.")
        return False
    
    # check if we can get info from server (testing auth)
    try:
        client.cluster.get_nodes_status()
    except weaviate.exceptions.UnexpectedStatusCodeException as e:
        msg.fail("Error on init schema: {0}".format(e))
        return False


    if os.getenv("OPENAI_API_TYPE") == "azure":
        resourceName = os.getenv("AZURE_OPENAI_RESOURCE_NAME")
        if resourceName is None:
            raise Exception("AZURE_OPENAI_RESOURCE_NAME should be set when OPENAI_API_TYPE is azure. It is XXX in http://XXX.openai.azure.com")
        moduleConfig = { 
            "generative-openai": {
                    "generative-openai": {"model": model}
            },
            "text2vec-openai": {
                    "deploymentId": model,
                    "resourceName": resourceName
            }
        }
    else:
        moduleConfig =  {
                    "generative-openai": {"model": model}
                },

    chunk_schema = {
        "classes": [
            {
                "class": "Chunk",
                "description": "Chunks of Documentations",
                "vectorizer": "text2vec-openai",
                "moduleConfig": moduleConfig, 
                "properties": [
                    {
                        "name": "text",
                        "dataType": ["text"],
                        "description": "Content of the document",
                    },
                    {
                        "name": "doc_name",
                        "dataType": ["text"],
                        "description": "Document name",
                    },
                    {
                        "name": "doc_type",
                        "dataType": ["text"],
                        "description": "Document type",
                    },
                    {
                        "name": "doc_uuid",
                        "dataType": ["text"],
                        "description": "Document UUID",
                        "moduleConfig": {
                            "text2vec-openai": {
                                "skip": True,
                                "vectorizePropertyName": False,
                            }
                        },
                    },
                    {
                        "name": "chunk_id",
                        "dataType": ["number"],
                        "description": "Document chunk from the whole document",
                        "moduleConfig": {
                            "text2vec-openai": {
                                "skip": True,
                                "vectorizePropertyName": False,
                            }
                        },
                    },
                ],
            }
        ]
    }

    document_schema = {
        "classes": [
            {
                "class": "Document",
                "description": "Documentation",
                "properties": [
                    {
                        "name": "text",
                        "dataType": ["text"],
                        "description": "Content of the document",
                    },
                    {
                        "name": "doc_name",
                        "dataType": ["text"],
                        "description": "Document name",
                    },
                    {
                        "name": "doc_type",
                        "dataType": ["text"],
                        "description": "Document type",
                    },
                    {
                        "name": "doc_link",
                        "dataType": ["text"],
                        "description": "Link to document",
                    },
                ],
            }
        ]
    }

    if client.schema.exists("Document"):
        user_input = input(
            "Document class already exists, do you want to overwrite it? (y/n): "
        )
        if user_input.strip().lower() == "y":
            client.schema.delete_class("Document")
            client.schema.delete_class("Chunk")
            client.schema.create(document_schema)
            client.schema.create(chunk_schema)
            msg.good("'Document' and 'Chunk' schemas created")
        else:
            msg.warn("Skipped deleting Document and Chunk schema, nothing changed")
    else:
        client.schema.create(document_schema)
        client.schema.create(chunk_schema)
        msg.good("'Document' and 'Chunk' schemas created")

    if client._connection.embedded_db:
        msg.info("Stopping Weaviate Embedded")
        client._connection.embedded_db.stop()
    msg.info("Done")
    return True
