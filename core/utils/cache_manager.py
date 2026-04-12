# core/utils/cache_manager.py
import os
import pickle
from typing import Dict, Any, Optional

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CACHE_DIR = os.path.join(PROJECT_ROOT, "cache")

# A global Cache Dictionary that persists throughout the process lifecycle.
# Mapping: file_name -> Dictionary containing attributes.
_GLOBAL_FILE_CACHE: Dict[str, Dict[str, Any]] = {}

class CacheManager:
    """
    Manages cross-task cache (Disk Cache + In-Memory Cache).
    Helps store and reuse parsed data of files that appear multiple times across different Tasks.
    The key used is file_name because competition formats usually hash file names into MD5/UUID algorithms.
    Data is stored directly as PICKLE files in the ./cache directory to maintain the session.
    """
    
    @staticmethod
    def _get_file_path(file_name: str) -> str:
        # Extract the actual file name (in case file_name is a path string containing / or \)
        safe_name = file_name.replace("\\", "/").split("/")[-1]
        
        # Ensure cache directory exists
        os.makedirs(CACHE_DIR, exist_ok=True)
        return os.path.join(CACHE_DIR, f"{safe_name}.pkl")

    @classmethod
    def get_cache(cls, file_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve all cache data of a file."""
        if file_name not in _GLOBAL_FILE_CACHE:
            # Try loading from disk if not yet in RAM
            file_path = cls._get_file_path(file_name)
            if os.path.exists(file_path):
                try:
                    with open(file_path, "rb") as f:
                        _GLOBAL_FILE_CACHE[file_name] = pickle.load(f)
                except Exception:
                    pass
        return _GLOBAL_FILE_CACHE.get(file_name)

    @classmethod
    def update_cache(cls, file_name: str, key: str, value: Any):
        """Update an attribute (e.g., 'chunks', 'keyword_summary') into the file's cache (both RAM and disk)."""
        if file_name not in _GLOBAL_FILE_CACHE:
            # Try loading before initializing empty
            cls.get_cache(file_name)
            if file_name not in _GLOBAL_FILE_CACHE:
                _GLOBAL_FILE_CACHE[file_name] = {}
                
        _GLOBAL_FILE_CACHE[file_name][key] = value

        # Sync to disk to persist
        file_path = cls._get_file_path(file_name)
        try:
            with open(file_path, "wb") as f:
                pickle.dump(_GLOBAL_FILE_CACHE[file_name], f)
        except Exception as e:
            print(f"Error saving cache to disk for {file_name}: {e}")

    @classmethod
    def get_cached_item(cls, file_name: str, key: str) -> Optional[Any]:
        """Retrieve a specific attribute from the cache."""
        cache = cls.get_cache(file_name)
        if cache:
            return cache.get(key)
        return None

    @classmethod
    def clear_all(cls):
        """Clear all cache in RAM and disk (useful for testing)."""
        _GLOBAL_FILE_CACHE.clear()
        if os.path.exists(CACHE_DIR):
            for filename in os.listdir(CACHE_DIR):
                if filename.endswith(".json") or filename.endswith(".pkl"):
                    try:
                        os.remove(os.path.join(CACHE_DIR, filename))
                    except Exception:
                        pass

