from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
import asyncio
import os
import random
import json
from concurrent.futures import ThreadPoolExecutor

from app.database import get_db, init_db
from app.models import (
    User, WordSet, Word, ClozeTest, ListeningExercise,
    QuizSet, QuizSetWordItem, QuizSetClozeItem, QuizSetListeningItem, TestResult
)
from app.schemas import (
    LoginRequest, LoginResponse, UserResponse,
    WordSetCreate, WordSetResponse, WordSetListResponse,
    WordResponse, GenerateWordRequest,
    ClozeTestCreate, ClozeTestResponse, ClozeTestListResponse,
    ListeningExerciseCreate, ListeningExerciseResponse, ListeningExerciseListResponse,
    QuizSetCreate, QuizSetUpdate, QuizSetResponse, QuizSetListResponse,
    QuizSetWordItemCreate, QuizSetClozeItemCreate, QuizSetListeningItemCreate,
    QuizSetWordItemResponse, QuizSetClozeItemResponse, QuizSetListeningItemResponse,
    ReorderItemsRequest,
    TestResultCreate, TestResultResponse, TestResultListResponse,
    ActiveTestResponse
)
from app.services import llm_service, image_service
from app.services.tts_service import tts_service
from app.config import get_settings
from app.deps import (
    require_auth, require_admin, init_admin_user,
    verify_password, create_access_token
)

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="A word visual memory web application with admin and user interfaces",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for images
static_dir = "backend/static/images"
os.makedirs(static_dir, exist_ok=True)
audio_dir = "backend/static/audio"
os.makedirs(audio_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

# Thread pool for running sync operations
executor = ThreadPoolExecutor(max_workers=4)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    # Initialize default admin user
    db = next(get_db())
    try:
        init_admin_user(db)
    finally:
        db.close()


# ============== Helper Functions ==============

async def run_sync(func, *args):
    """Run synchronous function in thread pool"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args)


async def generate_image_async(prompt: str, word: str):
    """Generate image asynchronously"""
    try:
        return await run_sync(image_service.generate_image, prompt, word)
    except Exception as e:
        print(f"Error generating image for {word}: {e}")
        return {
            "image_url": "",
            "local_path": ""
        }


# ============== Auth API Routes ==============

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """管理员登录"""
    user = db.query(User).filter(User.username == request.username).first()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    
    return LoginResponse(
        access_token=access_token,
        username=user.username,
        role=user.role
    )


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(require_auth)):
    """获取当前用户信息"""
    return current_user


# ============== Common API Routes ==============

# Common English words for random selection
COMMON_WORDS = [
    "apple", "banana", "orange", "grape", "lemon",
    "house", "garden", "river", "mountain", "beach",
    "happy", "angry", "brave", "gentle", "clever",
    "book", "pencil", "clock", "mirror", "candle",
    "cat", "dog", "bird", "fish", "rabbit",
    "sun", "moon", "star", "cloud", "rain",
    "bread", "cheese", "butter", "honey", "sugar",
    "chair", "table", "window", "door", "floor",
    "shirt", "dress", "hat", "shoe", "coat",
    "car", "bus", "train", "ship", "bicycle",
    "tree", "flower", "grass", "leaf", "rose",
    "water", "fire", "earth", "wind", "light",
    "king", "queen", "prince", "princess", "knight",
    "gold", "silver", "diamond", "ruby", "pearl",
    "music", "dance", "song", "piano", "guitar",
    "coffee", "tea", "juice", "milk", "wine",
    "paper", "stone", "wood", "metal", "glass",
    "heart", "mind", "soul", "dream", "hope",
    "spring", "summer", "autumn", "winter", "season",
    "morning", "evening", "night", "noon", "midnight"
]


@app.get("/")
async def root():
    return {"message": "Word Visual Memory API", "version": "2.0.0"}


@app.get("/api/random-word")
async def get_random_word():
    """Get a random word for dice roll feature"""
    word = random.choice(COMMON_WORDS)
    return {"word": word}


# ============== Word Set API Routes ==============

@app.get("/api/word-sets", response_model=List[WordSetListResponse])
async def list_word_sets(db: Session = Depends(get_db)):
    """Get all word sets with their main word and thumbnail"""
    word_sets = db.query(WordSet).order_by(WordSet.created_at.desc()).all()
    
    result = []
    for ws in word_sets:
        # Get main word's image
        main_word = next((w for w in ws.words if w.word_type == "main"), None)
        result.append(WordSetListResponse(
            id=ws.id,
            main_word=ws.main_word,
            main_word_image=main_word.image_local_path if main_word else None,
            created_at=ws.created_at
        ))
    
    return result


@app.get("/api/word-sets/{word_set_id}", response_model=WordSetResponse)
async def get_word_set(word_set_id: int, db: Session = Depends(get_db)):
    """Get a specific word set with all words and images"""
    word_set = db.query(WordSet).filter(WordSet.id == word_set_id).first()
    if not word_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word set not found"
        )
    return word_set


@app.post("/api/word-sets/generate", response_model=WordSetResponse)
async def generate_word_set(request: GenerateWordRequest, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """
    Generate a new word set with:
    - Main word (A)
    - Similar word (B) - 形近词
    - Synonym (C) - 近义词
    - Antonym (D) - 反义词
    And generate images for each.
    """
    try:
        # Step 1: Call LLM to generate word options and prompts
        llm_result = await run_sync(llm_service.generate_word_options, request.word)
        
        # Step 2: Create word set in database
        word_set = WordSet(main_word=request.word)
        db.add(word_set)
        db.commit()
        db.refresh(word_set)
        
        # Step 3: Prepare words data with meanings
        meanings = llm_result.get("meanings", {})
        words_data = [
            {"word": request.word, "type": "main", "prompt": llm_result["prompts"]["main"], "meaning": meanings.get("A", "")},
            {"word": llm_result["similar_word"], "type": "similar", "prompt": llm_result["prompts"]["similar"], "meaning": meanings.get("B", "")},
            {"word": llm_result["synonym"], "type": "synonym", "prompt": llm_result["prompts"]["synonym"], "meaning": meanings.get("C", "")},
            {"word": llm_result["antonym"], "type": "antonym", "prompt": llm_result["prompts"]["antonym"], "meaning": meanings.get("D", "")},
        ]
        
        # Step 4: Generate images concurrently
        image_tasks = [generate_image_async(wd["prompt"], wd["word"]) for wd in words_data]
        image_results = await asyncio.gather(*image_tasks)
        
        # Step 5: Save words to database
        for i, word_data in enumerate(words_data):
            word = Word(
                word_set_id=word_set.id,
                word=word_data["word"],
                word_type=word_data["type"],
                meaning=word_data.get("meaning", ""),
                image_prompt=word_data["prompt"],
                image_url=image_results[i].get("image_url", ""),
                image_local_path=image_results[i].get("local_path", "")
            )
            db.add(word)
        
        db.commit()
        db.refresh(word_set)
        
        return word_set
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating word set: {str(e)}"
        )


@app.post("/api/word-sets/manual", response_model=WordSetResponse)
async def create_word_set_manual(
    main_word: str = Form(...),
    main_word_meaning: str = Form(""),
    similar_word: str = Form(""),
    similar_word_meaning: str = Form(""),
    synonym_word: str = Form(""),
    synonym_word_meaning: str = Form(""),
    antonym_word: str = Form(""),
    antonym_word_meaning: str = Form(""),
    main_word_image: Optional[UploadFile] = File(None),
    similar_word_image: Optional[UploadFile] = File(None),
    synonym_word_image: Optional[UploadFile] = File(None),
    antonym_word_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Manually create a word set with uploaded images"""
    try:
        # Create word set
        word_set = WordSet(main_word=main_word)
        db.add(word_set)
        db.commit()
        db.refresh(word_set)
        
        # Helper function to save uploaded image
        async def save_uploaded_image(upload_file: UploadFile, word: str):
            if not upload_file or not upload_file.filename:
                return {"image_url": "", "local_path": ""}
            
            # Save the file
            file_ext = os.path.splitext(upload_file.filename)[1]
            safe_word = "".join(c for c in word if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_word}_{random.randint(1000, 9999)}{file_ext}"
            
            # Ensure directory exists
            images_dir = "backend/static/images"
            os.makedirs(images_dir, exist_ok=True)
            
            file_path = os.path.join(images_dir, filename)
            
            # Write file
            content = await upload_file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            return {
                "image_url": f"/static/images/{filename}",
                "local_path": f"/static/images/{filename}"
            }
        
        # Prepare words data
        words_data = [
            {"word": main_word, "type": "main", "meaning": main_word_meaning, "image_file": main_word_image},
            {"word": similar_word, "type": "similar", "meaning": similar_word_meaning, "image_file": similar_word_image},
            {"word": synonym_word, "type": "synonym", "meaning": synonym_word_meaning, "image_file": synonym_word_image},
            {"word": antonym_word, "type": "antonym", "meaning": antonym_word_meaning, "image_file": antonym_word_image},
        ]
        
        # Save images and create words
        for word_data in words_data:
            if word_data["word"]:  # Only create if word is provided
                image_result = await save_uploaded_image(word_data["image_file"], word_data["word"])
                
                word = Word(
                    word_set_id=word_set.id,
                    word=word_data["word"],
                    word_type=word_data["type"],
                    meaning=word_data["meaning"],
                    image_url=image_result.get("image_url", ""),
                    image_local_path=image_result.get("local_path", "")
                )
                db.add(word)
        
        db.commit()
        db.refresh(word_set)
        
        return word_set
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating word set: {str(e)}"
        )


