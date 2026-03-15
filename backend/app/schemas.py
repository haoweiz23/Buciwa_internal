from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class WordBase(BaseModel):
    word: str
    word_type: str
    meaning: Optional[str] = None


class WordCreate(WordBase):
    image_prompt: Optional[str] = None
    image_url: Optional[str] = None
    image_local_path: Optional[str] = None


class WordResponse(WordBase):
    id: int
    word_set_id: int
    image_prompt: Optional[str] = None
    image_url: Optional[str] = None
    image_local_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WordSetBase(BaseModel):
    main_word: str


class WordSetCreate(WordSetBase):
    pass


class WordSetResponse(WordSetBase):
    id: int
    created_at: datetime
    updated_at: datetime
    words: List[WordResponse] = []

    class Config:
        from_attributes = True


class WordSetListResponse(BaseModel):
    id: int
    main_word: str
    main_word_image: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class GenerateWordRequest(BaseModel):
    word: str


class RegenerateImageRequest(BaseModel):
    word_id: int


class LLMWordResponse(BaseModel):
    """Response from LLM for word generation"""
    similar_word: str  # 形近词
    synonym: str       # 近义词
    antonym: str       # 反义词
    prompts: dict      # Image prompts for each word


# ============== Cloze Test Schemas ==============

class ClozeTestBase(BaseModel):
    word1: str
    word2: str


class ClozeTestCreate(ClozeTestBase):
    pass


class ClozeTestResponse(ClozeTestBase):
    id: int
    sentence: str
    sentence_with_answers: str
    word1_meaning: Optional[str] = None
    word2_meaning: Optional[str] = None
    image_prompt: Optional[str] = None
    image_url: Optional[str] = None
    image_local_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClozeTestListResponse(BaseModel):
    id: int
    word1: str
    word2: str
    sentence: str
    image_local_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============== Listening Exercise Schemas ==============

class ListeningExerciseBase(BaseModel):
    scene_description: str


class ListeningExerciseCreate(ListeningExerciseBase):
    pass


class ListeningExerciseResponse(ListeningExerciseBase):
    id: int
    generated_text: Optional[str] = None
    image_prompt: Optional[str] = None
    image_url: Optional[str] = None
    image_local_path: Optional[str] = None
    audio_url: Optional[str] = None
    audio_local_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ListeningExerciseListResponse(BaseModel):
    id: int
    scene_description: str
    generated_text: Optional[str] = None
    image_local_path: Optional[str] = None
    audio_local_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
