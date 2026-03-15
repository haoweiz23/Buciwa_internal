from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
import asyncio
import os
import random
from concurrent.futures import ThreadPoolExecutor

from app.database import get_db, init_db
from app.models import WordSet, Word, ClozeTest, ListeningExercise
from app.schemas import (
    WordSetCreate, WordSetResponse, WordSetListResponse,
    WordResponse, GenerateWordRequest,
    ClozeTestCreate, ClozeTestResponse, ClozeTestListResponse,
    ListeningExerciseCreate, ListeningExerciseResponse, ListeningExerciseListResponse
)
from app.services import llm_service, image_service
from app.services.tts_service import tts_service
from app.config import get_settings

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="A word visual memory web application",
    version="1.0.0"
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


# ============== API Routes ==============

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
    return {"message": "Word Visual Memory API", "version": "1.0.0"}


@app.get("/api/random-word")
async def get_random_word():
    """Get a random word for dice roll feature"""
    word = random.choice(COMMON_WORDS)
    return {"word": word}


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
async def generate_word_set(request: GenerateWordRequest, db: Session = Depends(get_db)):
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


@app.post("/api/words/{word_id}/regenerate-image", response_model=WordResponse)
async def regenerate_word_image(word_id: int, db: Session = Depends(get_db)):
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
async def regenerate_word_set(word_set_id: int, db: Session = Depends(get_db)):
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
async def delete_word_set(word_set_id: int, db: Session = Depends(get_db)):
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


@app.post("/api/cloze-tests/generate", response_model=ClozeTestResponse)
async def generate_cloze_test(request: ClozeTestCreate, db: Session = Depends(get_db)):
    """
    Generate a new cloze test with:
    - Chinese sentence with two blanks
    - Image based on the sentence
    """
    try:
        # Step 1: Call LLM to generate cloze test content
        llm_result = await run_sync(llm_service.generate_cloze_test, request.word1, request.word2)
        
        # Step 2: Create cloze test in database
        cloze_test = ClozeTest(
            word1=request.word1,
            word2=request.word2,
            sentence=llm_result["sentence"],
            sentence_with_answers=llm_result["sentence_with_answers"],
            word1_meaning=llm_result.get("word1_meaning", ""),
            word2_meaning=llm_result.get("word2_meaning", ""),
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
async def delete_cloze_test(cloze_test_id: int, db: Session = Depends(get_db)):
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
async def generate_listening_exercise(request: ListeningExerciseCreate, db: Session = Depends(get_db)):
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
async def delete_listening_exercise(exercise_id: int, db: Session = Depends(get_db)):
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
