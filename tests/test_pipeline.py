import sys
from datetime import datetime
from dotenv import load_dotenv

# Add logic so that directly run file understands core/dataProvider module
import os
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from core.config.settings import settings
from dataProvider import ProviderService
from core.pipeline import SystemPipeline
from core.utils.logger import agent_logger

def run_test():
    # 1. Load environment variables
    load_dotenv()
    
    # 2. Generate log filename with Timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/test_pipeline_{timestamp}.txt"
    
    # 3. Branch Logger to a new file specifically for this test run
    agent_logger.add(
        log_filename,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | Agent Log - {message}",
        level="DEBUG",
        enqueue=True, # Thread-safe processing
        backtrace=True,
        diagnose=True
    )
    
    agent_logger.info(f"START E2E TEST: Full activity log will be saved at {log_filename}")
    
    try:
        # Step 1 & 2: Initialize Sessions
        agent_logger.info("Phase 1: Initialize DataProvider & Call Session Token...")
        provider = ProviderService(
            base_url=settings.BASE_URL, 
            api_key=settings.COMPETITION_API_KEY
        )
        provider.create_session()
        
        # Step 3: Assemble Pipeline
        agent_logger.info("Phase 2: Assemble DataProvider into SystemPipeline...")
        pipeline = SystemPipeline(provider)
        
        # Step 4: Run exactly 1 Task loop
        agent_logger.info("Phase 3: Start processing 1 single Task (Fetch -> Download -> Reason -> Submit)...")
        pipeline.process_single_task()
        
        agent_logger.success(f"SUCCESS: Processed and submitted 1 complete Task. Check details at: {log_filename}")
        
    except Exception as e:
        agent_logger.exception(f"FAILURE: E2E Test loop encountered an error. Extracted: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_test()
