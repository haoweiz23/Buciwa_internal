from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Word Visual Memory"
    debug: bool = True
    
    # Doubao API Configuration (using OpenAI compatible client)
    ark_api_key: str = ""
    ark_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    
    # Model names
    llm_model: str = "doubao-seed-1-8-251228"
    image_model: str = "doubao-seedream-4-0-250828"
    
    # Volcano TTS Configuration
    volcano_access_key: str = ""
    volcano_app_id: str = ""
    volcano_cluster: str = "volcano_tts"
    volcano_voice_type: str = "BV700_V2_streaming"
    
    # Database
    database_url: str = "sqlite:///./word_memory.db"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
