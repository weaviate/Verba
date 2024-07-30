import { RAGConfig } from "../RAG/types";

export const closeOnClick = () => {
  const elem = document.activeElement;
  if (elem && elem instanceof HTMLElement) {
    elem.blur();
  }
};
