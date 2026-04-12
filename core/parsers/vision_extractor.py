# core/parsers/vision_extractor.py
import base64
import fitz  # PyMuPDF
from PIL import Image
import io
from pathlib import Path
from ..utils.logger import agent_logger
from ..exceptions.agent_errors import ParsingError
from ..schemas.data_types import DocumentChunk

def encode_image_to_base64(image: Image.Image, max_size: int = 1500) -> str:
    """Compress image if too large and convert to Base64."""
    # Resize maintaining aspect ratio if image is larger than max_size
    if max(image.size) > max_size:
        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    
    # Convert to RGB (remove Alpha channel if PNG) to compress as lightweight JPEG
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
        
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=85)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def extract_vision_chunks(file_path: str) -> list[DocumentChunk]:
    path = Path(file_path)
    chunks = []
    
    try:
        # 1. If it's a direct image file
        if path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.tiff', '.tif']:
            img = Image.open(file_path)
            b64_str = encode_image_to_base64(img)
            chunks.append(DocumentChunk(
                chunk_type="image", content=b64_str, file_name=path.name, page_number=1
            ))
            agent_logger.success(f"Encoded image {path.name}.")
            
        # 2. If it's a PDF file, split each page into an image
        elif path.suffix.lower() == '.pdf':
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                # Increase DPI slightly for more accurate OCR (zoom=2 is sufficiently sharp)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                b64_str = encode_image_to_base64(img)
                chunks.append(DocumentChunk(
                    chunk_type="image", content=b64_str, file_name=path.name, page_number=page_num + 1
                ))
            doc.close()
            agent_logger.success(f"Split {path.name} into {len(chunks)} Base64 images.")
            
        return chunks
        
    except Exception as e:
        agent_logger.error(f"Error processing image {path.name}: {e}")
        raise ParsingError(f"Cannot process image/PDF: {str(e)}")