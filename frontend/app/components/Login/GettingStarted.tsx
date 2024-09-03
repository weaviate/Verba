"use client";

import React, { useEffect, useRef } from "react";
import VerbaButton from "../Navigation/VerbaButton";
import { FaGithub } from "react-icons/fa";
import { FaYoutube } from "react-icons/fa";
import { IoDocumentTextSharp } from "react-icons/io5";
import { FaHeart } from "react-icons/fa";

interface GettingStartedComponentProps {
  addStatusMessage: (
    message: string,
    type: "INFO" | "WARNING" | "SUCCESS" | "ERROR"
  ) => void;
}

const GettingStartedComponent: React.FC<GettingStartedComponentProps> = ({
  addStatusMessage,
}) => {
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
              <h1 className="text-2xl md:text-5xl font-bold">
                Welcome to Verba
              </h1>
              <h2 className="text-lg md:text-2xl mt-2">
                Your Open Source RAG App
              </h2>
              <p className="py-6 text-sm md:text-base">
                Verba is an open-source application designed to offer an
                end-to-end, streamlined, and user-friendly interface for
                Retrieval-Augmented Generation (RAG) out of the box. In just a
                few easy steps, explore your datasets and extract insights with
                ease, either locally with HuggingFace and Ollama or through LLM
                providers such as Anthrophic, Cohere, and OpenAI.
              </p>
              <p className="py-6 text-sm md:text-base">
                Learn more by visiting our GitHub repository, our blog post, or
                our video on Verba. Verba is currently still in development. If
                you have any questions or find issues, please reach out to us on
                GitHub.
              </p>
              <div className="flex flex-col md:flex-row gap-2">
                <VerbaButton
                  title="GitHub"
                  Icon={FaGithub}
                  onClick={() =>
                    window.open("https://github.com/weaviate/verba", "_blank")
                  }
                />
                <VerbaButton
                  title="YouTube"
                  Icon={FaYoutube}
                  onClick={() =>
                    window.open(
                      "https://www.youtube.com/watch?v=swKKRdLBhas",
                      "_blank"
                    )
                  }
                />
                <VerbaButton
                  title="Blog Post"
                  Icon={IoDocumentTextSharp}
                  onClick={() =>
                    window.open(
                      "https://weaviate.io/blog/verba-open-source-rag-app",
                      "_blank"
                    )
                  }
                />
              </div>
            </div>
            <div className="hidden md:block shrink-0">
              <img
                src="https://raw.githubusercontent.com/weaviate/Verba/main/img/thumbnail.png"
                alt="Verba AI"
                width={400}
                className="rounded-lg shadow-2xl"
              />
            </div>
          </div>
        </div>
        <div className="modal-action mt-6 justify-center md:justify-end">
          <form method="dialog">
            <VerbaButton
              title="Let's get started"
              type="submit"
              selected={true}
              onClick={() => {
                addStatusMessage(
                  "Achievement unlocked: Welcome to Verba!",
                  "SUCCESS"
                );
              }}
              selected_color="bg-primary-verba"
              Icon={FaHeart}
            />
          </form>
        </div>
      </div>
    </dialog>
  );
};

export default GettingStartedComponent;
