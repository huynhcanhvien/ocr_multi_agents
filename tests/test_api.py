import os
from dotenv import load_dotenv
from dataProvider import ProviderService

# 1. Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("COMPETITION_API_KEY")
BASE_URL = os.getenv("BASE_URL")

def check_env():
    if not API_KEY or not BASE_URL:
        print("[ERROR] API_KEY or BASE_URL not found in .env file!")
        return False
    return True
def main():
    if not check_env():
        return
    print("[INFO] Starting dataProvider module test...\n")
    
    # Initialize Service
    provider = ProviderService(base_url=BASE_URL, api_key=API_KEY)
    
    # Step 1: Create Session
    print(" Creating new session...")
    session = provider.create_session()
    print("Session completely created!")
    print(f"   - Session ID: {session.session_id}")
    print(f"   - Token expires in: {session.expires_in} seconds\n")
    
    # Step 2: Fetch Task
    print(" Fetching next task...")
    task = provider.get_next_task()
    print("Task successfully fetched!")
    print(f"   - Task ID: {task.task_id}")
    print(f"   - Prompt: {task.prompt_template}")
    print(f"   - Number of attached documents: {len(task.resources)} files\n")
    
    # Step 3: Download file (Stream format)
    if not task.resources:
        print("[INFO] This task has no attached documents.")
        return

    print(" Proceeding to download documents...")
    
    # Root directory for downloaded data
    base_download_dir = "downloaded_data"
    
    for i, res in enumerate(task.resources, 1):
        # res.file_path format: "Public/01_masked_.../xxx.pdf"
        # Create local path: "downloaded_data/Public/01_masked_.../xxx.pdf"
        local_file_path = os.path.join(base_download_dir, res.file_path)
        
        # Get directory correctly to pre-create (e.g. "downloaded_data/Public/01_masked_...")
        local_dir = os.path.dirname(local_file_path)
        os.makedirs(local_dir, exist_ok=True)
        
        print(f"   [{i}/{len(task.resources)}] Downloading: {res.file_path.split('/')[-1]} ...")
        
        try:
            # Call download function
            saved_path = provider.download_file(download_token=res.token, save_path=local_file_path)
            print(f"   [SUCCESS] Saved to: {saved_path}")
        except Exception as e:
            print(f"   Error downloading file {res.file_path}: {e}")

    print("\n Test process completed (Not submitting).")

if __name__ == "__main__":
    main()