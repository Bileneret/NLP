from pydantic import BaseModel, Field

class FeedbackScorecard(BaseModel):
    """Схема для фінального фідбеку після співбесіди."""
    technical_score: int = Field(description="Оцінка технічних знань від 1 до 10")
    communication_score: int = Field(description="Оцінка навичок комунікації від 1 до 10")
    strong_points: list[str] = Field(description="Список сильних сторін кандидата")
    areas_for_improvement: list[str] = Field(description="Список зон для покращення")
    final_verdict: str = Field(description="Короткий фінальний висновок (наймати чи ні, і чому)")