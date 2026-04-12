# core/parsers/text_extractor.py
import os
import tempfile
from pathlib import Path
import docx
from ..utils.logger import agent_logger
from ..exceptions.agent_errors import ParsingError
from ..schemas.data_types import DocumentChunk

def extract_text_chunks(file_path: str) -> list[DocumentChunk]:
    path = Path(file_path)
    chunks = []
    
    try:
        if path.suffix.lower() == '.docx':
            doc = docx.Document(file_path)
            full_text = []
            for para in doc.paragraphs:
                if para.text.strip():
                    full_text.append(para.text.strip())
            
            # Read tables in Word document (if any)
            for table in doc.tables:
                for row in table.rows:
                    row_data = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_data:
                        full_text.append(" | ".join(row_data))
                        
            content = "\n".join(full_text)
            chunks.append(DocumentChunk(
                chunk_type="text",
                content=content,
                file_name=path.name,
                page_number=1
            ))
            agent_logger.success(f"Extracted text from Word file {path.name}.")
            
        elif path.suffix.lower() == '.doc':
            # Note: The old out-of-date .doc format (binary) is not officially supported by python-docx.
            # We will try a catch-all (in case the file is actually a docx but renamed to .doc)
            try:
                doc = docx.Document(file_path)
                full_text = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
                content = "\n".join(full_text)
                chunks.append(DocumentChunk(
                    chunk_type="text", content=content, file_name=path.name, page_number=1
                ))
                agent_logger.success(f"Read {path.name} via python-docx (since it is actually structured as XML).")
            except Exception:
                # If it's truly an old binary OLE .doc file, we use a trick to scan basic printable text
                agent_logger.warning(f"File {path.name} is old .doc format. Using fallback to read raw text...")
                with open(file_path, "rb") as f:
                    content_bytes = f.read()
                    
                import string
                # Filter out printable ASCII characters and basic Unicode characters
                printable = set(string.printable.encode())
                extracted = []
                for b in content_bytes:
                    if b in printable:
                        extracted.append(chr(b))
                    elif b > 127: # Blindly accept some possible utf-8 bytes
                        extracted.append(" ")
                        
                raw_string = "".join(extracted)
                # Clean up whitespaces
                words = [w for w in raw_string.split() if len(w) > 3]
                content = " ".join(words)
                
                if len(content) > 0:
                    chunks.append(DocumentChunk(
                        chunk_type="text", 
                        content=f"[WARNING: Read raw from .doc binary, text might be garbled or missing formatting]\n{content}", 
                        file_name=path.name, 
                        page_number=1
                    ))
                else:
                    raise ValueError("No text found after parsing raw binary.")

        elif path.suffix.lower() == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            chunks.append(DocumentChunk(
                chunk_type="text", content=content, file_name=path.name, page_number=1
            ))
            agent_logger.success(f"Extracted text from file {path.name}.")

        return chunks
        
    except Exception as e:
        agent_logger.error(f"Error parsing text file {path.name}: {e}")
        raise ParsingError(f"Cannot parse word/txt file: {str(e)}")
