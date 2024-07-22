from transformers import AutoTokenizer
from bs4 import BeautifulSoup, Tag
import tiktoken

def estimate_tokens(text, provider: str, model: str) -> int:
    if provider.lower() == "openai":
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    
    # elif provider.lower() in ["ollama", "groq"]:
    #     if model.startswith("llama3"):
    #         try:
    #             tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")
    #             tokens = tokenizer.tokenize(text)
    #             return len(tokens)
    #         except Exception as e:
    #             print(f"Tokenizer error: {e}.\nFalling back to character-based approximation.")
    #             return len(text) // 4
    #     else:
    #         return len(text) // 4
    
    else:
        return len(text) // 4


def chunk_dom(html, provider: str, model: str, max_token: int) -> list[Tag]:
        
    def count_descendants(node: Tag):
        return len(node.find_all())

    def traverse(node: Tag, indent="") -> list[Tag]:
        
        token_estimated = estimate_tokens(node.get_text(' ', True), provider, model) + len(node.find_all('a', href=True)) * 12
        
        print(f"{indent}{node.name} ({token_estimated})")
        if token_estimated <= max_token * 0.8:
            return [node]
        
        chunks: list[Tag] = []
        for child in node.children:
            if child.name is not None:
                chunks = chunks + traverse(child, indent + "    ")
        return chunks
                
    soup = BeautifulSoup(html, 'html.parser')
    return traverse(soup.html)
