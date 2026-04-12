# main.py
from dotenv import load_dotenv
from core.config.settings import settings
from dataProvider import ProviderService
from core.pipeline import SystemPipeline
from core.utils.logger import agent_logger

def main():
    # 1. Load environment variables
    load_dotenv()
    
    agent_logger.info("OCR MULTI-AGENTS SYSTEM STARTED")
    
    try:
        # 2. Initialize DataProvider (Server Communication)
        provider = ProviderService(
            base_url=settings.BASE_URL, 
            api_key=settings.COMPETITION_API_KEY
        )
        provider.create_session()
        
        # 3. Attach DataProvider to Pipeline
        pipeline = SystemPipeline(provider)
        
        # 4. Activate autonomous competition loop
        # pipeline.process_single_task()
        pipeline.run_continuous()
        
    except Exception as e:
        agent_logger.critical(f"System crashed due to top-level error: {e}")

if __name__ == "__main__":
    main()