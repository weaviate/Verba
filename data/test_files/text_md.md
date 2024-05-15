# Verba 
## 🐕 The Golden RAGtriever

Welcome to Verba: The Golden RAGtriever, an open-source application designed to offer an end-to-end, streamlined, and user-friendly interface for Retrieval-Augmented Generation (RAG) out of the box. In just a few easy steps, explore your datasets and extract insights with ease, either locally or through LLM providers such as OpenAI, Cohere, and HuggingFace.

```
pip install goldenverba
```

[![Weaviate](https://img.shields.io/static/v1?label=powered%20by&message=Weaviate%20%E2%9D%A4&color=green&style=flat-square)](https://weaviate.io/) 
[![PyPi downloads](https://static.pepy.tech/personalized-badge/goldenverba?period=total&units=international_system&left_color=grey&right_color=orange&left_text=pip%20downloads)](https://pypi.org/project/goldenverba/) [![Docker support](https://img.shields.io/badge/Docker_support-%E2%9C%93-4c1?style=flat-square&logo=docker&logoColor=white)](https://docs.docker.com/get-started/) [![Demo](https://img.shields.io/badge/Check%20out%20the%20demo!-yellow?&style=flat-square&logo=react&logoColor=white)](https://verba.weaviate.io/)

![Demo of Verba](https://github.com/weaviate/Verba/blob/dev/img/verba.gif)

- [Verba](#verba)
  - [🎯 What Is Verba?](#what-is-verba)
  - [⚙️ Under the Hood](#️under-the-hood)
  - [💡 Effortless Data Import with Weaviate](#effortless-data-import-with-weaviate)
  - [💥 Advanced Query Resolution with Hybrid Search](#advanced-query-resolution-with-hybrid-search)
  - [🔥 Accelerate Queries with Semantic Cache](#accelerate-queries-with-semantic-cache)
- [✨ Getting Started with Verba](#getting-started-with-verba)
- [🐍 Installing Python and Setting Up a Virtual Environment](#installing-python-and-setting-up-a-virtual-environment)
  - [Installing Python](#installing-python)
  - [Setting Up a Virtual Environment](#setting-up-a-virtual-environment)
- [📦 Choosing the Right Verba Installation Package](#choosing-the-right-verba-installation-package)
  - [Default Package](#default-package)
  - [HuggingFace Version](#huggingface-version)
  - [Development Version](#development-version)
- [🚀 Quickstart: Deploy with pip](#quickstart-deploy-with-pip)
- [🛠️ Quickstart: Build from Source](#️quickstart-build-from-source)
- [🔑 API Keys](#api-keys)
  - [Weaviate](#weaviate)
  - [OpenAI](#openai)
  - [Cohere](#cohere)
  - [HuggingFace](#huggingface)
    - [Llama2](#llama2)
  - [Unstructured](#unstructured)
  - [Github](#github)
- [🐳 Quickstart: Deploy with Docker](#quickstart-deploy-with-docker)
  - [Large Language Model (LLM) Costs](#large-language-model-llm-costs)
- [💾 Importing Your Data into Verba](#️importing-your-data-into-verba)
- [🛠️ Project Architecture](#️project-architecture)
- [💖 Open Source Contribution](#open-source-contribution)

## What Is Verba?
Verba is more than just a tool—it's a personal assistant for querying and interacting with your data, **either locally or deployed via cloud**. Have questions about your documents? Need to cross-reference multiple data points? Want to gain insights from your existing knowledge base? Verba empowers you with the combined capabilities of Weaviate's context-aware database and the analytical power of Large Language Models (LLMs). Interact with your data through an intuitive chat interface that refines search results by using the ongoing conversation context to deliver even more accurate and relevant information.

![Demo of Verba](https://github.com/weaviate/Verba/blob/dev/img/verba_screen.png)

### Under the Hood
Verba is engineered with Weaviate's cutting-edge Generative Search technology at its core, extracting relevant context from your pool of documents to resolve queries with precision. By utilizing the power of Large Language Models, Verba doesn't just search for answers—it understands and provides responses that are contextually rich and informed by the content of your documents, all through an intuitive user interface designed for simplicity and efficiency.

### Effortless Data Import with Weaviate
Verba offers seamless data import functionality through its frontend, supporting a diverse range of file types including `.txt`, `.md`, `.pdf` and more. Before feeding your data into Weaviate, Verba handles chunking and vectorization to optimize it for search and retrieval. Together with collaborative partners we support popular libraries such as [HuggingFace](https://github.com/huggingface), [Haystack](https://github.com/deepset-ai/haystack), [Unstructured](https://github.com/Unstructured-IO/unstructured) and many more!

![Demo of Verba](https://github.com/weaviate/Verba/blob/dev/img/verba_import.png)

### Advanced Query Resolution with Hybrid Search
Experience the hybrid search capabilities of Weaviate within Verba, which merges vector and lexical search methodologies for even greater precision. This dual approach not only navigates through your documents to pinpoint exact matches but also understands the nuance of context, enabling the Large Language Models to craft responses that are both comprehensive and contextually aware. It's an advanced technique that redefines document retrieval, providing you with precisely what you need, when you need it.

### Accelerate Queries with Semantic Cache
Verba enhances search efficiency with Weaviate's Semantic Cache, a sophisticated system that retains the essence of your queries, results, and dialogues. This proactive feature means that Verba anticipates your needs, using cached data to expedite future inquiries. With semantic matching, it quickly determines if your question has been asked before, delivering instant results, and even suggests auto-completions based on historical interactions, streamlining your search experience to be faster and more intuitive.

---

# Getting Started with Verba

Starting your Verba journey is super easy, with multiple deployment options tailored to your preferences. Follow these simple steps to get Verba up and running:

- Deploy with pip [(Quickstart)](##🚀-Quickstart:-Deploy-with-pip)
```
pip install goldenverba
```
- Build from Source [(Quickstart)](##🛠️-Quickstart:-Build-from-Source)
```
git clone https://github.com/weaviate/Verba

pip install -e .
```
- Use Docker for Deployment [(Quickstart)](##🐳-Quickstart:-Deploy-with-Docker)

**Prerequisites**: If you're not using Docker, ensure that you have `Python >=3.10.0` installed on your system.

# Installing Python and Setting Up a Virtual Environment
Before you can use Verba, you'll need to ensure that `Python >=3.10.0` is installed on your system and that you can create a virtual environment for a safer and cleaner project setup.

## Installing Python
Python is required to run Verba. If you don't have Python installed, follow these steps:

### For Windows:
Download the latest Python installer from the official Python website.
Run the installer and make sure to check the box that says `Add Python to PATH` during installation.

### For macOS:
You can install Python using Homebrew, a package manager for macOS, with the following command in the terminal:
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then install Python:
```
brew install python
```

### For Linux:
Python usually comes pre-installed on most Linux distributions. If it's not, you can install it using your distribution's package manager. You can read more about it [here](https://opensource.com/article/20/4/install-python-linux)

## Setting Up a Virtual Environment
It's recommended to use a virtual environment to avoid conflicts with other projects or system-wide Python packages.

### Install the virtualenv package:
First, ensure you have pip installed (it comes with Python if you're using version 3.4 and above).
Install virtualenv by running:
```
pip install virtualenv
```

### Create a Virtual Environment:
Navigate to your project's directory in the terminal.
Run the following command to create a virtual environment named venv (you can name it anything you like):
```
python3 -m virtualenv venv
```

### Activate the Virtual Environment:
- On Windows, activate the virtual environment by running:
```
venv\Scripts\activate.bat
```

- On macOS and Linux, activate it with:
```
source venv/bin/activate
```

Once your virtual environment is activated, you'll see its name in the terminal prompt. Now you're ready to install Verba using the steps provided in the Quickstart sections.

> Remember to deactivate the virtual environment when you're done working with Verba by simply running deactivate in the terminal.

# Choosing the Right Verba Installation Package
Verba comes in several installation packages, each tailored for specific use cases and environments. Choose the package that aligns with your requirements:

## Default Package
The default package is perfect for getting started quickly and includes support for popular models and services like OpenAI, Cohere, and spaCy. This package is suitable for general use and can be installed easily via pip:

```
pip install goldenverba
```

> This will set you up with all you need to integrate Verba with these services without additional configuration.

## HuggingFace Version
For those looking to leverage models from the HuggingFace ecosystem, including `SentenceTransformer` and `LLama2`, the HuggingFace version is the ideal choice. This package is optimized for GPU usage to accommodate the high performance demands of these models:

```
pip install goldenverba[huggingface]
```

> Note: It's recommended to run this version on a system with a GPU to fully utilize the capabilities of the advanced models.

## Development Version
If you're a developer looking to contribute to Verba or need the latest features still in development, the dev version is what you're looking for. This version may be less stable but offers the cutting edge of Verba's capabilities:

```
pip install goldenverba[dev]
```

> Keep in mind that this version is intended for development purposes and may contain experimental features.

# Quickstart: Deploy with pip

1. **Initialize a new Python Environment**
```
python3 -m virtualenv venv
```

2. **Install Verba**
```
pip install goldenverba
```

3. **Launch Verba**
```
verba start
```

4. **Access Verba**
```
Visit localhost:8000
```

5. **Create .env file and add environment variables**

# Quickstart: Build from Source

1. **Clone the Verba repos**
```
git clone https://github.com/weaviate/Verba.git
```

2. **Initialize a new Python Environment**
```
python3 -m virtualenv venv
```

3. **Install Verba**
```
pip install -e .
```

4. **Launch Verba**
```
verba start
```

5. **Access Verba**
```
Visit localhost:8000
```

6. **Create .env file and add environment variables**

# API Keys

Before diving into Verba's capabilities, you'll need to configure access to various components depending on your chosen technologies, such as OpenAI, Cohere, and HuggingFace. Start by obtaining the necessary API keys and setting them up through a `.env` file based on our provided [example](./goldenverba/.env.example) , or by declaring them as environment variables on your system. If you're building from source or using Docker, make sure your `.env` file is within the goldenverba directory.
Please make sure to only include environment variables you really need.

Below is a comprehensive list of the API keys and variables you may require:

## Weaviate
Verba provides flexibility in connecting to Weaviate instances based on your needs. By default, Verba opts for [Weaviate Embedded](https://weaviate.io/developers/weaviate/installation/embedded) if it doesn't detect the `WEAVIATE_URL_VERBA` and `WEAVIATE_API_KEY_VERBA` environment variables. This local deployment is the most straightforward way to launch your Weaviate database for prototyping and testing.

However, you have other compelling options to consider:

**🌩️ Weaviate Cloud Service (WCS)**

If you prefer a cloud-based solution, Weaviate Cloud Service (WCS) offers a scalable, managed environment. Learn how to set up a cloud cluster and get the API keys by following the [Weaviate Cluster Setup Guide](https://weaviate.io/developers/wcs/guides/create-instance).

**🐳 Docker Deployment**
Another robust local alternative is deploying Weaviate using Docker. For more details, consult the [Weaviate Docker Guide](https://weaviate.io/developers/weaviate/installation/docker-compose).

```
WEAVIATE_URL_VERBA=URL-TO-YOUR-WEAVIATE-CLUSTER

WEAVIATE_API_KEY_VERBA=API-KEY-OF-YOUR-WEAVIATE-CLUSTER
```

## OpenAI

Verba supports OpenAI Models such as Ada, GPT3, and GPT4. To use them, you need to specify the `OPENAI_API_KEY` environment variable. You can get it from [OpenAI](https://openai.com/)

```
OPENAI_API_KEY=YOUR-OPENAI-KEY
```

You can also add a `OPENAI_BASE_URL` to use proxies such as LiteLLM (https://github.com/BerriAI/litellm)

```
OPENAI_BASE_URL=YOUR-OPENAI_BASE_URL
```

## Azure OpenAI

To use Azure OpenAI, you need to set 

- The API type:
```
OPENAI_API_TYPE="azure"
```

- The key and the endpoint:

```
OPENAI_API_KEY=<YOUR_KEY>
OPENAI_BASE_URL=http://XXX.openai.azure.com
```

- Azure OpenAI ressource name, which is XXX if your endpoint is XXX.openai.azure.com

```
AZURE_OPENAI_RESOURCE_NAME=<YOUR_AZURE_RESOURCE_NAME>
```
- You need to set the models, for the embeddings and for the query.
```
AZURE_OPENAI_EMBEDDING_MODEL="text-embedding-ada-002"
OPENAI_MODEL="gpt-4" 
```

- Finally, as Azure is using per-minute quota, you might need to add a waiting time between each chunk upload. For example, if you have a limit of 240k tokens per minute, if your chunks are 
400 tokens max, then 100ms between queries should be fine. If you get error 429 from weaviate, then increase this value.

```
WAIT_TIME_BETWEEN_INGESTION_QUERIES_MS="100"
```

## Cohere

Verba supports Cohere Models, to use them, you need to specify the `COHERE_API_KEY` environment variable. You can get it from [Cohere](https://dashboard.cohere.com/)

```
COHERE_API_KEY=YOUR-COHERE-KEY
```

## HuggingFace

Verba supports HuggingFace models, such as SentenceTransformers and Llama2. To use them you need the `HF_TOKEN` environment variable. You can get it from [HuggingFace](https://huggingface.co/)

```
HF_TOKEN=YOUR-HUGGINGFACE-TOKEN
```

### Llama2 

To use the Llama2 model from Meta, you first need to request access to it. Read more about accessing the [Llama model here](https://huggingface.co/blog/llama2). To enable the LLama2 model for Verba use:

```
LLAMA2-7B-CHAT-HF=True
```

## Unstructured
Verba supports importing documents through Unstructured (e.g .pdf). To use them you need the `UNSTRUCTURED_API_KEY` environment variable. You can get it from [Unstructured](https://unstructured.io/)

```
UNSTRUCTURED_API_KEY=YOUR-UNSTRUCTURED-KEY
UNSTRUCTURED_API_URL=YOUR-SELF-HOSTED-INSTANCE # If you are self hosting, in the form of `http://localhost:8000/general/v0/general`
```



## Github

If you want to use the Github Reader, you need the `GITHUB_TOKEN` environment variable. You can get it from [GitHub](https://github.com/)

```
GITHUB_TOKEN=YOUR-GITHUB-TOKEN
```

## Status Page

Once configured, you can monitor your Verba installation's health and status via the 'Status Verba' page. This dashboard provides insights into your deployment type, libraries, environment settings, Weaviate schema counts, and more. It's also your go-to for maintenance tasks like resetting Verba, clearing the cache, or managing auto-complete suggestions.

![Demo of Verba](https://github.com/weaviate/Verba/blob/dev/img/verba_status.png)

# Quickstart: Deploy with Docker

Docker is a set of platform-as-a-service products that use OS-level virtualization to deliver software in packages called containers. Containers are isolated from one another and bundle their own software, libraries, and configuration files; they can communicate with each other through well-defined channels. All containers are run by a single operating system kernel and are thus more lightweight than virtual machines. Docker provides an additional layer of abstraction and automation of operating-system-level virtualization on Windows and Linux.

Docker's use of containers to package software means that the application and its dependencies, libraries, and other binaries are packaged together and can be moved between environments easily. This makes it incredibly useful for developers looking to create predictable environments that are isolated from other applications. 

To get started with deploying Verba using Docker, follow the steps below. If you need more detailed instructions on Docker usage, check out the [Docker Curriculum](https://docker-curriculum.com/).

If you're unfamiliar with Docker, you can learn more about it [here](https://docker-curriculum.com/).

0. **Clone the Verba repos**
Ensure you have Git installed on your system. Then, open a terminal or command prompt and run the following command to clone the Verba repository:

```
git clone https://github.com/weaviate/Verba.git
```

1. **Set neccessary environment variables**
Make sure to set your required environment variables in the ```.env``` file. You can read more about how to set them up in the [API Keys Section](#api-keys)

2. **Adjust the docker-compose file**
You can use the ```docker-compose.yml``` to add required environment variables under the ```verba``` service and can also adjust the Weaviate Docker settings to enable Authentification or change other settings of your database instance. You can read more about the Weaviate configuration in our [docker-compose documentation](https://weaviate.io/developers/weaviate/installation/docker-compose)

> Please make sure to only add environment variables that you really need. If have no authentifcation enabled in your Weaviate Cluster, make sure to not include the ```WEAVIATE_API_KEY_VERBA``` enviroment variable

2. **Deploy using Docker**
With Docker installed and the Verba repository cloned, navigate to the directory containing the Docker Compose file in your terminal or command prompt. Run the following command to start the Verba application in detached mode, which allows it to run in the background:

```
docker compose up -d
```

This command will download the necessary Docker images, create containers, and start Verba.
Remember, Docker must be installed on your system to use this method. For installation instructions and more details about Docker, visit the official Docker documentation. 

4. **Access Verba**

- You can access your local Weaviate instance at ```localhost:8080```

- You can access the Verba frontend at ```localhost:8000```


If you want your Docker Instance to install a specific version of Verba (as described in the [package section](#choosing-the-right-verba-installation-package)) you can edit the ```Dockerfile``` and change the installation line.

```
RUN pip install -e '.'
```


## Importing Your Data into Verba

With Verba configured, you're ready to import your data and start exploring. Follow these simple steps to get your data into Verba:

![Demo of Verba](https://github.com/weaviate/Verba/blob/dev/img/verba_data.gif)

1. **Initiate the Import Process**
   - Click on "Add Documents" to begin.

2. **Select Your Data Processing Tools**
   - At the top, you'll find three tabs labeled `Reader`, `Chunker`, and `Embedder`, each offering different options for handling your data.

3. **Choose a Reader**
   - The `Reader` is responsible for importing your data. Select from the available options:
     - `SimpleReader`: For importing `.txt` and `.md` files.
     - `GitHubReader`: For loading data directly from a GitHub repository by specifying the path (`owner/repo/folder_path`).
     - `PDFReader`: For importing `.pdf` files.

4. **Select a Chunker**
   - `Chunkers` break down your data into manageable pieces. Choose a suitable chunker:
     - `WordChunker`: Chunks the text by words.
     - `SentenceChunker`: Chunks the text by sentences.

5. **Pick an Embedder**
   - `Embedders` are crucial for integrating your data into Weaviate. Select one based on your preference:
     - `AdaEmbedder`: Utilizes OpenAI's ADA model for embedding.
     - `MiniLMEmbedder`: Employs Sentence Transformers for embedding.
     - `CohereEmbedder`: Uses Cohere for embedding.

6. **Commence Data Ingestion**
   - After setting up your preferences, click on "Import" to ingest your data into Verba.

Now your data is ready to be used within Verba, enabling you to leverage its powerful search and retrieval capabilities.

## Large Language Model (LLM) Costs

Verba utilizes LLM models through APIs. Be advised that the usage costs for these models will be billed to the API access key you provide. Primarily, costs are incurred during data embedding and answer generation processes.

## Open Source Contribution

Your contributions are always welcome! Feel free to contribute ideas, feedback, or create issues and bug reports if you find any! Before contributing, please read the [Contribution Guide](./CONTRIBUTING.md). Visit our [Weaviate Community Forum](https://forum.weaviate.io/) if you need any help!

### Project Architecture
You can learn more about Verba's architecture and implementation in its [technical documentation](./TECHNICAL.md) and [frontend documentation](./FRONTEND.md). It's recommended to read them before making any contributions.

