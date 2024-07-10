from goldenverba.components.generation.GPT4Generator import GPT4Generator
from langchain_openai import ChatOpenAI


class GPT3Generator(GPT4Generator):
    """
    GPT3 Generator.
    """

    def __init__(self):
        super().__init__()
        self.name = "GPT3"
        self.description = "Generator using OpenAI's gpt-3.5-turbo-0125 model"
        self.model_name = "gpt-3.5-turbo-0125"

        # Reinitialize the ChatOpenAI with the new model name
        self.llm = ChatOpenAI(
            model_name=self.model_name,
            temperature=0.0,
            streaming=True,
            callbacks=self.llm.callbacks,  # Reuse the callbacks from the parent class
        )
