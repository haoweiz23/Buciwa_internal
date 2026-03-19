from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# ============== Auth Schemas ==============

class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============== Word Schemas ==============

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
    # 主要单词
    word1_meaning: Optional[str] = None
    word2_meaning: Optional[str] = None
    # 干扰选项
    distractor1: Optional[str] = None
    distractor2: Optional[str] = None
    distractor1_meaning: Optional[str] = None
    distractor2_meaning: Optional[str] = None
    # 中文句子
    sentence: str
    sentence_with_answers: str
    # 英文句子
    sentence_en: Optional[str] = None
    sentence_with_answers_en: Optional[str] = None
    # 图片
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


# ============== Quiz Set Schemas ==============

class QuizSetBase(BaseModel):
    name: str
    description: Optional[str] = None


class QuizSetCreate(QuizSetBase):
    pass


class QuizSetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class QuizSetWordItemCreate(BaseModel):
    word_set_id: int
    order: Optional[int] = 0


class QuizSetClozeItemCreate(BaseModel):
    cloze_test_id: int
    order: Optional[int] = 0


class QuizSetListeningItemCreate(BaseModel):
    listening_exercise_id: int
    order: Optional[int] = 0


class QuizSetWordItemResponse(BaseModel):
    id: int
    word_set_id: int
    order: int
    word_set: WordSetListResponse

    class Config:
        from_attributes = True


class QuizSetClozeItemResponse(BaseModel):
    id: int
    cloze_test_id: int
    order: int
    cloze_test: ClozeTestListResponse

    class Config:
        from_attributes = True


class QuizSetListeningItemResponse(BaseModel):
    id: int
    listening_exercise_id: int
    order: int
    listening_exercise: ListeningExerciseListResponse

    class Config:
        from_attributes = True


class QuizSetResponse(QuizSetBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    word_set_items: List[QuizSetWordItemResponse] = []
    cloze_items: List[QuizSetClozeItemResponse] = []
    listening_items: List[QuizSetListeningItemResponse] = []

    class Config:
        from_attributes = True


class QuizSetListResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    word_count: int = 0
    cloze_count: int = 0
    listening_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class ReorderItemsRequest(BaseModel):
    word_items: Optional[List[dict]] = None  # [{"id": 1, "order": 1}, ...]
    cloze_items: Optional[List[dict]] = None
    listening_items: Optional[List[dict]] = None


# ============== Test Result Schemas ==============

class WordResultItem(BaseModel):
    word_set_id: int
    main_word: str
    selected_word: str
    correct_word: Optional[str] = None
    is_correct: bool


class ClozeResultItem(BaseModel):
    cloze_test_id: int
    sentence: Optional[str] = None
    selected_answer1: Optional[str] = None
    selected_answer2: Optional[str] = None
    correct_answer1: Optional[str] = None
    correct_answer2: Optional[str] = None
    selected_answer: Optional[str] = None  # Keep for backward compatibility
    correct_answer: Optional[str] = None  # Keep for backward compatibility
    is_correct: bool


class ListeningResultItem(BaseModel):
    """听力练习结果项"""
    listening_exercise_id: int
    scene_description: Optional[str] = None
    completed: bool  # 听力题只记录是否完成，不判断对错


class WrongQuestionItem(BaseModel):
    """错误题目项"""
    question_type: str  # 'word', 'cloze', or 'listening'
    question_id: int
    main_word: Optional[str] = None  # for word questions
    sentence: Optional[str] = None  # for cloze questions
    selected_answer: str
    correct_answer: str


class TestResultCreate(BaseModel):
    quiz_set_id: int
    total_questions: int
    correct_answers: int
    word_results: Optional[List[WordResultItem]] = None
    cloze_results: Optional[List[ClozeResultItem]] = None
    listening_results: Optional[List[ListeningResultItem]] = None
    wrong_questions: Optional[List[WrongQuestionItem]] = None


class TestResultResponse(BaseModel):
    id: int
    quiz_set_id: int
    quiz_set_name: str
    total_questions: int
    correct_answers: int
    score_percentage: float
    word_results: Optional[str] = None  # JSON string
    cloze_results: Optional[str] = None  # JSON string
    wrong_questions: Optional[str] = None  # JSON string
    created_at: datetime

    class Config:
        from_attributes = True


class TestResultListResponse(BaseModel):
    id: int
    quiz_set_name: str
    total_questions: int
    correct_answers: int
    score_percentage: float
    word_results: Optional[str] = None  # JSON string
    cloze_results: Optional[str] = None  # JSON string
    wrong_questions: Optional[str] = None  # JSON string
    created_at: datetime

    class Config:
        from_attributes = True


# ============== Active Test Schemas ==============

class UnifiedQuestionItem(BaseModel):
    """统一的题目项，用于按顺序展示题目"""
    type: str  # 'word', 'cloze', 'listening'
    order: int
    item_id: int  # word_set_id, cloze_test_id, or listening_exercise_id
    word_data: Optional[WordSetListResponse] = None
    cloze_data: Optional[ClozeTestListResponse] = None
    listening_data: Optional[ListeningExerciseListResponse] = None


class ActiveTestResponse(BaseModel):
    """当前激活的测验题集信息"""
    quiz_set: QuizSetResponse
    word_questions: List[WordSetListResponse]
    cloze_questions: List[ClozeTestListResponse]
    ordered_questions: List[UnifiedQuestionItem]  # 新增：按顺序排列的所有题目
    total_questions: int
