from pydantic import BaseModel, Field


class MessageAnalysisRequest(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=2000,
    )


class MessageAnalysisResponse(BaseModel):
    label: str
    score: float
    warning: bool
    message: str