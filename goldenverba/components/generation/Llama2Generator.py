from goldenverba.components.generation.interface import Generator
from wasabi import msg
import asyncio
import os


class Llama2Generator(Generator):
    """
    Llama2Generator Generator
    """

    def __init__(self):
        super().__init__()
        self.name = "Llama2Generator"
        self.description = "Generator using Meta's Llama-2-7b-chat-hf model"
        self.requires_library = ["huggingface_hub", "transformers"]
        self.requires_env = ["HF_TOKEN", "LLAMA2-7B-CHAT-HF"]
        self.streamable = True
        self.model = None
        self.tokenizer = None
        self.device = None
        if os.environ.get("LLAMA2-7B-CHAT-HF", False):
            try:
                from transformers import AutoTokenizer, AutoModelForCausalLM
                import torch

                def get_device():
                    if torch.cuda.is_available():
                        msg.info("CUDA is available. Using CUDA...")
                        return torch.device("cuda")
                    elif (
                        torch.backends.mps.is_available()
                    ):  # Assuming torch.has_mps is a function to check for MPS availability
                        msg.info("MPS is available. Using MPS...")
                        return torch.device("mps")
                    else:
                        msg.info("Neither CUDA nor MPS is available. Using CPU...")
                        return torch.device("cpu")

                self.device = get_device()

                self.model = AutoModelForCausalLM.from_pretrained(
                    "meta-llama/Llama-2-7b-chat-hf",
                    device_map=self.device,
                )
                self.tokenizer = AutoTokenizer.from_pretrained(
                    "meta-llama/Llama-2-7b-chat-hf",
                    device_map=self.device,
                )
                self.model = self.model.to(self.device)
                msg.info("Loading Llama Model")
            except Exception as e:
                msg.warn(str(e))

    async def generate_stream(
        self,
        queries: list[str],
        context: list[str],
        conversation: dict = {},
    ) -> str:
        """Generate an answer based on a list of queries and list of contexts, include conversational context
        @parameter: queries : list[str] - List of queries
        @parameter: context : list[str] - List of contexts
        @parameter: conversation : dict - Conversational context
        @returns str - Answer generated by the Generator
        """

        messages = self.prepare_messages(queries, context, conversation)

        try:
            import torch

            prompt = messages
            output_length = 200

            # Ensure the tokenizer has a padding token defined
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            input = self.tokenizer(
                prompt,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=3500,  # Specify a max_length value
            )

            input = {k: v.to(self.device) for k, v in input.items()}
            attention_mask = input.get(
                "attention_mask", None
            )  # Get the attention mask, if provided
            input_len = input["input_ids"].shape[1]
            msg.info(f"Tokenized finished with {input_len} tokens")

            position_ids = torch.arange(
                0, input_len, dtype=torch.long, device=self.device
            ).unsqueeze(0)

            for output_len in range(output_length):
                updated_position_ids = torch.arange(
                    0, input_len + output_len, dtype=torch.long, device=self.device
                ).unsqueeze(0)
                output = await asyncio.to_thread(
                    lambda: self.model.generate(
                        input_ids=input["input_ids"],
                        attention_mask=attention_mask,
                        position_ids=updated_position_ids,
                        max_length=input_len + output_len + 1,
                        do_sample=True,
                        temperature=0.1,
                        pad_token_id=self.tokenizer.pad_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                    )
                )
                current_token_id = output[0][-1]
                if current_token_id == self.tokenizer.eos_token_id:
                    break
                current_token = self.tokenizer.convert_ids_to_tokens(
                    [current_token_id], skip_special_tokens=False
                )
                if type(current_token) == list:
                    current_token = " ".join(current_token)
                current_token = current_token.replace("<0x0A>", "\n").replace("▁", " ")
                # Update input for next iteration
                input["input_ids"] = torch.cat(
                    (input["input_ids"], current_token_id.view(1, 1)), dim=1
                )
                attention_mask = torch.cat(
                    (
                        attention_mask,
                        torch.ones((1, 1), dtype=torch.long, device=self.device),
                    ),
                    dim=1,
                )  # Update the attention_mask
                position_ids = torch.cat(
                    (
                        position_ids,
                        torch.tensor([[input_len + output_len]], device=self.device),
                    ),
                    dim=1,
                )
                yield {
                    "message": current_token,
                    "finish_reason": "",
                }
            yield {
                "message": "",
                "finish_reason": "stop",
            }

        except Exception as e:
            raise e

    def prepare_messages(self, queries, context, conversation):
        llama_prompt = f"""
        <s>[INST] <<SYS>>
        You are a Retrieval Augmented Generation chatbot. Answer user queries using only the provided context. If the context does not provide enough information, say so. If the answer requires code examples encapsulate them with ```programming-language-name ```. Don't do pseudo-code. \n<</SYS>>\n\n
        """

        query = " ".join(queries)
        user_context = " ".join(context)

        llama_prompt += (
            f"Answer this query: '{query}' with this context: {user_context} [/INST] "
        )

        return llama_prompt
