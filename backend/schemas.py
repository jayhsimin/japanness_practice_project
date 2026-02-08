from pydantic import BaseModel, Field
from typing import List


class VocabCreate(BaseModel):
    zh: str = Field(min_length=1, max_length=255)
    ja: str = Field(min_length=1, max_length=255)

class VocabUpdate(BaseModel):
    zh: str = Field(min_length=1, max_length=255)
    ja: str = Field(min_length=1, max_length=255)

class VocabOut(BaseModel):
    id: int
    zh: str
    ja: str
    class Config:
        from_attributes = True

class QuizItem(BaseModel):
    id: int
    zh: str

class QuizSubmitItem(BaseModel):
    id: int
    answer_ja: str

class QuizSubmitRequest(BaseModel):
    answers: List[QuizSubmitItem]

class QuizResultItem(BaseModel):
    id: int
    zh: str
    correct_ja: str
    user_ja: str
    is_correct: bool


class AISuggestRequest(BaseModel):
    zh: str = Field(default="", max_length=255)
    ja: str = Field(default="", max_length=255)

class AISuggestResponse(BaseModel):
    sentence: str
    translation: str
    spell_check: str


