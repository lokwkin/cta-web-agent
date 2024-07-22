import tiktoken
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.pre_tokenizers import Whitespace


def estimate_tokens(text, provider: str, model: str):
    if provider.lower() == "openai":
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    
    elif provider.lower() in ["ollama", "groq"]:
        # Using a BPE tokenizer for LLaMA-like models
        if model.startswith("llama3"):
            try:
                tokenizer = Tokenizer(BPE())
                tokenizer.pre_tokenizer = Whitespace()
                return len(tokenizer.encode(text).tokens)
            except Exception as e:
                print(f"Tokenizer error: {e}. Falling back to character-based approximation.")
                return len(text) // 4
        else:
            return len(text) // 4
    
    else:
        # Fallback for unsupported providers
        return len(text) // 4
