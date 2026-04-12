# core/utils/tokens.py
import tiktoken
from ..config.settings import settings
from .logger import agent_logger

def count_tokens(text: str, model: str = settings.GPT_MODEL_NAME) -> int:
    """Accurately count the number of tokens in a text string for the current model."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # If model is too new and tiktoken hasn't updated yet, fallback to o200k_base for gpt-4o
        encoding = tiktoken.get_encoding("o200k_base") 
    
    return len(encoding.encode(text))

def truncate_text(text: str, max_tokens: int = settings.MAX_TOKENS_PER_CHUNK) -> str:
    """Truncate text if it exceeds the token limit (to avoid API errors)."""
    encoding = tiktoken.get_encoding("o200k_base")
    encoded_text = encoding.encode(text)
    
    if len(encoded_text) <= max_tokens:
        return text
        
    agent_logger.warning(f"Text too long ({len(encoded_text)} tokens). Truncating down to {max_tokens} tokens.")
    return encoding.decode(encoded_text[:max_tokens])