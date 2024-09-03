import contextlib

from wasabi import msg

with contextlib.suppress(Exception):
    from sklearn.metrics.pairwise import cosine_similarity

from goldenverba.components.chunk import Chunk
from goldenverba.components.interfaces import Chunker
from goldenverba.components.document import Document
from goldenverba.components.types import InputConfig
from goldenverba.components.interfaces import Embedding

import numpy as np


class SemanticChunker(Chunker):
    """
    SemanticChunker for Verba based on https://github.com/FullStackRetrieval-com/RetrievalTutorials/blob/main/tutorials/LevelsOfTextSplitting/5_Levels_Of_Text_Splitting.ipynb
    """

    def __init__(self):
        super().__init__()
        self.name = "Semantic"
        self.requires_library = ["sklearn"]
        self.description = (
            "Split documents based on semantic similarity or max sentences"
        )
        self.config = {
            "Breakpoint Percentile Threshold": InputConfig(
                type="number",
                value=80,
                description="Percentile Threshold to split and create a chunk, the lower the more chunks you get",
                values=[],
            ),
            "Max Sentences Per Chunk": InputConfig(
                type="number",
                value=20,
                description="Maximum number of sentences per chunk",
                values=[],
            ),
        }

    async def chunk(
        self,
        config: dict,
        documents: list[Document],
        embedder: Embedding | None = None,
        embedder_config: dict | None = None,
    ) -> list[Document]:
        

        breakpoint_percentile_threshold = int(
            config["Breakpoint Percentile Threshold"].value
        )
        max_sentences = int(config["Max Sentences Per Chunk"].value)

        for document in documents:

            # Skip if document already contains chunks
            if len(document.chunks) > 0:
                continue

            # Use spaCy's sentence segmentation
            sentences = [
                {"sentence": sent.text, "index": i}
                for i, sent in enumerate(document.spacy_doc.sents)
            ]
            sentences = self.combine_sentences(sentences)

            # If there's only one sentence, create a single chunk
            if len(sentences) == 1:
                document.chunks.append(
                    Chunk(
                        content=sentences[0]["sentence"],
                        chunk_id=0,
                        start_i=0,
                        end_i=len(document.content),
                        content_without_overlap=sentences[0]["sentence"]
                    )
                )
                continue

            msg.info(f"Generated {len(sentences)} sentences")

            embeddings = await embedder.vectorize(
                embedder_config, [x["combined_sentence"] for x in sentences]
            )

            msg.info(f"Generated {len(embeddings)} embeddings")

            for i, sentence in enumerate(sentences):
                sentence["combined_sentence_embedding"] = embeddings[i]

            distances, sentences = self.calculate_cosine_distances(sentences)

            breakpoint_distance_threshold = np.percentile(
                distances, breakpoint_percentile_threshold
            )

            chunks = []
            current_chunk = []
            char_is = []
            sentence_count = 0
            char_end_i = -1
            for i, sentence in enumerate(sentences):
                current_chunk.append(sentence["sentence"])
                sentence_count += 1

                # new chunk found (distance breakpoint not reached or reached max sentences)
                if (
                    i < len(distances) and distances[i] > breakpoint_distance_threshold
                ) or sentence_count >= max_sentences:
                    
                    chunk_text = " ".join(current_chunk)
                    chunks.append(chunk_text)

                    char_start_i = char_end_i + 1
                    char_end_i = char_start_i + len(chunk_text)
                    char_is.append((char_start_i, char_end_i))

                    current_chunk = []
                    sentence_count = 0

            # Add any remaining sentences as the last chunk
            if current_chunk:
                chunk_text = " ".join(current_chunk)
                chunks.append(chunk_text)
                char_is.append((char_end_i + 1, char_end_i + 1 + len(chunk_text)))

            for i, chunk in enumerate(chunks):
                document.chunks.append(
                    Chunk(
                        content=chunk,
                        chunk_id=i,
                        start_i=char_is[i][0],
                        end_i=char_is[i][1],
                        content_without_overlap=chunk,
                    )
                )

        return documents

    def combine_sentences(self, sentences, buffer_size=1):
        # Go through each sentence dict
        for i in range(len(sentences)):

            # Create a string that will hold the sentences which are joined
            combined_sentence = ""

            # Add sentences before the current one, based on the buffer size.
            for j in range(i - buffer_size, i):
                # Check if the index j is not negative (to avoid index out of range like on the first one)
                if j >= 0:
                    # Add the sentence at index j to the combined_sentence string
                    combined_sentence += sentences[j]["sentence"] + " "

            # Add the current sentence
            combined_sentence += sentences[i]["sentence"]

            # Add sentences after the current one, based on the buffer size
            for j in range(i + 1, i + 1 + buffer_size):
                # Check if the index j is within the range of the sentences list
                if j < len(sentences):
                    # Add the sentence at index j to the combined_sentence string
                    combined_sentence += " " + sentences[j]["sentence"]

            # Then add the whole thing to your dict
            # Store the combined sentence in the current sentence dict
            sentences[i]["combined_sentence"] = combined_sentence

        return sentences

    def calculate_cosine_distances(self, sentences):
        distances = []
        for i in range(len(sentences) - 1):
            embedding_current = sentences[i]["combined_sentence_embedding"]
            embedding_next = sentences[i + 1]["combined_sentence_embedding"]

            # Calculate cosine similarity
            similarity = cosine_similarity([embedding_current], [embedding_next])[0][0]

            # Convert to cosine distance
            distance = 1 - similarity

            # Append cosine distance to the list
            distances.append(distance)

            # Store distance in the dictionary
            sentences[i]["distance_to_next"] = distance

        # Optionally handle the last sentence
        # sentences[-1]['distance_to_next'] = None  # or a default value

        return distances, sentences
