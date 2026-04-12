# core/utils/retry.py
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from ..exceptions.agent_errors import LLMCommunicationError
from .logger import agent_logger

def log_retry_attempt(retry_state):
    """Print a message whenever the system has to retry."""
    agent_logger.warning(
        f"Retrying attempt {retry_state.attempt_number} due to error: {retry_state.outcome.exception()}"
    )

def llm_retry():
    """
    Industry-standard decorator to wrap OpenAI function calls.
    - Try a maximum of 4 times.
    - Exponential wait time: 2s -> 4s -> 8s.
    """
    return retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception), # Catch all exceptions from OpenAI library
        before_sleep=log_retry_attempt,
        reraise=True # Reraise exception if all 4 retries fail
    )