@app.post("/api/words/{word_id}/regenerate-image", response_model=WordResponse)
async def regenerate_word_image(word_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Regenerate image for a specific word"""
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word not found"
        )
    
    try:
        # Generate new image prompt if not exists
        if not word.image_prompt:
            word.image_prompt = await run_sync(
                llm_service.generate_image_prompt,
                word.word,
                word.word_type
            )
        
        # Generate new image
        image_result = await generate_image_async(word.image_prompt, word.word)
        
        # Update word with new image
        word.image_url = image_result.get("image_url", "")
        word.image_local_path = image_result.get("local_path", "")
        db.commit()
        db.refresh(word)
        
        return word
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error regenerating image: {str(e)}"
        )


@app.post("/api/word-sets/{word_set_id}/regenerate", response_model=WordSetResponse)
async def regenerate_word_set(word_set_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """
    Regenerate all words (B/C/D) and images for a word set.
    Keeps the main word (A) but generates new distractors.
    """
    word_set = db.query(WordSet).filter(WordSet.id == word_set_id).first()
    if not word_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word set not found"
        )
    
    try:
        # Get new word options from LLM
        llm_result = await run_sync(llm_service.generate_word_options, word_set.main_word)
        
        # Delete old words
        db.query(Word).filter(Word.word_set_id == word_set_id).delete()
        db.commit()
        
        # Prepare words data with meanings
        meanings = llm_result.get("meanings", {})
        words_data = [
            {"word": word_set.main_word, "type": "main", "prompt": llm_result["prompts"]["main"], "meaning": meanings.get("A", "")},
            {"word": llm_result["similar_word"], "type": "similar", "prompt": llm_result["prompts"]["similar"], "meaning": meanings.get("B", "")},
            {"word": llm_result["synonym"], "type": "synonym", "prompt": llm_result["prompts"]["synonym"], "meaning": meanings.get("C", "")},
            {"word": llm_result["antonym"], "type": "antonym", "prompt": llm_result["prompts"]["antonym"], "meaning": meanings.get("D", "")},
        ]
        
        # Generate images concurrently
        image_tasks = [generate_image_async(wd["prompt"], wd["word"]) for wd in words_data]
        image_results = await asyncio.gather(*image_tasks)
        
        # Save new words
        for i, word_data in enumerate(words_data):
            word = Word(
                word_set_id=word_set.id,
                word=word_data["word"],
                word_type=word_data["type"],
                meaning=word_data.get("meaning", ""),
                image_prompt=word_data["prompt"],
                image_url=image_results[i].get("image_url", ""),
                image_local_path=image_results[i].get("local_path", "")
            )
            db.add(word)
        
        db.commit()
        db.refresh(word_set)
        
        return word_set
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error regenerating word set: {str(e)}"
        )


@app.delete("/api/word-sets/{word_set_id}")
async def delete_word_set(word_set_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Delete a word set and all its words"""
    word_set = db.query(WordSet).filter(WordSet.id == word_set_id).first()
    if not word_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word set not found"
        )
    
    # Delete associated image files
    for word in word_set.words:
        if word.image_local_path:
            try:
                file_path = image_service.get_image_path(word.image_local_path)
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting image file: {e}")
    
    # Delete from database (cascade will delete words)
    db.delete(word_set)
    db.commit()
    
    return {"message": "Word set deleted successfully"}


