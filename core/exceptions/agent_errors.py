# core/exceptions/agent_errors.py

class BaseSystemError(Exception):
    """Base class for all exceptions in the OCR Multi-Agent system."""
    pass

class SystemConfigError(BaseSystemError):
    """Error raised at startup if API Key is missing or configuration format is invalid."""
    pass

class DataProviderError(BaseSystemError):
    """Error when communicating with the Competition Server (Download failure, Submit error)."""
    pass

class LLMCommunicationError(BaseSystemError):
    """Error when calling OpenAI API (Timeout, Rate Limit, or API downtime)."""
    pass

class ParsingError(BaseSystemError):
    """Error when unable to parse PDF, Excel, or Image files."""
    pass