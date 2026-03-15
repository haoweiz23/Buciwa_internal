"""
Test script for Doubao API calls
================================

This script tests the LLM and Image generation APIs independently.
Run with: python test_api.py
"""

import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI


def test_llm():
    """Test the LLM API with a simple word"""
    print("=" * 50)
    print("Testing LLM API (doubao-seed-1-8-251228)")
    print("=" * 50)
    
    api_key = os.getenv("ARK_API_KEY")
    if not api_key:
        print("ERROR: ARK_API_KEY not found in environment variables")
        return False
    
    print(f"API Key: {api_key[:10]}...")
    
    client = OpenAI(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=api_key,
    )
    
    test_word = "happy"
    prompt = f"""Given the English word "{test_word}", please provide:

1. A similar-looking word (形近词)
2. A synonym (近义词)
3. An antonym (反义词)

Please respond in the following JSON format only:
{{
    "similar_word": "the similar-looking word",
    "synonym": "the synonym",
    "antonym": "the antonym"
}}

Make sure the response is valid JSON only, no additional text."""

    print(f"\nSending prompt for word: '{test_word}'")
    print("-" * 30)
    
    try:
        response = client.chat.completions.create(
            model="doubao-seed-1-8-251228",
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
        print("Response received:")
        print(content)
        print("-" * 30)
        print("[PASS] LLM API test PASSED")
        return True
        
    except Exception as e:
        print(f"[FAIL] LLM API test FAILED: {e}")
        return False


def test_image_generation():
    """Test the Image Generation API"""
    print("\n" + "=" * 50)
    print("Testing Image API (doubao-seedream-4-0-250828)")
    print("=" * 50)
    
    api_key = os.getenv("ARK_API_KEY")
    if not api_key:
        print("ERROR: ARK_API_KEY not found in environment variables")
        return False
    
    client = OpenAI(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=api_key,
    )
    
    test_prompt = "A beautiful sunset over a calm ocean, warm orange and pink colors, peaceful atmosphere, digital art style"
    
    print(f"\nGenerating image with prompt:")
    print(f"'{test_prompt[:50]}...'")
    print("-" * 30)
    
    try:
        response = client.images.generate(
            model="doubao-seedream-4-0-250828",
            prompt=test_prompt,
            size="1024x1024",
            response_format="url",
            extra_body={
                "watermark": False,
            }
        )
        
        image_url = response.data[0].url
        print("Image URL received:")
        print(image_url)
        print("-" * 30)
        print("[PASS] Image API test PASSED")
        return True
        
    except Exception as e:
        print(f"[FAIL] Image API test FAILED: {e}")
        return False


def main():
    print("\n" + "=" * 60)
    print("  Doubao API Test Script")
    print("=" * 60)
    
    # Check environment
    api_key = os.getenv("ARK_API_KEY")
    if api_key:
        print(f"\n[OK] ARK_API_KEY found: {api_key[:10]}...{api_key[-4:]}")
    else:
        print("\n[ERROR] ARK_API_KEY not found!")
        print("Please create a .env file with your API key:")
        print("ARK_API_KEY=your_api_key_here")
        return
    
    # Run tests
    llm_success = test_llm()
    image_success = test_image_generation()
    
    # Summary
    print("\n" + "=" * 60)
    print("  Test Summary")
    print("=" * 60)
    print(f"LLM API:        {'[PASS]' if llm_success else '[FAIL]'}")
    print(f"Image API:      {'[PASS]' if image_success else '[FAIL]'}")
    print("=" * 60)
    
    if llm_success and image_success:
        print("\nAll tests passed! The APIs are working correctly.")
    else:
        print("\nSome tests failed. Please check the errors above.")


if __name__ == "__main__":
    main()