# ============== Cloze Test API Routes ==============

@app.get("/api/cloze-tests", response_model=List[ClozeTestListResponse])
async def list_cloze_tests(db: Session = Depends(get_db)):
    """Get all cloze tests with thumbnails"""
    cloze_tests = db.query(ClozeTest).order_by(ClozeTest.created_at.desc()).all()
    return cloze_tests


@app.get("/api/cloze-tests/{cloze_test_id}", response_model=ClozeTestResponse)
async def get_cloze_test(cloze_test_id: int, db: Session = Depends(get_db)):
    """Get a specific cloze test"""
    cloze_test = db.query(ClozeTest).filter(ClozeTest.id == cloze_test_id).first()
    if not cloze_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cloze test not found"
        )
    return cloze_test


@app.post("/api/cloze-tests/manual", response_model=ClozeTestResponse)
async def create_cloze_test_manual(
    word1: str = Form(...),
    word2: str = Form(...),
    word1_meaning: str = Form(""),
    word2_meaning: str = Form(""),
    distractor1: str = Form(""),
    distractor2: str = Form(""),
    distractor1_meaning: str = Form(""),
    distractor2_meaning: str = Form(""),
    sentence: str = Form(...),
    sentence_with_answers: str = Form(...),
    sentence_en: str = Form(""),
    sentence_with_answers_en: str = Form(""),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Manually create a cloze test with uploaded image"""
    try:
        image_url = ""
        image_local_path = ""
        
        # Save uploaded image if provided
        if image and image.filename:
            file_ext = os.path.splitext(image.filename)[1]
            safe_word1 = "".join(c for c in word1 if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_word2 = "".join(c for c in word2 if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"cloze_{safe_word1}_{safe_word2}_{random.randint(1000, 9999)}{file_ext}"
            
            images_dir = "backend/static/images"
            os.makedirs(images_dir, exist_ok=True)
            
            file_path = os.path.join(images_dir, filename)
            content = await image.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            image_url = f"/static/images/{filename}"
            image_local_path = f"/static/images/{filename}"
        
        # Create cloze test
        cloze_test = ClozeTest(
            word1=word1,
            word2=word2,
            word1_meaning=word1_meaning,
            word2_meaning=word2_meaning,
            distractor1=distractor1,
            distractor2=distractor2,
            distractor1_meaning=distractor1_meaning,
            distractor2_meaning=distractor2_meaning,
            sentence=sentence,
            sentence_with_answers=sentence_with_answers,
            sentence_en=sentence_en,
            sentence_with_answers_en=sentence_with_answers_en,
            image_url=image_url,
            image_local_path=image_local_path
        )
        db.add(cloze_test)
        db.commit()
        db.refresh(cloze_test)
        
        return cloze_test
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating cloze test: {str(e)}"
        )


@app.post("/api/cloze-tests/generate", response_model=ClozeTestResponse)
async def generate_cloze_test(request: ClozeTestCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """
    Generate a new cloze test with:
    - Chinese sentence with two blanks
    - English sentence with two blanks
    - Two distractor words
    - Image based on the sentence
    """
    try:
        # Step 1: Call LLM to generate cloze test content (with distractors and English sentence)
        llm_result = await run_sync(llm_service.generate_cloze_test_with_distractors, request.word1, request.word2)
        
        # Step 2: Create cloze test in database
        cloze_test = ClozeTest(
            word1=request.word1,
            word2=request.word2,
            word1_meaning=llm_result.get("word1_meaning", ""),
            word2_meaning=llm_result.get("word2_meaning", ""),
            # 干扰选项
            distractor1=llm_result.get("distractor1", ""),
            distractor2=llm_result.get("distractor2", ""),
            distractor1_meaning=llm_result.get("distractor1_meaning", ""),
            distractor2_meaning=llm_result.get("distractor2_meaning", ""),
            # 中文句子
            sentence=llm_result["sentence"],
            sentence_with_answers=llm_result["sentence_with_answers"],
            # 英文句子
            sentence_en=llm_result.get("sentence_en", ""),
            sentence_with_answers_en=llm_result.get("sentence_with_answers_en", ""),
            # 图片
            image_prompt=llm_result["image_prompt"]
        )
        db.add(cloze_test)
        db.commit()
        db.refresh(cloze_test)
        
        # Step 3: Generate image
        image_result = await generate_image_async(llm_result["image_prompt"], f"cloze_{request.word1}_{request.word2}")
        
        # Update with image paths
        cloze_test.image_url = image_result.get("image_url", "")
        cloze_test.image_local_path = image_result.get("local_path", "")
        db.commit()
        db.refresh(cloze_test)
        
        return cloze_test
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating cloze test: {str(e)}"
        )


@app.delete("/api/cloze-tests/{cloze_test_id}")
async def delete_cloze_test(cloze_test_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Delete a cloze test"""
    cloze_test = db.query(ClozeTest).filter(ClozeTest.id == cloze_test_id).first()
    if not cloze_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cloze test not found"
        )
    
    # Delete associated image file
    if cloze_test.image_local_path:
        try:
            file_path = image_service.get_image_path(cloze_test.image_local_path)
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting image file: {e}")
    
    db.delete(cloze_test)
    db.commit()
    
    return {"message": "Cloze test deleted successfully"}


