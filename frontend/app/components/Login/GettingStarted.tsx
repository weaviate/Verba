"use client";

import React, { useEffect, useRef } from "react";

interface GettingStartedComponentProps {}

const GettingStartedComponent: React.FC<
  GettingStartedComponentProps
> = ({}) => {
  const dialogRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    if (dialogRef.current) {
      dialogRef.current.showModal();
    }
  }, []);

  return (
    <dialog id={"Getting-Started-Modal"} className="modal" ref={dialogRef}>
      <div className="modal-box w-11/12 max-w-5xl">
        <div className="hero">
          <div className="hero-content flex-row">
            <div className="text-center lg:text-left">
              <h1 className="text-5xl font-bold">Welcome to Verba</h1>
              <h2 className="text-2xl mt-2">Your Open Source RAG App</h2>
              <p className="py-6">
                Verba is an open-source application designed to offer an
                end-to-end, streamlined, and user-friendly interface for
                Retrieval-Augmented Generation (RAG) out of the box. In just a
                few easy steps, explore your datasets and extract insights with
                ease, either locally with HuggingFace and Ollama or through LLM
                providers such as Anthrophic, Cohere, and OpenAI.
              </p>
              <p className="py-6">
                Learn more by visiting our GitHub repository, our blog post, or
                our video on Verba. Verba is currently still in development. If
                you have any questions or find issues, please reach out to us on
                GitHub.
              </p>
              <div className="flex flex-col sm:flex-row gap-2">
                <button
                  className="btn border-none shadow-none bg-button-verba hover:bg-button-hover-verba text-text-alt-verba hover:text-text-verba"
                  onClick={() =>
                    window.open("https://github.com/weaviate/verba", "_blank")
                  }
                >
                  GitHub
                </button>
                <button
                  className="btn border-none shadow-none bg-button-verba hover:bg-button-hover-verba text-text-alt-verba hover:text-text-verba"
                  onClick={() =>
                    window.open(
                      "https://www.youtube.com/watch?v=swKKRdLBhas",
                      "_blank"
                    )
                  }
                >
                  YouTube
                </button>
                <button
                  className="btn border-none shadow-none bg-button-verba hover:bg-button-hover-verba text-text-alt-verba hover:text-text-verba"
                  onClick={() =>
                    window.open(
                      "https://weaviate.io/blog/verba-open-source-rag-app",
                      "_blank"
                    )
                  }
                >
                  Blog Post
                </button>
              </div>
            </div>
            <div className="shrink-0">
              <img
                src="https://raw.githubusercontent.com/weaviate/Verba/main/img/thumbnail.png"
                alt="Verba AI"
                width={400}
                className="rounded-lg shadow-2xl"
              />
            </div>
          </div>
        </div>
        <div className="modal-action mt-6">
          <form method="dialog">
            <button className="btn text-text-alt-verba hover:text-text-verba bg-button-verba border-none hover:bg-primary-verba">
              Lets get started ♥
            </button>
          </form>
        </div>
      </div>
    </dialog>
  );
};

export default GettingStartedComponent;
