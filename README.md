# Verba 
## 🐕 The Golden RAGtriever

Welcome to Verba: The Golden RAGtriever, an open-source initiative designed to offer a streamlined, user-friendly interface for Retrieval-Augmented Generation (RAG) applications. In just a few easy steps, dive into your data and make meaningful interactions!

```pip install goldenverba```

[![Weaviate](https://img.shields.io/static/v1?label=powered%20by&message=Weaviate%20%E2%9D%A4&color=green&style=flat-square)](https://weaviate.io/) 
[![PyPi downloads](https://static.pepy.tech/personalized-badge/goldenverba?period=total&units=international_system&left_color=grey&right_color=orange&left_text=pip%20downloads)](https://pypi.org/project/goldenverba/) [![Docker support](https://img.shields.io/badge/Docker_support-%E2%9C%93-4c1?style=flat-square&logo=docker&logoColor=white)](https://docs.docker.com/get-started/) [![Demo](https://img.shields.io/badge/Check%20out%20the%20demo!-yellow?&style=flat-square&logo=react&logoColor=white)](https://verba.weaviate.io/)

![Demo of Verba](https://github.com/weaviate/Verba/blob/main/img/verba.gif)

## 🎯 What Is Verba?
Verba is more than just a tool—it's a personal assistant for querying and interacting with your data. Have questions about your documents? Need to cross-reference multiple data points? Want to gain insights from your existing knowledge base? Verba makes it all possible through the power of Weaviate and Large Language Models (LLMs)!

## ⚙️ Under the Hood
Built on top of Weaviate's state-of-the-art Generative Search technology, Verba fetches relevant context from your documents to answer queries. It leverages the computational strength of LLMs to offer comprehensive, contextually relevant answers. All of this is conveniently accessible through Verba's intuitive user interface.

## 💡 Effortless Data Import with Weaviate
Verba offers seamless data import functionality, supporting a diverse range of file types including `.txt`, `.md`, and more. Before feeding your data into Weaviate, our system handles chunking and vectorization to optimize it for search and retrieval.

> 🔧 Work in Progress: We are actively developing a data cleaning pipeline for custom datasets. Until then, please ensure your data is clean and well-structured before importing it into Weaviate.

## 💥 Advanced Query Resolution with Hybrid and Generative Search
Harness the power of Weaviate's generate module and hybrid search features when using Verba. These advanced search techniques sift through your documents to identify contextually relevant fragments, which are then used by Large Language Models to formulate comprehensive answers to your queries.

## 🔥 Accelerate Queries with Semantic Cache
Verba utilizes Weaviate's Semantic Cache to embed both the generated results and queries, making future searches incredibly efficient. When you ask a question, Verba will first check the Semantic Cache to see if a semantically identical query has already been processed.

# ✨ Getting Started with Verba

This section outlines various methods to set up and deploy Verba, so you can choose the one that fits you best:

- Deploy with `pip`
- Build from Source
- Use Docker for Deployment

**Prerequisites**: If you're not using Docker, ensure that you have Python >=3.9.0 installed on your system.

**🔑 API Key Requirement**: Regardless of the deployment method, you'll need an OpenAI API key to enable data ingestion and querying features. You can specify this by either creating a .env file when cloning the project, or by storing the API key in your system environment variables.

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

2. **Deploy using Docker**
- ```docker-compose up```

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

