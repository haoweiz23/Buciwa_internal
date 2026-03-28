import json
from openai import OpenAI
from app.config import get_settings
from app.prompts import get_word_generation_prompt, get_single_image_prompt, get_cloze_test_prompt, get_listening_exercise_prompt

settings = get_settings()


class LLMService:
    """Service for interacting with Doubao LLM API using OpenAI compatible client"""
    
    def __init__(self):
        self.client = OpenAI(
            base_url=settings.ark_base_url,
            api_key=settings.ark_api_key,
        )
        self.model = settings.llm_model
    
    def generate_word_options(self, word: str) -> dict:
        """
        Generate similar word, synonyms, and image prompts for the given word.
        Uses visual isolation protocol to ensure no visual/logical overlap.
        
        Returns:
            dict: {
                "similar_word": str,  # B选项 - 形近词
                "synonym": str,       # C选项 - 无关名词1
                "antonym": str,       # D选项 - 无关名词2
                "prompts": {
                    "main": str,      # A选项提示词
                    "similar": str,   # B选项提示词
                    "synonym": str,   # C选项提示词
                    "antonym": str    # D选项提示词
                }
            }
        """
        prompt = get_word_generation_prompt(word)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        content = response.choices[0].message.content
        
        # Parse JSON response
        try:
            # Try to extract JSON from the response
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            result = json.loads(content)
            
            # Transform the new format to the expected format
            # New format: {"words": {"A":..., "B":..., "C":..., "D":...}, "prompts": {...}}
            # Expected format: {"similar_word":..., "synonym":..., "antonym":..., "prompts": {...}}
            
            if "words" in result:
                # New format
                transformed = {
                    "similar_word": result["words"].get("B", ""),
                    "synonym": result["words"].get("C", ""),
                    "antonym": result["words"].get("D", ""),
                    "prompts": {
                        "main": result["prompts"].get("A", ""),
                        "similar": result["prompts"].get("B", ""),
                        "synonym": result["prompts"].get("C", ""),
                        "antonym": result["prompts"].get("D", "")
                    },
                    "meanings": result.get("meanings", {})
                }
                return transformed
            else:
                # Old format - return as is
                return result
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse LLM response as JSON: {e}\nResponse: {content}")
    
    def generate_image_prompt(self, word: str, word_type: str) -> str:
        """
        Generate an image prompt for a single word.
        
        Args:
            word: The word to generate prompt for
            word_type: Type of word (A/B/C/D)
        
        Returns:
            str: Image generation prompt in Chinese
        """
        prompt = get_single_image_prompt(word, word_type)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_cloze_test(self, word1: str, word2: str) -> dict:
        """
        Generate a cloze test with two main words and two distractor words.
        Generates both Chinese and English sentences.
        
        Args:
            word1: First English word
            word2: Second English word
        
        Returns:
            dict: {
                "sentence": str,  # Chinese sentence with blanks (using ___)
                "sentence_with_answers": str,  # Chinese sentence with answers
                "sentence_en": str,  # English sentence with blanks (using ___)
                "sentence_with_answers_en": str,  # English sentence with answers
                "word1_meaning": str,
                "word2_meaning": str,
                "distractor1": str,  # First distractor word
                "distractor2": str,  # Second distractor word
                "distractor1_meaning": str,
                "distractor2_meaning": str,
                "image_prompt": str
            }
        """
        prompt = get_cloze_test_prompt(word1, word2)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        content = response.choices[0].message.content
        
        try:
            # Try to extract JSON from the response
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            result = json.loads(content)
            return result
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse LLM response as JSON: {e}\nResponse: {content}")
    
    def generate_listening_text(self, scene_description: str) -> dict:
        """
        Generate text for listening exercise based on scene description.
        
        Args:
            scene_description: User's description of the scene
        
        Returns:
            dict: {
                "text": str,  # English text for TTS
                "image_prompt": str  # Image generation prompt
            }
        """
        prompt = get_listening_exercise_prompt(scene_description)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        
        try:
            # Try to extract JSON from the response
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            result = json.loads(content)
            return result
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse LLM response as JSON: {e}\nResponse: {content}")


# Create a singleton instance
llm_service = LLMService()
