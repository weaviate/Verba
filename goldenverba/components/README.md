# Components



# Error Cases

- Chunk size too big
-> Hardcapped to 2000 tokens (tiktoken)

# Notes on LLama
- Request Meta and Huggingface
- Huggingface Account, add Huggingface Token, + transformers
- 10GB, pip install accelerate, saved within global cache, not dependent on virtualenv


text-generation-launcher --model-id meta-llama/Llama-2-7b-chat-hf --port 8080 --disable-custom-kernels --sharded false --dtype bfloat16 --cuda-memory-fraction 0.0