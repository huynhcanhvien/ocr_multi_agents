import pytest
from unittest.mock import patch, MagicMock
from dataProvider import ProviderService
from core.parsers.file_router import parse_file
from core.agents.task_router import TaskRouterAgent
from core.agents.file_organizer import FileOrganizerAgent

class TestOrganizationFlow:

    @patch('requests.get')
    @patch('requests.post')
    def test_full_org_flow(self, mock_post, mock_get):
        # 1. Simulate data from DataProvider
        mock_get.return_value.json.return_value = {
            "task_id": "test_org_001",
            "prompt_template": "Classify this file into the correct technical folder.",
            "resources": [{"file_path": "tests/sample_data/bang_tien_do.xlsx", "file_type": "excel", "token": "abc"}]
        }
        
        # 2. Data Pipeline step: Download and Parse
        # (Using local file in sample_data to mock real download)
        task_file = "tests/sample_data/bang_tien_do.xlsx"
        chunks = parse_file(task_file)
        
        # 3. Agent 1 Step: TaskRouter (Determine flow)
        router = TaskRouterAgent()
        route_result = router.classify_task("Classify this file into the correct technical folder.")
        
        assert route_result.task_type == "ORGANIZE"
        
        # 4. Keyword Extractor
        from core.agents.keyword_extractor import KeywordExtractorAgent
        kw_extractor = KeywordExtractorAgent()
        kw_result = kw_extractor.extract_keywords(chunks[0].content)
        assert len(kw_result.keywords) > 0
        
        keywords_str = ", ".join(kw_result.keywords)
        enhanced_file_list = [f"bang_tien_do.xlsx (Keywords: {keywords_str})"]
        
        # 5. Agent 2 Step: FileOrganizer (Taxonomy Classification)
        organizer = FileOrganizerAgent()
        org_result = organizer.organize_files("Classify according to project rules", enhanced_file_list)
        
        assert len(org_result.thought_log) > 0
        print(f"\nOrganization flow OK. AI reasoning:\n{org_result.thought_log[:100]}...")