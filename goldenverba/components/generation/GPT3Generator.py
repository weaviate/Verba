from goldenverba.components.generation.GPT4Generator import GPT4Generator


class GPT3Generator(GPT4Generator):
    """
    GPT3 Generator.
    """

    def __init__(self):
        super().__init__()
        self.name = "GPT3"
        self.description = "Generator using OpenAI's gpt-3.5-turbo-0125 model"
        self.model_name = "gpt-3.5-turbo-0125"
