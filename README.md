# Verba 
## 🐕 The Golden RAGtriever

Welcome to Verba The Golden RAGtriever, an open-source project aimed at providing an easy usable retrieval augmented generation (RAG) app. Use it to interact with your data in just a handful of steps!

[![Weaviate](https://img.shields.io/static/v1?label=powered%20by&message=Weaviate%20%E2%9D%A4&color=green&style=flat-square)](https://weaviate.io/) [![Demo](https://img.shields.io/badge/Check%20out%20the%20demo!-yellow?&style=flat-square&logo=react&logoColor=white)](https://verba-golden-ragtriever.onrender.com/)

![Demo of Verba](https://github.com/weaviate/Verba/blob/main/img/verba.gif)

> Verba is a WIP project and many important features and updates are on their way!

## 🎯 Overview

Verba provides an interface for importing and querying your data. You can ask questions about your documents and discuss different data points.
It leverages Weaviate together with Generative Search to retrieve relevant document pieces and uses LLMs to power the answer to your query. Verba aims to support popular RAG solutions such as Llama Index, Langchain, Haystack, and more!

### 💡 Import your data to Weaviate

Verba supports importing different data types (.txt, .md, etc.) into Weaviate, chunking and vectorizing them beforehand.

> Currently, there is no data cleaning pipeline for custom data (WIP). Make sure that your data is in a good state before feeding them into Weaviate

### 💥 Hybrid- and Generative Search to answer your queries 

Verba uses Weaviate's `generate` module and `hybrid search` to fetch relevant document pieces and generate an answer to your query based on their context. 

### 🔥 Semantic Cache to speed up your process

We embed the generated results and queries to Weaviate, and use it as a `Semantic Cache`.
This method is advantageous as it enables Verba to return results from queries that are semantically equal to the new query. This method allows us to gain much more from generated results than traditional string matching would permit. It's a simple yet potent solution that enhances the efficiency of the search process.

## ✨ Quickstart

1. **Set up your Weaviate cluster:**
- **OPTION 1** Create a cluster in WCS (for more details, refer to the [Weaviate Cluster Setup Guide](https://weaviate.io/developers/wcs/guides/create-instance))
- **OPTION 2** Use Docker-Compose to setup a cluster locally [Weaviate Docker Guide](https://weaviate.io/developers/weaviate/installation/docker-compose)

2. **Set environment variables:**
- Create a `.env` file to set the following variables

- ```WEAVIATE_URL=http://your-weaviate-server:8080```
- ```WEAVIATE_API_KEY=your-weaviate-database-key```
- ```OPENAI_API_KEY=your-openai-api-key```
- (OPTIONAL) ```GITHUB_TOKEN=your-token``` (Only if you want to ingest Weaviate data)
> You can use `.env` files (https://github.com/theskumar/python-dotenv) or set the variables to your system

3. **Create a new Python virtual environment:**
- Make sure you have python `>=3.8.0` installed
- ```python3 -m venv env```
- ```source env/bin/activate```

4. **Install dependencies:**
- Install Verba with the following command:
- ```pip install -e .```

5. **Start Verba with:**
- ```verba start```


## 📦 Importing your data

Please note, that importing data will generate cost for your specified OpenAI access key.
> Currently, you can only import simple files such as (.txt, .md, .mdx). Other data types are WIP.

> Basic CRUD-Operations and interactions through the interface are WIP

**01 Import your data:**
- Insert your data into the `./data` folder (currently only supporting .txt, .md, .mdx files). The folder contains example data about Minecraft.
- Use `verba import` to import all data inside the folder
- `verba import --model gpt-4` 
> You can also specify the OpenAI model, default is set to gpt-3.5-turbo

> Using this command will remove all existing documents, chunks, and cache entries in your Weaviate cluster

> Enhanced CRUD operations are WIP

**02 Run verba**
- Run verba with `verba start` and go to `localhost:8000`.


**(OPTIONAL) Importing Weaviate:**
- You can also import all documentation, blog posts, video transcripts, etc from Weaviate. You need to specify your `GITHUB_TOKEN` environment variable to the `.env` file
- Use `verba weaviate` script to download, process, and import Weaviate data to your cluster.
- `verba weaviate --model gpt-4`

## 💰 Large Language Model (LLM) Costs

Verba currently only supports OpenAI models. By default, any costs associated with using this service will be billed to the access key that you provide. Processes that will generate cost are the data embedding and answer generation part. The default vectorizer for this project is `Ada v2`

## 🛠️ Project Structure

Verba is structured in three main components:

1. A Weaviate database (either cluster hosted on WCS or local).
2. A FastAPI endpoint facilitating communication between the LLM provider and database.
3. An interactive React frontend for displaying the information.

> If you want to edit the frontend itself, make sure you have Node (`>=18.16.0`) installed.

## 💖 Open Source Contribution

Your contributions are always welcome! Feel free to contribute ideas, feedback, or create issues and bug reports if you find any! Please adhere to the code guidelines that include formatting, linting, and testing.

## 🛣️ Roadmap

- Add more robustness to the app
    - Write a lot of tests
- Improve data interaction with the app
    - More CRUD operations, interact with the frontend to ingest data
- Add more retrieval algorithms (e.g. LlamaIndex, LangChain, etc.)
- Add more datatypes (.pdf, etc.)
- Connect to datasources
- Support fast changing data
