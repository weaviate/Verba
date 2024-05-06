import { FormattedDocument } from "./types";

export function splitDocument(
  fullText: string,
  searchSubstring: string | null
): FormattedDocument {
  if (searchSubstring === null || searchSubstring === "") {
    const beginning = fullText;
    const substring = "";
    const ending = "";

    return { beginning, substring, ending };
  }

  const startIndex = fullText.indexOf(searchSubstring);
  if (startIndex === -1) {
    // Substring not found, handle as appropriate, maybe return null or the full text as beginning
    return { beginning: fullText, substring: "", ending: "" };
  }

  const endIndex = startIndex + searchSubstring.length;

  const beginning = fullText.substring(0, startIndex);
  const substring = fullText.substring(startIndex, endIndex);
  const ending = fullText.substring(endIndex);

  return { beginning, substring, ending };
}
