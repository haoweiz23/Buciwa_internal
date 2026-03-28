import httpx
import base64
import os
import uuid
from pathlib import Path
from typing import Optional
from openai import OpenAI
from app.config import get_settings

settings = get_settings()


class ImageService:
    """Service for interacting with Doubao Image Generation API using OpenAI compatible client"""
    
    def __init__(self):
        self.client = OpenAI(
            base_url=settings.ark_base_url,
            api_key=settings.ark_api_key,
        )
        self.model = settings.image_model
        # Create images directory if it doesn't exist
        # Use relative path from working directory (backend/)
        self.images_dir = Path("static/images")
        self.images_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_image(self, prompt: str, word: str) -> dict:
        """
        Generate an image using Doubao Seedream 4.0 API.
        
        Args:
            prompt: Image generation prompt
            word: The word for naming the file
        
        Returns:
            dict: {
                "image_url": str (URL from API),
                "local_path": str (local file path)
            }
        """
        response = self.client.images.generate(
            model=self.model,
            prompt=prompt,
            size="1024x1024",
            response_format="url",
            extra_body={
                "watermark": False,
            }
        )
        
        image_url = response.data[0].url
        
        result = {
            "image_url": image_url,
            "local_path": ""
        }
        
        # Download and save locally
        if image_url:
            local_path = self._download_and_save(image_url, word)
            result["local_path"] = local_path
        
        return result
    
    def _download_and_save(self, url: str, word: str) -> str:
        """Download image from URL and save locally"""
        response = httpx.get(url, timeout=60.0)
        if response.status_code == 200:
            # Generate unique filename
            filename = f"{word}_{uuid.uuid4().hex[:8]}.png"
            filepath = self.images_dir / filename
            
            # Save image
            with open(filepath, "wb") as f:
                f.write(response.content)
            
            return f"/static/images/{filename}"
        else:
            raise Exception(f"Failed to download image: {response.status_code}")
    
    def get_image_path(self, relative_path: str) -> Optional[str]:
        """Get absolute path for a relative image path"""
        if relative_path:
            # Remove /static/ prefix if present
            clean_path = relative_path.replace("/static/", "")
            # Use relative path from working directory (backend/)
            full_path = Path("static") / clean_path
            if full_path.exists():
                return str(full_path)
        return None


# Create a singleton instance
image_service = ImageService()
