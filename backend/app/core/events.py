from typing import Literal, Optional
from pydantic import BaseModel

class PlaywrightEvent(BaseModel):
    type: Literal[
        "FIELD_START",
        "FIELD_FILLED", 
        "FIELD_ERROR",
        "PAGE_SUBMIT",
        "COMPLETE",
        "FATAL_ERROR"
    ]
    field: Optional[str] = None
    label: Optional[str] = None
    value: Optional[str] = None
    error: Optional[str] = None
    certificate_url: Optional[str] = None
    message: Optional[str] = None
    timestamp: Optional[str] = None

class CatalogueEvent(BaseModel):
    type: Literal[
        "ANALYSING",
        "CRAFT_DETECTED",
        "TITLE_READY",
        "DESCRIPTION_READY",
        "PRICE_SUGGESTED",
        "LISTING_READY",
        "ERROR"
    ]
    payload: dict = {}
    timestamp: Optional[str] = None