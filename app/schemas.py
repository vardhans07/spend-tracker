from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import date
from typing import Optional, Dict

class ExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Amount must be positive")
    category: str = Field(..., min_length=1, max_length=50)
    note: Optional[str] = Field(default="", max_length=255)
    date: date

    @field_validator("category")
    @classmethod
    def strip_category(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Category cannot be empty or whitespace")
        return cleaned.title()

class ExpenseResponse(ExpenseCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int

class SummaryResponse(BaseModel):
    total_spend: float
    by_category: Dict[str, float]
    current_month_spend: float
    previous_month_spend: float
    month_over_month_change_pct: Optional[float]
