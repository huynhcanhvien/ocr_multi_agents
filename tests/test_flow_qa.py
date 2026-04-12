import pytest
from unittest.mock import patch
from core.parsers.file_router import parse_file
from core.agents.task_router import TaskRouterAgent
from core.agents.file_locator import FileLocatorAgent
from core.agents.base_agent import BaseAgent # Or your specific ExtractorAgent

class TestQAFlow:

    def test_full_qa_extract_flow(self):
        # Suppose we have a request about the PDF content
        user_query = "What is the name of this project and who is implementing it?"
        pdf_path = "tests/sample_data/tai_lieu_dac_ta.pdf"
        
        # 1. Parse data (Convert PDF to Vision Chunks)
        chunks = parse_file(pdf_path)
        
        # 2. Router identifies Task
        router = TaskRouterAgent()
        route_result = router.classify_task(user_query)
        assert route_result.task_type == "QA"
        
        # 3. Analyzer (File Locator) with Chunk loop
        locator = FileLocatorAgent()
        target_file_names = set()
        
        chunks_by_file = {}
        for chunk in chunks:
            chunks_by_file.setdefault(chunk.file_name, []).append(chunk)
            
        file_read_index = {fname: 0 for fname in chunks_by_file.keys()}
        active_files = set(chunks_by_file.keys())
        
        loop_count = 0
        while active_files and loop_count < 3:
            loop_count += 1
            user_content_blocks = [
                {"type": "text", "text": f"<Task Instruction>\n{user_query}\n\n<Document List and Current Content>\n"}
            ]
            for fname in active_files:
                idx = file_read_index[fname]
                if idx < len(chunks_by_file[fname]):
                    c = chunks_by_file[fname][idx]
                    if c.chunk_type == "image":
                        user_content_blocks.append({
                            "type": "text",
                            "text": f"\n- File: {fname} (Page/Chunk {idx+1}) | Attached image content:"
                        })
                        user_content_blocks.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{c.content}",
                                "detail": "auto" 
                            }
                        })
                    else:
                        text_excerpt = c.content[:1500]
                        user_content_blocks.append({
                            "type": "text",
                            "text": f"\n- File: {fname} (Page/Chunk {idx+1}) | Text content:\n{text_excerpt}..."
                        })
                else:
                    user_content_blocks.append({"type": "text", "text": f"\n- File: {fname} | [END OF DOCUMENT CONTENT]\n"})
            
            user_content_blocks.append({
                "type": "text",
                "text": "\nAnalyze content. Determine which files are definitely needed, definitely excluded, and need the next page read."
            })
                    
            locate_result = locator.locate_files_advanced(user_content_blocks)
            
            for f in locate_result.target_file_names:
                target_file_names.add(f)
                
            if not locate_result.requires_more_info:
                break
                
            next_active_files = set()
            for fname in locate_result.files_needing_more_chunks:
                if fname in chunks_by_file and file_read_index[fname] + 1 < len(chunks_by_file[fname]):
                    file_read_index[fname] += 1
                    next_active_files.add(fname)
            active_files = next_active_files
        
        # If test is correct, it will finish scanning without crashing.
        assert target_file_names is not None
        
        # 4. QA/Extractor Agent reads specific content
        # Here we directly call a vision agent to test reading capability
        qa_agent = BaseAgent(agent_name="QA_Tester", temperature=1.0) 
        
        # Suppose we send the first page (usually contains project name) to AI
        system_msg = "You are a construction document reading expert."
        user_msg = f"Based on this image, answer the question: {user_query}"
        
        # Send attached Base64 image from chunk via image_base64 parameter for Vision standard
        response = qa_agent.call_llm(
            system_prompt=system_msg, 
            user_prompt=user_msg, 
            image_base64=chunks[0].content if chunks[0].chunk_type == "image" else None
        )
        
        assert response is not None
        print(f"\nQA flow OK. AI response: {response[:100]}...")