# ============== Listening Exercise API Routes ==============

@app.get("/api/listening-exercises", response_model=List[ListeningExerciseListResponse])
async def list_listening_exercises(db: Session = Depends(get_db)):
    """Get all listening exercises with thumbnails"""
    exercises = db.query(ListeningExercise).order_by(ListeningExercise.created_at.desc()).all()
    return exercises


@app.get("/api/listening-exercises/{exercise_id}", response_model=ListeningExerciseResponse)
async def get_listening_exercise(exercise_id: int, db: Session = Depends(get_db)):
    """Get a specific listening exercise"""
    exercise = db.query(ListeningExercise).filter(ListeningExercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listening exercise not found"
        )
    return exercise


@app.post("/api/listening-exercises/generate", response_model=ListeningExerciseResponse)
async def generate_listening_exercise(request: ListeningExerciseCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """
    Generate a new listening exercise with:
    - English text based on scene description
    - Image based on the scene
    - TTS audio
    """
    try:
        # Step 1: Call LLM to generate text and image prompt
        llm_result = await run_sync(llm_service.generate_listening_text, request.scene_description)
        
        # Step 2: Create listening exercise in database
        exercise = ListeningExercise(
            scene_description=request.scene_description,
            generated_text=llm_result["text"],
            image_prompt=llm_result["image_prompt"]
        )
        db.add(exercise)
        db.commit()
        db.refresh(exercise)
        
        # Step 3: Generate image and TTS concurrently
        image_task = generate_image_async(llm_result["image_prompt"], f"listening_{exercise.id}")
        tts_task = run_sync(tts_service.generate_speech, llm_result["text"])
        
        image_result, tts_result = await asyncio.gather(image_task, tts_task, return_exceptions=True)
        
        # Update with image paths
        if not isinstance(image_result, Exception):
            exercise.image_url = image_result.get("image_url", "")
            exercise.image_local_path = image_result.get("local_path", "")
        
        # Update with audio paths
        if not isinstance(tts_result, Exception):
            exercise.audio_url = tts_result.get("audio_url", "")
            exercise.audio_local_path = tts_result.get("local_path", "")
        
        db.commit()
        db.refresh(exercise)
        
        return exercise
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating listening exercise: {str(e)}"
        )


