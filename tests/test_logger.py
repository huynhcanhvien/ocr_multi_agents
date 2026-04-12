import os
import pytest
from pathlib import Path
from core.utils.trace_logger import TaskTracer

@pytest.fixture
def tracer():
    # Initialize a completely new Tracer before each test (Clear Singleton cache)
    TaskTracer._instance = None
    return TaskTracer()

class MockResource:
    """Mock Resource class similar to dataProvider.models.Task structure"""
    def __init__(self, path, ftype):
        self.file_path = path
        self.file_type = ftype
        self.token = "abc123token"

def test_task_tracer_end_to_end(tracer, tmp_path, monkeypatch):
    """Simulate a Task run scenario and check Markdown Diary export"""
    # 1. Change output directory TRACE_DIR to temp directory (tmp_path)
    monkeypatch.setattr("core.utils.trace_logger.TRACE_DIR", tmp_path)
    
    mock_resources = [
        MockResource("ho_so_xay_dung.pdf", "pdf"),
        MockResource("anh_ky.jpg", "image")
    ]
    
    # 2. Start Task
    task_id = "test-uuid-5678"
    tracer.start_task(task_id, "Request: Extract all data", resources=mock_resources)
    tracer.set_task_type("QA_WORKFLOW")
    
    # 3. Record 2 logs from 2 Agents
    tracer.add_agent_span(
        agent_name="TaskRouter",
        system_prompt="You are a router",
        user_prompt="Please select the path",
        response={"task_type": "QA"}  # Demo passing Object
    )
    
    tracer.add_agent_span(
        agent_name="Extractor",
        system_prompt="You are an extractor",
        user_prompt=[{"type": "image_url"}],  # Demo passing Vision list block
        response="Nothing found"
    )
    
    # 4. End Task and check Dump File
    tracer.end_task()
    
    output_file = tmp_path / f"task_{task_id}.md"
    assert output_file.exists(), f"Output file not found at {output_file}"
    
    # 5. Analyze if MD content is empty/missing
    logs = output_file.read_text(encoding="utf-8")
    
    assert task_id in logs, "Missing ID title"
    assert "Request: Extract all data" in logs, "Missing original prompt"
    assert "QA_WORKFLOW" in logs, "Missing Task Type identifier"
    assert "ho_so_xay_dung.pdf" in logs, "Missing Resource number 1"
    assert "anh_ky.jpg" in logs, "Missing Resource number 2"
    
    assert "TaskRouter" in logs, "Missing Agent 1"
    assert "Extractor" in logs, "Missing Agent 2"
    assert "You are an extractor" in logs
    assert "[Compressed and sent 1 Vision Base64 image]" in logs, "Error in Vision prompt processing format"
    assert "Nothing found" in logs
