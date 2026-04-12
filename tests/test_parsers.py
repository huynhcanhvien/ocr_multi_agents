import pytest
from pathlib import Path
from PIL import Image
from core.parsers.file_router import parse_file
from core.parsers.vision_extractor import extract_vision_chunks
from core.exceptions.agent_errors import ParsingError

def test_parse_invalid_file():
    """Check handling of non-existent / structurally corrupted files"""
    # PyMuPDF or PIL will throw Exception on missing/corrupted file load, 
    # extract_vision_chunks must handle and raise ParsingError
    with pytest.raises(ParsingError):
        parse_file("thu_muc_ao/file_ma.pdf")

def test_extract_vision_chunks_image(tmp_path):
    """Check capability to partition and convert Base64 for static image"""
    image_path = tmp_path / "test_anh.jpg"
    
    # Create a red 100x100px image with PIL
    img = Image.new('RGB', (100, 100), color='red')
    img.save(image_path)
    
    # Pass to file_router (It will route to vision_extractor)
    chunks = parse_file(str(image_path))
    
    assert len(chunks) == 1, "Single image yields only 1 chunk"
    assert chunks[0].chunk_type == "image", "Chunk must be labeled as image"
    assert chunks[0].file_name == "test_anh.jpg"
    assert chunks[0].page_number == 1
    assert isinstance(chunks[0].content, str), "Base64 must be a string format"
    assert len(chunks[0].content) > 50, "Base64 structure was generated"

def test_parse_text_formats(tmp_path):
    """Check handling of text formats (docx, txt)"""
    import docx
    
    # Create mock content for .docx
    file_docx = tmp_path / "tailieu.docx"
    doc = docx.Document()
    doc.add_paragraph("This is a Word test text line.")
    doc.save(file_docx)
    
    chunks_docx = parse_file(str(file_docx))
    assert len(chunks_docx) == 1
    assert "This is a Word test text line" in chunks_docx[0].content
    assert chunks_docx[0].chunk_type == "text"
    
    # Create test for .txt
    file_txt = tmp_path / "tailieu.txt"
    file_txt.write_text("Mock Text Test Data", encoding="utf-8")
    
    chunks_txt = parse_file(str(file_txt))
    assert len(chunks_txt) == 1
    assert "Mock Text Test Data" in chunks_txt[0].content

    # Create test for .doc (mock binary format)
    file_doc = tmp_path / "tailieu.doc"
    # Write mock bytes with some meaningful text to test raw-text fallback mechanism
    file_doc.write_bytes(b"\x00\x01\x02Fallback_word\x04\x05 \xFF \xFE text")
    
    chunks_doc = parse_file(str(file_doc))
    assert len(chunks_doc) == 1
    assert "Fallback_word" in chunks_doc[0].content
    assert "text" in chunks_doc[0].content

def test_parse_unsupported_format(tmp_path):
    """Check handling of strange formats (e.g. .psd)"""
    file_path = tmp_path / "tailieu.psd"
    file_path.write_text("Mock junk data", encoding="utf-8")
    
    # By design in file_router, unsupported formats return an empty list []
    chunks = parse_file(str(file_path))
    assert len(chunks) == 0, "If unsupported, must skip and return empty"
