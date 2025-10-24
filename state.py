# state.py
from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional


class ConversionState(BaseModel):
    """Shared state schema for the Rails → Django conversion graph."""

    # --- Core paths ---
    input_dir: str
    output_dir: str
    project_root: Optional[str] = None

    # --- Discovery phase ---
    discovered_files: Optional[List[str]] = None
    parsed_summary: Optional[Dict[str, Any]] = None
    rails_summary: Optional[Dict[str, Any]] = None
    files_to_read: Optional[List[str]] = None
    rails_units: Optional[Dict[str, Any]] = None

    # --- Converter phase ---
    django_blueprint: Optional[Dict[str, Any]] = None

    # --- Builder phase ---
    generated_files: Optional[List[str]] = None

    # --- Integration phase ---
    integration: Optional[Dict[str, Any]] = None

    # --- Logging ---
    logs: Optional[List[str]] = None
    llm_response: Optional[Any] = None

    # ✅ allow LangGraph to attach runtime attributes (e.g., current_node)
    model_config = ConfigDict(extra="allow")

    # ---------- Dict-like helpers ----------
    def get(self, key: str, default=None):
        """Safe getter (dict-like)."""
        return getattr(self, key, default)

    def set(self, key: str, value: Any):
        """Setter helper."""
        setattr(self, key, value)

    def __getitem__(self, key: str):
        """Enable state['key'] syntax."""
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any):
        """Enable state['key'] = value syntax."""
        setattr(self, key, value)

    def __contains__(self, key: str):
        """Support `'key' in state` checks."""
        return hasattr(self, key)

    def update(self, data: dict = None, **kwargs):
        """Enable dict-like update()"""
        data = data or {}
        data.update(kwargs)
        for k, v in data.items():
            setattr(self, k, v)

    def dict(self, *args, **kwargs):
        """Ensure recursive serialization for JSON output."""
        return super().dict(*args, **kwargs)
