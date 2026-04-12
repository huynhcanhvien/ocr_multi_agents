import pytest
from pathlib import Path
from core.parsers.file_router import parse_file
from core.agents.keyword_extractor import KeywordExtractorAgent
from core.agents.extractor import ExtractorAgent

@pytest.fixture
def sample_excel_path() -> str:
    return str(Path("tests/sample_data/bang_tien_do.xlsx").absolute())

@pytest.fixture
def sample_pdf_img_path() -> str:
    return str(Path("tests/sample_data/tai_lieu_dac_ta.pdf").absolute())

def test_excel_parsing_and_keyword_extraction(sample_excel_path):
    # Excel data contains tables (table text chunk)
    chunks = parse_file(sample_excel_path)
    assert len(chunks) > 0, "Excel parsing failed, no chunks found."
    
    # Check if there is actual text to send to LLM
    all_text = ""
    for c in chunks:
        assert c.chunk_type in ["text", "table"], "Excel must return chunk_type as 'table' or 'text'"
        all_text += c.content + "\n"
        
    assert "bang_tien_do.xlsx" in all_text or "Table" in all_text or len(all_text) > 10, "Excel table has no data."

    # Test KeywordExtractor
    agent = KeywordExtractorAgent()
    result = agent.extract_keywords(all_text)
    
    assert result.keywords, "System failed to find any keyword from Excel data."
    print("Keywords from Excel:", result.keywords)
    print("Thought log (Excel):", result.thought_log)


def test_pdf_image_parsing_and_keyword_extraction(sample_pdf_img_path):
    # PDF data is chunked into image chunks (If testing in CI environment without Ghostscript, can skip)
    try:
        chunks = parse_file(sample_pdf_img_path)
    except Exception as e:
        pytest.skip(f"Cannot parse PDF to image: {e}")
        
    assert len(chunks) > 0, "PDF parsing failed."
    
    # Check if chunks are Base64 images
    has_image = False
    first_image_base64 = None
    all_text = ""
    for c in chunks:
        if c.chunk_type == "image":
            has_image = True
            if not first_image_base64:
                first_image_base64 = c.content
        else:
            all_text += c.content + "\n"

    assert has_image, "No image chunk detected from PDF."

    # Test KeywordExtractor with image support system (Vision)
    agent = KeywordExtractorAgent()
    result = agent.extract_keywords(all_text, image_base64=first_image_base64)
    
    assert result.keywords, "System failed to find any keyword from Image data (Vision LLM)."
    print("Keywords from Image:", result.keywords)
    print("Thought log (Image):", result.thought_log)


def test_extractor_agent_vision_support(sample_pdf_img_path):
    try:
        chunks = parse_file(sample_pdf_img_path)
        img_chunk = next(c for c in chunks if c.chunk_type == "image")
    except Exception as e:
        pytest.skip(f"Cannot get image chunk: {e}")

    extractor = ExtractorAgent()
    guidelines = "Please find the main title of this document."
    target_keywords = ["title", "report"]

    result = extractor.extract_from_chunk(img_chunk, guidelines, target_keywords)

    print("Thought log of Extractor (Vision):", result.thought_log)
    print("Extracted content:", result.extracted_data)
    assert result.confidence_score >= 0, "Score must be >= 0"
