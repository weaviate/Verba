# Verba (WIP)

Welcome to the Verba, an open-source project aimed at providing an easy usable retrieval augmented generation (RAG) system. Use it to interact with your data in just a handful of steps! 

[![Weaviate](https://img.shields.io/static/v1?label=%E2%9D%A4%20made%20with&message=Weaviate&color=green&style=flat-square)](https://weaviate.io/) 


## 🎯 Overview

Verba provides an interface for importing and querying your data. You can ask questions about your documents and discuss different data points.
It leverages Weaviate together with Generative Search to retrieve relevant document pieces and uses LLM to power the answer to your query. Verba aims to support popular RAG solutions such as Llama Index, Langchain, Haystack, and more!

### 💡 Import your data to Weaviate (WIP)

Verba provides an interface to load different data types (.txt, .md, .pdf, etc.) into Weaviate, cleaning, chunking and vectorizing them beforehand.


### 🔎 Semantic Search and more on your documents (WIP)

Verba supports all Weaviate search techniques such as BM25-, Vector-, and Hybrid Search to browse through your documents and ask questions.

### 💥 Generative Search to answer your queries (WIP)

Verba uses Weaviate's generate module to look at the retrieved document pieces and form an answer to your query. 

### 🔥 Semantic Cache to speed up your process (WIP)

We embed the generated results and queries to Weaviate, and use it as a `Semantic Cache`.
This method is advantageous as it enables Verba to return results from queries that are semantically equal to the new query. This method allows us to gain much more from generated results than traditional string matching would permit. It's a simple yet potent solution that enhances the efficiency of the search process.

## 💰 Large Language Model (LLM) Costs

Verba supports multiple LLM providers such as OpenAI, Cohere, Huggingface, and more. By default, any costs associated with using these services will be billed to the access key that you provide. Processes that will cost will be data embedding and answer generation.

## 🛠️ Project Structure

Verba is structured in three main components:

1. A Weaviate database (either cluster hosted on WCS or local).
2. A FastAPI endpoint facilitating communication between the LLM provider and database.
3. An interactive React frontend for displaying the information.

Make sure you have Python (`>=3.8.0`) and Node (`>=18.16.0`) installed.

## 📚 Getting Started

To kick-start with the Healthsearch Demo, please refer to the READMEs in the `Frontend` and `Backend` folders:

- [Frontend README](./frontend/README.md)
- [Backend README](./backend/README.md)

## 💡 Usage

Follow these steps to use the Healthsearch Demo:

1. Set up the Weaviate database, FastAPI backend, and the React frontend by following the instructions in their respective READMEs.
2. Launch the database, backend server, and the frontend application.
3. Use the Verba frontend to talk with you data

## 💖 Open Source Contribution

Your contributions are always welcome! Feel free to contribute ideas, feedback, or create issues and bug reports if you find any! Please adhere to the code guidelines that include formatting, linting, and testing.