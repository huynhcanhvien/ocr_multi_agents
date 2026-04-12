# core/utils/logger.py
import sys
import io
from loguru import logger
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Ensure logs directory exists
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Remove the bland default Python configuration
logger.remove()

# 1. Log to Terminal (Colorized for readability)
logger.add(
    sys.stdout, 
    colorize=True, 
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO" # Keep as INFO for competition to avoid clutter
)

# 2. Log to file (Keep everything including DEBUG for traceback on wrong submission)
logger.add(
    "logs/agent_pipeline.log", 
    rotation="10 MB",     # Automatically create new file when 10MB is reached
    retention="3 days",   # Delete old logs after 3 days
    compression="zip",    # Compress old log files
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    encoding="utf-8"
)

agent_logger = logger