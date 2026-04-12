# tests/test_data_pipeline.py
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


# IMPORTANT: STRICTLY DO NOT IMPORT core.agents DIRECTORY HERE
from core.parsers.file_router import parse_file
from core.schemas.data_types import DocumentChunk
from dataProvider import ProviderService

# Get absolute path to sample data folder
SAMPLE_DATA_DIR = Path(__file__).parent / "sample_data"

class TestDataPipeline:

    # ==========================================
    # 1. TEST CHUNKING & PARSING (REAL FILE, OFFLINE)
    # ==========================================
    
    def test_excel_to_markdown_chunking(self):
        """Test if real Excel file is properly chunked into Markdown Table."""
        excel_file = SAMPLE_DATA_DIR / "bang_tien_do.xlsx"
        
        if not excel_file.exists():
            pytest.skip(f"Sample file not found: {excel_file.name}")

        chunks = parse_file(str(excel_file))
        assert len(chunks) > 0, "Parser generated 0 chunks!"
        
        # NOTE: Use chunks[0] instead of chunk
        assert chunks[0].chunk_type == "table", "Wrong chunk type"
        print(f"\n[Parser] Excel successfully chunked into {len(chunks)} chunks.")

    def test_pdf_to_vision_chunking(self):
        """Test if real PDF file is properly cut into Base64 images."""
        pdf_file = SAMPLE_DATA_DIR / "tai_lieu_dac_ta.pdf"
        
        if not pdf_file.exists():
            pytest.skip(f"Sample file not found: {pdf_file.name}")

        chunks = parse_file(str(pdf_file))
        assert len(chunks) > 0, "Parser failed to cut any PDF pages!"
        assert chunks[0].chunk_type == "image", "Wrong chunk type"
        print(f"\n[Parser] PDF successfully cut into {len(chunks)} image pages.")


    # ==========================================
    # 2. TEST DATAPROVIDER (MOCK 100% NETWORK)
    # ==========================================
    
    # 2a. Mock GET (Fetch task) and POST (Create session)
    @patch('requests.post') 
    @patch('requests.get')
    def test_provider_fetch_task_mock(self, mock_get, mock_post):
        """Simulate fetching new Task from Server (No real API call)."""
        # Simulate Server returning Session ID
        mock_session_response = MagicMock()
        mock_session_response.json.return_value = {   
            "session_id": "mock_session_123", 
            "access_token": "Bearer abc", 
            "expires_in": 3600
        }
        mock_post.return_value = mock_session_response

        # Simulate Server returning Task
        mock_task_response = MagicMock()
        mock_task_response.json.return_value = {
            "task_id": "task_mock_999",
            "prompt_template": "Identify the index file.",
            "resources": [{
                "file_path": "folder/muc_luc.pdf",
                "file_type": "pdf",
                "token": "dl_token_1"
            }]
        }
        mock_get.return_value = mock_task_response

        # Initialize Provider with mock URL
        provider = ProviderService(base_url="https://mock-server.local", api_key="fake-key")
        
        provider.create_session()
        task = provider.get_next_task()
        
        assert provider.session.session_id == "mock_session_123"
        assert task.task_id == "task_mock_999"
        print("\n[DataProvider] Task Fetch mock successful. No real request was sent.")

    # 2b. Mock POST (Submit task) -> Prevent accidental submit!
    @patch('requests.post')
    def test_provider_submit_mock(self, mock_post):
        """Simulate task submission to Server. Ensure submit_task is tested safely."""
        # Simulate Server returning successful submission result
        mock_submit_response = MagicMock()
        mock_submit_response.status_code = 200
        mock_submit_response.json.return_value = {
            "status": "success",
            "message": "Submission received",
            "score": 10
        }
        mock_post.return_value = mock_submit_response

        provider = ProviderService(base_url="https://mock-server.local", api_key="fake-key")
        # Inject mock session to bypass check session_id function
        provider.session = MagicMock()
        provider.session.session_id = "mock_session_123"

        # CALL SUBMIT FUNCTION
        result = provider.submit_task(
            task_id="task_mock_999",
            answers=["Mock answer 1"],
            thought_log="This is a mock reasoning log",
            used_tools=["MockTool"]
        )

        # Check if Provider catches and processes the JSON file correctly
        assert result["status"] == "success"
        assert result["score"] == 10
        
        # SECURITY CHECK: Ensure sent Request is a mock URL, not the real competition URL
        called_url = mock_post.call_args[0][0]
        assert "mock-server.local" in called_url, "WARNING: API call URL is wrong or real URL got intercepted!"
        
        print(f"\n[DataProvider] Submit mock successful. Real API blocked, mock result: {result['score']} points.")