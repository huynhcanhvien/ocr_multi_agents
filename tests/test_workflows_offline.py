import pytest
from pathlib import Path
from unittest.mock import MagicMock

from core.workflows.qa_workflow import QAWorkflow
from core.workflows.organize_workflow import OrganizeWorkflow
from dataProvider.models.task import Task, Resource
from core.utils.cache_manager import CacheManager

@pytest.fixture(autouse=True)
def clear_cache():
    # Clear cache to avoid conflicts between unit tests
    CacheManager.clear_all()

@pytest.fixture
def mock_provider():
    provider = MagicMock()
    return provider

def test_offline_organize_workflow(mock_provider):
    """
    Check Organize Workflow running end-to-end (offline).
    Also verify CacheManager and Review Loop run correctly.
    """
    # Configure Mock DataProvider to return Offline Excel file (Simulate download_file success)
    sample_path = Path("tests/sample_data/bang_tien_do.xlsx").absolute()
    mock_provider.download_file.return_value = str(sample_path)
    
    # Simulate successful Submit response
    mock_provider.submit_task.return_value = {"status": "success", "score": 10}

    # Create empty Task
    mock_task = Task(
        task_id="mock_org_id",
        prompt_template="Classify construction drawing file into correct folder",
        resources=[Resource(file_path="mock_file.xlsx", file_type="excel", token="fake_token")]
    )

    workflow = OrganizeWorkflow(provider=mock_provider)
    
    # EXECUTION (Flow Run 1: No Cache)
    workflow.execute(mock_task)
    
    # Verify:
    mock_provider.download_file.assert_called()
    mock_provider.submit_task.assert_called()
    
    submit_args = mock_provider.submit_task.call_args[1]
    assert "thought_log" in submit_args
    assert "Reviewer" in submit_args["used_tools"]
    
    # Check if CacheManager worked
    assert CacheManager.get_cached_item("mock_file.xlsx", "keywords") is not None
    
    # EXECUTION (Flow Run 2: Using Cache)
    workflow.execute(mock_task)
    # If cache success, thought_log on submit 2 must contain keyword "[Cache HIT]"
    submit_args_2 = mock_provider.submit_task.call_args[1]
    assert "[Cache HIT]" in submit_args_2["thought_log"]


def test_offline_qa_workflow(mock_provider):
    """
    Check QA Workflow running end-to-end with PDF image data.
    """
    sample_path = Path("tests/sample_data/tai_lieu_dac_ta.pdf").absolute()
    mock_provider.download_file.return_value = str(sample_path)
    mock_provider.submit_task.return_value = {"status": "success"}

    mock_task = Task(
        task_id="mock_qa_id",
        prompt_template="Find the name of the power generation system",
        resources=[Resource(file_path="mock_pdf.pdf", file_type="pdf", token="fake_token")]
    )

    workflow = QAWorkflow(provider=mock_provider)
    
    workflow.execute(mock_task)
    
    mock_provider.download_file.assert_called()
    mock_provider.submit_task.assert_called()

    submit_args = mock_provider.submit_task.call_args[1]
    assert "thought_log" in submit_args
    assert "Reviewer" in submit_args["used_tools"]
    assert "FileLocator" in submit_args["used_tools"]