@app.delete("/api/listening-exercises/{exercise_id}")
async def delete_listening_exercise(exercise_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """Delete a listening exercise"""
    exercise = db.query(ListeningExercise).filter(ListeningExercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listening exercise not found"
        )
    
    # Delete associated image file
    if exercise.image_local_path:
        try:
            file_path = image_service.get_image_path(exercise.image_local_path)
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting image file: {e}")
    
    # Delete associated audio file
    if exercise.audio_local_path:
        try:
            file_path = tts_service.get_audio_path(exercise.audio_local_path)
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting audio file: {e}")
    
    db.delete(exercise)
    db.commit()
    
    return {"message": "Listening exercise deleted successfully"}


# ============== Quiz Set API Routes ==============

@app.get("/api/quiz-sets", response_model=List[QuizSetListResponse])
async def list_quiz_sets(db: Session = Depends(get_db)):
    """获取所有题集"""
    quiz_sets = db.query(QuizSet).order_by(QuizSet.created_at.desc()).all()
    
    result = []
    for qs in quiz_sets:
        result.append(QuizSetListResponse(
            id=qs.id,
            name=qs.name,
            description=qs.description,
            is_active=qs.is_active,
            word_count=len(qs.word_set_items),
            cloze_count=len(qs.cloze_items),
            listening_count=len(qs.listening_items),
            created_at=qs.created_at
        ))
    
    return result


@app.get("/api/quiz-sets/{quiz_set_id}", response_model=QuizSetResponse)
async def get_quiz_set(quiz_set_id: int, db: Session = Depends(get_db)):
    """获取题集详情"""
    quiz_set = db.query(QuizSet).filter(QuizSet.id == quiz_set_id).first()
    if not quiz_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题集不存在"
        )
    
    # 构建响应
    word_items = []
    for item in sorted(quiz_set.word_set_items, key=lambda x: x.order):
        main_word = next((w for w in item.word_set.words if w.word_type == "main"), None)
        word_items.append(QuizSetWordItemResponse(
            id=item.id,
            word_set_id=item.word_set_id,
            order=item.order,
            word_set=WordSetListResponse(
                id=item.word_set.id,
                main_word=item.word_set.main_word,
                main_word_image=main_word.image_local_path if main_word else None,
                created_at=item.word_set.created_at
            )
        ))
    
    cloze_items = []
    for item in sorted(quiz_set.cloze_items, key=lambda x: x.order):
        cloze_items.append(QuizSetClozeItemResponse(
            id=item.id,
            cloze_test_id=item.cloze_test_id,
            order=item.order,
            cloze_test=ClozeTestListResponse(
                id=item.cloze_test.id,
                word1=item.cloze_test.word1,
                word2=item.cloze_test.word2,
                sentence=item.cloze_test.sentence,
                image_local_path=item.cloze_test.image_local_path,
                created_at=item.cloze_test.created_at
            )
        ))
    
    listening_items = []
    for item in sorted(quiz_set.listening_items, key=lambda x: x.order):
        listening_items.append(QuizSetListeningItemResponse(
            id=item.id,
            listening_exercise_id=item.listening_exercise_id,
            order=item.order,
            listening_exercise=ListeningExerciseListResponse(
                id=item.listening_exercise.id,
                scene_description=item.listening_exercise.scene_description,
                generated_text=item.listening_exercise.generated_text,
                image_local_path=item.listening_exercise.image_local_path,
                audio_local_path=item.listening_exercise.audio_local_path,
                created_at=item.listening_exercise.created_at
            )
        ))
    
    return QuizSetResponse(
        id=quiz_set.id,
        name=quiz_set.name,
        description=quiz_set.description,
        is_active=quiz_set.is_active,
        created_at=quiz_set.created_at,
        updated_at=quiz_set.updated_at,
        word_set_items=word_items,
        cloze_items=cloze_items,
        listening_items=listening_items
    )


