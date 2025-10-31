from pydantic import BaseModel, Field
from typing import Any, Dict, List

class ExportRequest(BaseModel):
    sheet_name: str = Field(..., description="Sheet to transform")

class LLMRulePayload(BaseModel):
    rules_json: Dict[str, Any]
    rows: List[Dict[str, Any]]

class LLMResult(BaseModel):
    rows: List[Dict[str, Any]]
