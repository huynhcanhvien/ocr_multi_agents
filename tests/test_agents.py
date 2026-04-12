# tests/test_agents.py
import pytest
from dotenv import load_dotenv

# Import Agents from core system
from core.agents.task_router import TaskRouterAgent
from core.agents.file_locator import FileLocatorAgent
from core.agents.file_organizer import FileOrganizerAgent

# Load environment variables (API Key) before running tests
load_dotenv()

class TestMultiAgents:
    
    # ---------------------------------------------------------
    # 1. TEST TASK ROUTER AGENT
    # ---------------------------------------------------------
    def test_router_organize_flow(self):
        """Test if Router correctly identifies Organize folder requests."""
        router = TaskRouterAgent()
        prompt = "Please classify the provided documents into the correct corresponding folders."
        
        result = router.classify_task(prompt)
        
        # Check return data type and classification result
        assert result.task_type == "ORGANIZE", "Router misidentified ORGANIZE flow"
        print(f"\n[Router - Organize] Reasoning: {result.reasoning}")

    def test_router_qa_flow(self):
        """Test if Router correctly identifies Extraction requests."""
        router = TaskRouterAgent()
        prompt = "Identify the construction schedule table and read the start and end times."
        
        result = router.classify_task(prompt)
        
        assert result.task_type == "QA", "Router misidentified QA flow"
        print(f"\n[Router - QA] Reasoning: {result.reasoning}")

    # ---------------------------------------------------------
    # 2. TEST FILE LOCATOR AGENT
    # ---------------------------------------------------------
    def test_file_locator_accuracy(self):
        """Test if FileLocator correctly finds the target file among irrelevant ones."""
        locator = FileLocatorAgent()
        
        task_prompt = "Identify the index file and check the document structure."
        document_summaries = """
        - File: ban_ve_tang_1.pdf | Content: Technical design drawing of Floor 1 construction...
        - File: muc_luc_du_an.pdf | Content: 1. Project Introduction, 2. 目次・インデックス, 3. Stakeholders...
        - File: hoa_don_dien_nuoc.pdf | Content: Electricity bill for October...
        """
        
        result = locator.locate_files(task_prompt, document_summaries)
        
        # Must return the exact requested filename
        assert "muc_luc_du_an.pdf" in result.target_file_names, "FileLocator picked the wrong target file!"
        assert "hoa_don_dien_nuoc.pdf" not in result.target_file_names, "FileLocator was confused by irrelevant file!"
        print(f"\n[Locator] Target: {result.target_file_names} | Reasoning: {result.reasoning}")

    # ---------------------------------------------------------
    # 3. TEST FILE ORGANIZER AGENT
    # ---------------------------------------------------------
    def test_file_organizer_taxonomy(self):
        """Test if Organizer strictly follows the provided Taxonomy."""
        organizer = FileOrganizerAgent()
        
        task_prompt = "Classify construction drawings and site photos."
        file_list = [
            "ban_ve_thi_cong_mai_nha.pdf",
            "anh_chup_ngay_15_10.jpg"
        ]
        
        result = organizer.organize_files(task_prompt, file_list)
        
        # Ensure Agent generated a thought log
        assert result.thought_log is not None
        assert len(result.thought_log) > 20, "Thought log is too short!"
        
        # Ensure Agent used exact folder names from VALID_FOLDERS
        assert "6. 竣工図面・施工図面" in result.thought_log, "Did not correctly classify drawings!"
        assert "19. 工事写真・写真帳" in result.thought_log, "Did not correctly classify images!"
        print(f"\n[Organizer] Thought Log:\n{result.thought_log}")