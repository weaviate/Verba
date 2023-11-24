from goldenverba.components.generation.GPT4Generator import GPT4Generator


class GPT3Generator(GPT4Generator):
    """
    GPT3 Generator.
    """

    def __init__(self):
        super().__init__()
        self.name = "GPT3Generator"
        self.description = "Generator using OpenAI's GPT-3.5-turbo-1106 model"
        self.model_name = "gpt-3.5-turbo-1106"
