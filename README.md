# Verba 
## 🐕 The Golden RAGtriever

Welcome to Verba: The Golden RAGtriever, an open-source application designed to offer an end-to-end, streamlined, and user-friendly interface for Retrieval-Augmented Generation (RAG) out of the box. In just a few easy steps, explore your datasets and extract insights with ease, either locally or through LLM providers such as OpenAI, Cohere, and HuggingFace.

```pip install goldenverba```

[![Weaviate](https://img.shields.io/static/v1?label=powered%20by&message=Weaviate%20%E2%9D%A4&color=green&style=flat-square)](https://weaviate.io/) 
[![PyPi downloads](https://static.pepy.tech/personalized-badge/goldenverba?period=total&units=international_system&left_color=grey&right_color=orange&left_text=pip%20downloads)](https://pypi.org/project/goldenverba/) [![Docker support](https://img.shields.io/badge/Docker_support-%E2%9C%93-4c1?style=flat-square&logo=docker&logoColor=white)](https://docs.docker.com/get-started/) [![Demo](https://img.shields.io/badge/Check%20out%20the%20demo!-yellow?&style=flat-square&logo=react&logoColor=white)](https://verba.weaviate.io/)

![Demo of Verba](https://github.com/weaviate/Verba/blob/dev/img/verba.gif)

## 🎯 What Is Verba?
Verba is more than just a tool—it's a personal assistant for querying and interacting with your data, **either locally or deployed via cloud**. Have questions about your documents? Need to cross-reference multiple data points? Want to gain insights from your existing knowledge base? Verba empowers you with the combined capabilities of Weaviate's context-aware database and the analytical power of Large Language Models (LLMs). Interact with your data through an intuitive chat interface that refines search results by using the ongoing conversation context to deliver even more accurate and relevant information.

![Demo of Verba](https://github.com/weaviate/Verba/blob/dev/img/verba_screen.png)

## ⚙️ Under the Hood
Verba is engineered with Weaviate's cutting-edge Generative Search technology at its core, extracting relevant context from your pool of documents to resolve queries with precision. By utilizing the power of Large Language Models, Verba doesn't just search for answers—it understands and provides responses that are contextually rich and informed by the content of your documents, all through an intuitive user interface designed for simplicity and efficiency.

## 💡 Effortless Data Import with Weaviate
Verba offers seamless data import functionality through its frontend, supporting a diverse range of file types including `.txt`, `.md`, `.pdf` and more. Before feeding your data into Weaviate, Verba handles chunking and vectorization to optimize it for search and retrieval. Together with collaborative partners we support popular libraries such as [HuggingFace](https://github.com/huggingface), [Haystack](https://github.com/deepset-ai/haystack), [Unstructured](https://github.com/Unstructured-IO/unstructured) and many more!

![Demo of Verba](https://github.com/weaviate/Verba/blob/dev/img/verba_import.png)

## 💥 Advanced Query Resolution with Hybrid Search
Experience the hybrid search capabilities of Weaviate within Verba, which merges vector and lexical search methodologies for even greater precision. This dual approach not only navigates through your documents to pinpoint exact matches but also understands the nuance of context, enabling the Large Language Models to craft responses that are both comprehensive and contextually aware. It's an advanced technique that redefines document retrieval, providing you with precisely what you need, when you need it.

## 🔥 Accelerate Queries with Semantic Cache
Verba enhances search efficiency with Weaviate's Semantic Cache, a sophisticated system that retains the essence of your queries, results, and dialogues. This proactive feature means that Verba anticipates your needs, using cached data to expedite future inquiries. With semantic matching, it quickly determines if your question has been asked before, delivering instant results, and even suggests auto-completions based on historical interactions, streamlining your search experience to be faster and more intuitive.

# ✨ Getting Started with Verba

Starting your Verba journey is super easy, with multiple deployment options tailored to your preferences. Follow these simple steps to get Verba up and running:

- Deploy with pip [(Quickstart)](##🚀-Quickstart:-Deploy-with-pip)
    -  `pip install goldenverba`
- Build from Source [(Quickstart)](##🛠️-Quickstart:-Build-from-Source)
    - `git clone https://github.com/weaviate/Verba`
    - `pip install -e .`
- Use Docker for Deployment [(Quickstart)](##🐳-Quickstart:-Deploy-with-Docker)

**Prerequisites**: If you're not using Docker, ensure that you have `Python >=3.9.0` installed on your system.

## 🔑 Status page and API Key Requirements

Before diving into Verba's capabilities, you'll need to configure access to various components depending on your chosen technologies, such as OpenAI, Cohere, and HuggingFace. Start by obtaining the necessary API keys and setting them up through a `.env` file based on our provided [example](./.env.example) , or by declaring them as environment variables on your system. Below is a comprehensive list of the API keys and variables you may require:

- ```WEAVIATE_URL_VERBA=URL-TO-YOUR-WEAVIATE-CLUSTER```
- ```WEAVIATE_API_KEY_VERBA=API-KEY-OF-YOUR-WEAVIATE-CLUSTER```
- ```OPENAI_API_KEY=YOUR-OPENAI-KEY```
- ```COHERE_API_KEY=YOUR-COHERE-KEY```
- ```UNSTRUCTURED_API_KEY=YOUR-UNSTRUCTURED-KEY```
- ```GITHUB_TOKEN=YOUR-GITHUB-TOKEN```
- ```HF_TOKEN=YOUR-HUGGINGFACE-TOKEN```
- ```LLAMA2-7B-CHAT-HF=ENABLE-LLAMA2?-(True or False)```

Once configured, you can monitor your Verba installation's health and status via the 'Status Verba' page. This dashboard provides insights into your deployment type, libraries, environment settings, Weaviate schema counts, and more. It's also your go-to for maintenance tasks like resetting Verba, clearing the cache, or managing auto-complete suggestions.

![Demo of Verba](https://github.com/weaviate/Verba/blob/dev/img/verba_status.png)

## 🚀 Quickstart: Deploy with pip

1. **Initialize a new Python Environment**
- ```python3 -m virtualenv venv```

2. **Install Verba**
- ```pip install goldenverba```

3. **Launch Verba**
- ```verba start```

## 🛠️ Quickstart: Build from Source

1. **Clone the Verba repos**
- ```git clone https://github.com/weaviate/Verba.git```

2. **Initialize a new Python Environment**
- ```python3 -m virtualenv venv```

3. **Install Verba**
- ```pip install -e .```

4. **Launch Verba**
- ```verba start```

## 🐳 Quickstart: Deploy with Docker
If you're unfamiliar with Docker, you can learn more about it [here](https://docker-curriculum.com/).

0. **Clone the Verba repos**
- ```git clone https://github.com/weaviate/Verba.git```

1. **Deploy using Docker**
- ``` docker compose up -d ```

## 🌐 Selecting the Optimal Weaviate Deployment for Verba

Verba provides flexibility in connecting to Weaviate instances based on your needs. By default, Verba opts for [Weaviate Embedded](https://weaviate.io/developers/weaviate/installation/embedded) if it doesn't detect the `VERBA_URL` and `VERBA_API_KEY` environment variables. This local deployment is the most straightforward way to launch your Weaviate database for prototyping and testing.

However, you have other compelling options to consider:

**🌩️ Weaviate Cloud Service (WCS)**

If you prefer a cloud-based solution, Weaviate Cloud Service (WCS) offers a scalable, managed environment. Learn how to set up a cloud cluster by following the [Weaviate Cluster Setup Guide](https://weaviate.io/developers/wcs/guides/create-instance).

**🐳 Docker Deployment**
Another robust local alternative is deploying Weaviate using Docker. For more details, consult the [Weaviate Docker Guide](https://weaviate.io/developers/weaviate/installation/docker-compose).

**🌿 Environment Variable Configuration**
Regardless of your chosen deployment method, you'll need to specify the following environment variables. These can either be added to a .env file in your project directory or set as global environment variables on your system:

- ```VERBA_URL=http://your-weaviate-server:8080```
- ```VERBA_API_KEY=your-weaviate-database-key```

# 📦 Data Import Guide

Verba offers straightforward commands to import your data for further interaction. Before you proceed, please be aware that importing data will **incur costs** based on your configured OpenAI access key.

> **Important Notes:**
> Supported file types are currently limited to .txt, .md, and .mdx. Additional formats are in development.
> Basic CRUD operations and UI interactions are also in the pipeline.

``` 
verba start --model "gpt-3.5-turbo"     # Initiates Verba application
verba import --path "Path to your dir or file" --model "gpt-3.5-turbo" --clear True # Imports data into Verba
verba clear                             # Deletes all data within Verba
verba clear_cache                       # Removes cached data in Verba
```

If you've cloned the repository, you can get a quick start with sample datasets in the `./data` directory. Use `verba import --path ./data` to import these samples. You can also populate Verba with predefined suggestions using a JSON list via `verba import --path suggestions.json`. An example is provided in the `./data/minecraft` directory.


## 💰 Large Language Model (LLM) Costs

Verba exclusively utilizes OpenAI models. Be advised that the usage costs for these models will be billed to the API access key you provide. Primarily, costs are incurred during data embedding and answer generation processes. The default vectorization engine for this project is `Ada v2`.

## 🛠️ Project Architecture
Verba is built on three primary components:

- Weaviate Database: You have the option to host on Weaviate Cloud Service (WCS) or run it locally.
- FastAPI Endpoint: Acts as the communication bridge between the Large Language Model provider and the Weaviate database.
- React Frontend (Static served through FastAPI): Offers an interactive UI to display and interact with your data.
Development 

>Note: If you're planning to modify the frontend, ensure you have Node.js version >=18.16.0 installed. For more details on setting up the frontend, check out the Frontend README.

## 💖 Open Source Contribution

Your contributions are always welcome! Feel free to contribute ideas, feedback, or create issues and bug reports if you find any! Visit our [Weaviate Community Forum](https://forum.weaviate.io/) if you need any help!

