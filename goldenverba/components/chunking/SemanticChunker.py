import contextlib

from wasabi import msg
import re

with contextlib.suppress(Exception):
    from sklearn.metrics.pairwise import cosine_similarity

from goldenverba.components.chunk import Chunk
from goldenverba.components.interfaces import Chunker
from goldenverba.components.document import Document
from goldenverba.components.types import InputConfig
from goldenverba.components.interfaces import Embedding
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
        self.description = "Split documents based on semantic similarity based on Greg Kamradt's implementation"
        self.config = {
            "Breakpoint Percentile Threshold": InputConfig(
                type="number", value=55, description="Percentile Threshold to split and create a chunk, the lower the more chunks you get", values=[]
            ),
        }

    async def chunk(self, config: dict, documents: list[Document], embedder: Embedding, embedder_config: dict) -> list[Document]:

        breakpoint_percentile_threshold = int(config["Breakpoint Percentile Threshold"].value)

        for document in documents:

            print(f"Using {embedder.name}")

            # Skip if document already contains chunks
            if len(document.chunks) > 0:
                continue

            sentences = self.combine_sentences([{'sentence': x, 'index' : i} for i, x in enumerate(re.split(r'(?<=[.?!])\s+', document.content))])
            embeddings = await embedder.vectorize(embedder_config,[x['combined_sentence'] for x in sentences])
            for i, sentence in enumerate(sentences):
                sentence['combined_sentence_embedding'] = embeddings[i]

            distances, sentences = self.calculate_cosine_distances(sentences)

            breakpoint_distance_threshold = np.percentile(distances, breakpoint_percentile_threshold)
            indices_above_thresh = [i for i, x in enumerate(distances) if x > breakpoint_distance_threshold]

            # Initialize the start index
            start_index = 0

            # Create a list to hold the grouped sentences
            chunks = []

            # Iterate through the breakpoints to slice the sentences
            for index in indices_above_thresh:
                # The end index is the current breakpoint
                end_index = index

                # Slice the sentence_dicts from the current start index to the end index
                group = sentences[start_index:end_index + 1]
                combined_text = ' '.join([d['sentence'] for d in group])
                chunks.append(combined_text)
                
                # Update the start index for the next group
                start_index = index + 1

            # The last group, if any sentences remain
            if start_index < len(sentences):
                combined_text = ' '.join([d['sentence'] for d in sentences[start_index:]])
                chunks.append(combined_text)

            for i, chunk in enumerate(chunks):
                document.chunks.append(Chunk(
                    content=chunk,
                    chunk_id=i,
                ))

        return documents
    
    def combine_sentences(self, sentences, buffer_size=1):
        # Go through each sentence dict
        for i in range(len(sentences)):

            # Create a string that will hold the sentences which are joined
            combined_sentence = ''

            # Add sentences before the current one, based on the buffer size.
            for j in range(i - buffer_size, i):
                # Check if the index j is not negative (to avoid index out of range like on the first one)
                if j >= 0:
                    # Add the sentence at index j to the combined_sentence string
                    combined_sentence += sentences[j]['sentence'] + ' '

            # Add the current sentence
            combined_sentence += sentences[i]['sentence']

            # Add sentences after the current one, based on the buffer size
            for j in range(i + 1, i + 1 + buffer_size):
                # Check if the index j is within the range of the sentences list
                if j < len(sentences):
                    # Add the sentence at index j to the combined_sentence string
                    combined_sentence += ' ' + sentences[j]['sentence']

            # Then add the whole thing to your dict
            # Store the combined sentence in the current sentence dict
            sentences[i]['combined_sentence'] = combined_sentence

        return sentences
    
    def calculate_cosine_distances(self, sentences):
        distances = []
        for i in range(len(sentences) - 1):
            embedding_current = sentences[i]['combined_sentence_embedding']
            embedding_next = sentences[i + 1]['combined_sentence_embedding']
            
            # Calculate cosine similarity
            similarity = cosine_similarity([embedding_current], [embedding_next])[0][0]
            
            # Convert to cosine distance
            distance = 1 - similarity

            # Append cosine distance to the list
            distances.append(distance)

            # Store distance in the dictionary
            sentences[i]['distance_to_next'] = distance

        # Optionally handle the last sentence
        # sentences[-1]['distance_to_next'] = None  # or a default value

        return distances, sentences