@app.post("/api/quiz-sets", response_model=QuizSetResponse)
async def create_quiz_set(request: QuizSetCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """创建题集"""
    quiz_set = QuizSet(
        name=request.name,
        description=request.description
    )
    db.add(quiz_set)
    db.commit()
    db.refresh(quiz_set)
    
    return QuizSetResponse(
        id=quiz_set.id,
        name=quiz_set.name,
        description=quiz_set.description,
        is_active=quiz_set.is_active,
        created_at=quiz_set.created_at,
        updated_at=quiz_set.updated_at,
        word_set_items=[],
        cloze_items=[],
        listening_items=[]
    )


@app.put("/api/quiz-sets/{quiz_set_id}", response_model=QuizSetResponse)
async def update_quiz_set(quiz_set_id: int, request: QuizSetUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """更新题集"""
    quiz_set = db.query(QuizSet).filter(QuizSet.id == quiz_set_id).first()
    if not quiz_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题集不存在"
        )
    
    if request.name is not None:
        quiz_set.name = request.name
    if request.description is not None:
        quiz_set.description = request.description
    
    db.commit()
    db.refresh(quiz_set)
    
    return await get_quiz_set(quiz_set_id, db)


@app.delete("/api/quiz-sets/{quiz_set_id}")
async def delete_quiz_set(quiz_set_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """删除题集"""
    quiz_set = db.query(QuizSet).filter(QuizSet.id == quiz_set_id).first()
    if not quiz_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题集不存在"
        )
    
    db.delete(quiz_set)
    db.commit()
    
    return {"message": "题集删除成功"}


@app.post("/api/quiz-sets/{quiz_set_id}/activate")
async def activate_quiz_set(quiz_set_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """激活题集（设为当前测验题集）"""
    # 先将所有题集设为非激活
    db.query(QuizSet).update({QuizSet.is_active: False})
    
    # 激活指定题集
    quiz_set = db.query(QuizSet).filter(QuizSet.id == quiz_set_id).first()
    if not quiz_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题集不存在"
        )
    
    quiz_set.is_active = True
    db.commit()
    
    return {"message": f"题集 '{quiz_set.name}' 已激活"}


@app.get("/api/quiz-sets/active", response_model=Optional[QuizSetResponse])
async def get_active_quiz_set(db: Session = Depends(get_db)):
    """获取当前激活的题集"""
    quiz_set = db.query(QuizSet).filter(QuizSet.is_active == True).first()
    if not quiz_set:
        return None
    
    return await get_quiz_set(quiz_set.id, db)


@app.post("/api/quiz-sets/{quiz_set_id}/words", response_model=QuizSetWordItemResponse)
async def add_word_to_quiz_set(
    quiz_set_id: int,
    request: QuizSetWordItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """添加单选题到题集"""
    quiz_set = db.query(QuizSet).filter(QuizSet.id == quiz_set_id).first()
    if not quiz_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题集不存在"
        )
    
    word_set = db.query(WordSet).filter(WordSet.id == request.word_set_id).first()
    if not word_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="单词集不存在"
        )
    
    # 检查是否已存在
    existing = db.query(QuizSetWordItem).filter(
        QuizSetWordItem.quiz_set_id == quiz_set_id,
        QuizSetWordItem.word_set_id == request.word_set_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该单词集已在题集中"
        )
    
    # 获取最大顺序
    max_order = db.query(QuizSetWordItem).filter(
        QuizSetWordItem.quiz_set_id == quiz_set_id
    ).count()
    
    item = QuizSetWordItem(
        quiz_set_id=quiz_set_id,
        word_set_id=request.word_set_id,
        order=request.order if request.order else max_order
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    
    main_word = next((w for w in word_set.words if w.word_type == "main"), None)
    return QuizSetWordItemResponse(
        id=item.id,
        word_set_id=item.word_set_id,
        order=item.order,
        word_set=WordSetListResponse(
            id=word_set.id,
            main_word=word_set.main_word,
            main_word_image=main_word.image_local_path if main_word else None,
            created_at=word_set.created_at
        )
    )


@app.delete("/api/quiz-sets/{quiz_set_id}/words/{item_id}")
async def remove_word_from_quiz_set(
    quiz_set_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """从题集中移除单选题"""
    item = db.query(QuizSetWordItem).filter(
        QuizSetWordItem.id == item_id,
        QuizSetWordItem.quiz_set_id == quiz_set_id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )
    
    db.delete(item)
    db.commit()
    
    return {"message": "题目已移除"}


@app.post("/api/quiz-sets/{quiz_set_id}/cloze", response_model=QuizSetClozeItemResponse)
async def add_cloze_to_quiz_set(
    quiz_set_id: int,
    request: QuizSetClozeItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """添加完形填空到题集"""
    quiz_set = db.query(QuizSet).filter(QuizSet.id == quiz_set_id).first()
    if not quiz_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题集不存在"
        )
    
    cloze_test = db.query(ClozeTest).filter(ClozeTest.id == request.cloze_test_id).first()
    if not cloze_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="完形填空不存在"
        )
    
    # 检查是否已存在
    existing = db.query(QuizSetClozeItem).filter(
        QuizSetClozeItem.quiz_set_id == quiz_set_id,
        QuizSetClozeItem.cloze_test_id == request.cloze_test_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该完形填空已在题集中"
        )
    
    # 获取最大顺序
    max_order = db.query(QuizSetClozeItem).filter(
        QuizSetClozeItem.quiz_set_id == quiz_set_id
    ).count()
    
    item = QuizSetClozeItem(
        quiz_set_id=quiz_set_id,
        cloze_test_id=request.cloze_test_id,
        order=request.order if request.order else max_order
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    
    return QuizSetClozeItemResponse(
        id=item.id,
        cloze_test_id=item.cloze_test_id,
        order=item.order,
        cloze_test=ClozeTestListResponse(
            id=cloze_test.id,
            word1=cloze_test.word1,
            word2=cloze_test.word2,
            sentence=cloze_test.sentence,
            image_local_path=cloze_test.image_local_path,
            created_at=cloze_test.created_at
        )
    )


@app.delete("/api/quiz-sets/{quiz_set_id}/cloze/{item_id}")
async def remove_cloze_from_quiz_set(
    quiz_set_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """从题集中移除完形填空"""
    item = db.query(QuizSetClozeItem).filter(
        QuizSetClozeItem.id == item_id,
        QuizSetClozeItem.quiz_set_id == quiz_set_id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )
    
    db.delete(item)
    db.commit()
    
    return {"message": "题目已移除"}


@app.post("/api/quiz-sets/{quiz_set_id}/listening", response_model=QuizSetListeningItemResponse)
async def add_listening_to_quiz_set(
    quiz_set_id: int,
    request: QuizSetListeningItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """添加听力题到题集"""
    quiz_set = db.query(QuizSet).filter(QuizSet.id == quiz_set_id).first()
    if not quiz_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题集不存在"
        )
    
    listening_exercise = db.query(ListeningExercise).filter(ListeningExercise.id == request.listening_exercise_id).first()
    if not listening_exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="听力练习不存在"
        )
    
    # 检查是否已存在
    existing = db.query(QuizSetListeningItem).filter(
        QuizSetListeningItem.quiz_set_id == quiz_set_id,
        QuizSetListeningItem.listening_exercise_id == request.listening_exercise_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该听力练习已在题集中"
        )
    
    # 获取最大顺序
    max_order = db.query(QuizSetListeningItem).filter(
        QuizSetListeningItem.quiz_set_id == quiz_set_id
    ).count()
    
    item = QuizSetListeningItem(
        quiz_set_id=quiz_set_id,
        listening_exercise_id=request.listening_exercise_id,
        order=request.order if request.order else max_order
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    
    return QuizSetListeningItemResponse(
        id=item.id,
        listening_exercise_id=item.listening_exercise_id,
        order=item.order,
        listening_exercise=ListeningExerciseListResponse(
            id=listening_exercise.id,
            scene_description=listening_exercise.scene_description,
            generated_text=listening_exercise.generated_text,
            image_local_path=listening_exercise.image_local_path,
            audio_local_path=listening_exercise.audio_local_path,
            created_at=listening_exercise.created_at
        )
    )


@app.delete("/api/quiz-sets/{quiz_set_id}/listening/{item_id}")
async def remove_listening_from_quiz_set(
    quiz_set_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """从题集中移除听力题"""
    item = db.query(QuizSetListeningItem).filter(
        QuizSetListeningItem.id == item_id,
        QuizSetListeningItem.quiz_set_id == quiz_set_id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题目不存在"
        )
    
    db.delete(item)
    db.commit()
    
    return {"message": "题目已移除"}


@app.put("/api/quiz-sets/{quiz_set_id}/reorder")
async def reorder_quiz_items(
    quiz_set_id: int,
    request: ReorderItemsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """重新排序题目"""
    if request.word_items:
        for item_data in request.word_items:
            item = db.query(QuizSetWordItem).filter(
                QuizSetWordItem.id == item_data["id"],
                QuizSetWordItem.quiz_set_id == quiz_set_id
            ).first()
            if item:
                item.order = item_data["order"]
    
    if request.cloze_items:
        for item_data in request.cloze_items:
            item = db.query(QuizSetClozeItem).filter(
                QuizSetClozeItem.id == item_data["id"],
                QuizSetClozeItem.quiz_set_id == quiz_set_id
            ).first()
            if item:
                item.order = item_data["order"]
    
    if request.listening_items:
        for item_data in request.listening_items:
            item = db.query(QuizSetListeningItem).filter(
                QuizSetListeningItem.id == item_data["id"],
                QuizSetListeningItem.quiz_set_id == quiz_set_id
            ).first()
            if item:
                item.order = item_data["order"]
    
    db.commit()
    
    return {"message": "排序已更新"}


# ============== Test API Routes ==============

@app.get("/api/test/active", response_model=Optional[ActiveTestResponse])
async def get_active_test(db: Session = Depends(get_db)):
    """获取当前激活的测验题集（用户端使用）"""
    quiz_set = db.query(QuizSet).filter(QuizSet.is_active == True).first()
    if not quiz_set:
        return None
    
    # 获取单选题
    word_questions = []
    for item in sorted(quiz_set.word_set_items, key=lambda x: x.order):
        main_word = next((w for w in item.word_set.words if w.word_type == "main"), None)
        word_questions.append(WordSetListResponse(
            id=item.word_set.id,
            main_word=item.word_set.main_word,
            main_word_image=main_word.image_local_path if main_word else None,
            created_at=item.word_set.created_at
        ))
    
    # 获取完形填空题
    cloze_questions = []
    for item in sorted(quiz_set.cloze_items, key=lambda x: x.order):
        cloze_questions.append(ClozeTestListResponse(
            id=item.cloze_test.id,
            word1=item.cloze_test.word1,
            word2=item.cloze_test.word2,
            sentence=item.cloze_test.sentence,
            image_local_path=item.cloze_test.image_local_path,
            created_at=item.cloze_test.created_at
        ))
    
    # 构建统一排序的题目列表
    ordered_questions = []
    
    # 收集所有题目及其顺序
    all_items = []
    for item in quiz_set.word_set_items:
        main_word = next((w for w in item.word_set.words if w.word_type == "main"), None)
        all_items.append({
            'type': 'word',
            'order': item.order,
            'item_id': item.word_set_id,
            'data': WordSetListResponse(
                id=item.word_set.id,
                main_word=item.word_set.main_word,
                main_word_image=main_word.image_local_path if main_word else None,
                created_at=item.word_set.created_at
            )
        })
    
    for item in quiz_set.cloze_items:
        all_items.append({
            'type': 'cloze',
            'order': item.order,
            'item_id': item.cloze_test_id,
            'data': ClozeTestListResponse(
                id=item.cloze_test.id,
                word1=item.cloze_test.word1,
                word2=item.cloze_test.word2,
                sentence=item.cloze_test.sentence,
                image_local_path=item.cloze_test.image_local_path,
                created_at=item.cloze_test.created_at
            )
        })
    
    for item in quiz_set.listening_items:
        all_items.append({
            'type': 'listening',
            'order': item.order,
            'item_id': item.listening_exercise_id,
            'data': ListeningExerciseListResponse(
                id=item.listening_exercise.id,
                scene_description=item.listening_exercise.scene_description,
                generated_text=item.listening_exercise.generated_text,
                image_local_path=item.listening_exercise.image_local_path,
                audio_local_path=item.listening_exercise.audio_local_path,
                created_at=item.listening_exercise.created_at
            )
        })
    
    # 按顺序排序
    all_items.sort(key=lambda x: x['order'])
    
    # 构建统一题目列表
    for item in all_items:
        from app.schemas import UnifiedQuestionItem
        ordered_questions.append(UnifiedQuestionItem(
            type=item['type'],
            order=item['order'],
            item_id=item['item_id'],
            word_data=item['data'] if item['type'] == 'word' else None,
            cloze_data=item['data'] if item['type'] == 'cloze' else None,
            listening_data=item['data'] if item['type'] == 'listening' else None
        ))
    
    # 构建完整响应
    quiz_set_response = await get_quiz_set(quiz_set.id, db)
    
    return ActiveTestResponse(
        quiz_set=quiz_set_response,
        word_questions=word_questions,
        cloze_questions=cloze_questions,
        ordered_questions=ordered_questions,
        total_questions=len(ordered_questions)
    )


@app.post("/api/test/submit", response_model=TestResultResponse)
async def submit_test_result(request: TestResultCreate, db: Session = Depends(get_db)):
    """提交测验结果"""
    quiz_set = db.query(QuizSet).filter(QuizSet.id == request.quiz_set_id).first()
    if not quiz_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="题集不存在"
        )
    
    # 计算得分百分比
    score_percentage = (request.correct_answers / request.total_questions * 100) if request.total_questions > 0 else 0
    
    # 将结果转换为 JSON 字符串
    word_results_json = json.dumps([r.model_dump() for r in request.word_results]) if request.word_results else None
    cloze_results_json = json.dumps([r.model_dump() for r in request.cloze_results]) if request.cloze_results else None
    wrong_questions_json = json.dumps([r.model_dump() for r in request.wrong_questions]) if request.wrong_questions else None
    
    result = TestResult(
        quiz_set_id=request.quiz_set_id,
        quiz_set_name=quiz_set.name,
        total_questions=request.total_questions,
        correct_answers=request.correct_answers,
        score_percentage=score_percentage,
        word_results=word_results_json,
        cloze_results=cloze_results_json,
        wrong_questions=wrong_questions_json
    )
    
    db.add(result)
    db.commit()
    db.refresh(result)
    
    return TestResultResponse(
        id=result.id,
        quiz_set_id=result.quiz_set_id,
        quiz_set_name=result.quiz_set_name,
        total_questions=result.total_questions,
        correct_answers=result.correct_answers,
        score_percentage=result.score_percentage,
        word_results=result.word_results,
        cloze_results=result.cloze_results,
        wrong_questions=result.wrong_questions,
        created_at=result.created_at
    )


@app.get("/api/test/results", response_model=List[TestResultListResponse])
async def list_test_results(db: Session = Depends(get_db)):
    """获取历史测验结果"""
    results = db.query(TestResult).order_by(TestResult.created_at.desc()).all()
    return results


@app.get("/api/test/results/{result_id}", response_model=TestResultResponse)
async def get_test_result(result_id: int, db: Session = Depends(get_db)):
    """获取测验结果详情"""
    result = db.query(TestResult).filter(TestResult.id == result_id).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="测验结果不存在"
        )
    
    return TestResultResponse(
        id=result.id,
        quiz_set_id=result.quiz_set_id,
        quiz_set_name=result.quiz_set_name,
        total_questions=result.total_questions,
        correct_answers=result.correct_answers,
        score_percentage=result.score_percentage,
        word_results=result.word_results,
        cloze_results=result.cloze_results,
        wrong_questions=result.wrong_questions,
        created_at=result.created_at
    )


@app.delete("/api/test/results/{result_id}")
async def delete_test_result(result_id: int, db: Session = Depends(get_db)):
    """删除测验结果"""
    result = db.query(TestResult).filter(TestResult.id == result_id).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="测验结果不存在"
        )
    
    db.delete(result)
    db.commit()
    
    return {"message": "测验结果已删除"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
