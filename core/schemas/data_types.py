# core/schemas/data_types.py
from pydantic import BaseModel, Field
from typing import Literal, Optional

class DocumentChunk(BaseModel):
    """
    Represents a parsed document chunk (1 Image, 1 Excel Sheet, or 1 Text Chunk).
    This is the input material for the Extractor Agent.
    """
    chunk_type: Literal["text", "image", "table"]
    content: str = Field(..., description="Content String, Markdown Table, or Base64 Image")
    file_name: str
    page_number: Optional[int] = None
    
    def get_context_description(self) -> str:
        """Utility function to help the Agent understand what it is reading."""
        loc = f"Page {self.page_number}" if self.page_number else "Entire file"
        return f"[Document: {self.file_name} | Location: {loc} | Format: {self.chunk_type}]"

class TaskContext(BaseModel):
    """
    Stores the context of the entire current Task. 
    Avoids passing too many discrete parameters between functions.
    """
    task_id: str
    original_prompt: str
    chunks: list[DocumentChunk] = []