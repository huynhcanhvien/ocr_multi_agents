# core/schemas/data_types.py
from pydantic import BaseModel
from typing import Literal, Optional

class DocumentChunk(BaseModel):
    """A chunk of data that has been parsed to pass into the AI."""
    chunk_type: Literal["text", "image", "table"]
    content: str  # Contains Text, Markdown or Image Base64 string
    file_name: str
    page_number: Optional[int] = None
    
    # Metadata to help the Agent understand context (e.g., "This is table on page 3")
    def get_context_description(self) -> str:
        loc = f"Page {self.page_number}" if self.page_number else "Entire file"
        return f"[File: {self.file_name} | Location: {loc} | Type: {self.chunk_type}]"
    