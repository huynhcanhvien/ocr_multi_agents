# core/parsers/file_router.py
from pathlib import Path
from ..utils.logger import agent_logger
from .table_extractor import extract_tables
from .vision_extractor import extract_vision_chunks
from .text_extractor import extract_text_chunks
from ..schemas.data_types import DocumentChunk

def parse_file(file_path: str) -> list[DocumentChunk]:
    """
    Universal routing system.
    Receives file downloaded from DataProvider -> Returns a list of standardized DocumentChunks.
    """
    path = Path(file_path)
    agent_logger.info(f"Analyzing file format: {path.name}")
    
    ext = path.suffix.lower()
    
    if ext in ['.xlsx', '.xls', '.csv']:
        return extract_tables(file_path)
        
    elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.tiff', '.tif']:
        return extract_vision_chunks(file_path)
        
    elif ext in ['.docx', '.doc', '.txt']:
        return extract_text_chunks(file_path)
        
    elif ext == '.pdf':
        # Note: Currently converting all PDFs to images to address your Japanese Prompt requirements.
        # If there are pure text files in the future, you can use fitz.get_text() here.
        return extract_vision_chunks(file_path)
        
    else:
        agent_logger.warning(f"Format {ext} not supported for file {path.name}. Skipping.")
        return []