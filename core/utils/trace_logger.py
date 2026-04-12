import json
import os
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel
from .logger import agent_logger

TRACE_DIR = Path("logs/traces")
TRACE_DIR.mkdir(parents=True, exist_ok=True)

class TaskTracer:
    """Singleton that records highly detailed Markdown logs for each Task."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TaskTracer, cls).__new__(cls)
            cls._instance.current_task = None
            cls._instance.spans = []
        return cls._instance

    def start_task(self, task_id: str, prompt_template: str = "", resources: list = None):
        if resources is None:
            resources = []
        self.current_task = {
            "task_id": task_id,
            "start_time": datetime.now(),
            "prompt_template": prompt_template,
            "task_type": "Unclassified",
            "resources": resources
        }
        self.spans = []

    def set_task_type(self, task_type: str):
        if self.current_task:
            self.current_task["task_type"] = task_type
            
    def add_agent_span(self, agent_name: str, system_prompt: str, user_prompt: str | list, response: any):
        if not self.current_task:
            return  # No task is currently running

        # Format user prompt
        user_text = ""
        if isinstance(user_prompt, str):
            user_text = user_prompt
        elif isinstance(user_prompt, list):
            for item in user_prompt:
                if item.get("type") == "text":
                    user_text += item.get("text", "") + "\n"
                elif item.get("type") == "image_url":
                    user_text += "\n*[Compressed and sent 1 Vision Base64 image]*\n"

        # Format response
        if isinstance(response, BaseModel):
            response_text = "```json\n" + response.model_dump_json(indent=2) + "\n```"
        else:
            response_text = str(response)

        span = {
            "agent_name": agent_name,
            "time": datetime.now(),
            "system_prompt": system_prompt,
            "user_prompt": user_text.strip(),
            "response": response_text
        }
        self.spans.append(span)

    def end_task(self):
        if not self.current_task:
            return
            
        task_id = self.current_task["task_id"]
        start_time = self.current_task["start_time"]
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        md_lines = []
        md_lines.append(f"# TASK DIARY: `{task_id}`")
        md_lines.append(f"> **Execution Time:** {duration:.2f} seconds")
        md_lines.append(f"> **Task Category (Type):** `{self.current_task['task_type']}`")
        md_lines.append(f"> **Datetime:** {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        md_lines.append(f"\n##  Original Prompt Template\n")
        md_lines.append(f"```text\n{self.current_task['prompt_template']}\n```")
        
        resources = self.current_task.get("resources", [])
        if resources:
            md_lines.append("\n## Attached file list (Resources)\n")
            for idx, res in enumerate(resources, 1):
                md_lines.append(f"{idx}. `[{res.file_type}]` **{res.file_path}**")
                
        md_lines.append(f"\n---\n")
        
        md_lines.append(f"##  AGENT REASONING HISTORY\n")
        
        for i, span in enumerate(self.spans, 1):
            md_lines.append(f"### Step {i}: [{span['agent_name']}]")
            md_lines.append(f"* Execution Time: {span['time'].strftime('%H:%M:%S')}*")
            
            md_lines.append(f"\n<details><summary><b>1. System Prompt (Permissions)</b></summary>\n")
            md_lines.append(f"```text\n{span['system_prompt']}\n```\n</details>\n")
            
            md_lines.append(f"\n<details open><summary><b>2. User Prompt (Input)</b></summary>\n")
            md_lines.append(f"```text\n{span['user_prompt']}\n```\n</details>\n")
            
            md_lines.append(f"\n<details open><summary><b>3. Output (Analysis Result)</b></summary>\n")
            md_lines.append(f"{span['response']}")
            md_lines.append(f"\n</details>\n")
            md_lines.append(f"\n---\n")
        
        # Save to file
        file_path = TRACE_DIR / f"task_{task_id}.md"
        md_content = "\n".join(md_lines)
        file_path.write_text(md_content, encoding="utf-8")
            
        agent_logger.success(f"Exported Agent report for Task {task_id} to file: {file_path}")
        
        self.current_task = None
        self.spans = []

# Global instance
tracer = TaskTracer()
