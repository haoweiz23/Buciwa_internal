"""
LLM Prompts Configuration
=========================

This module loads prompts from the prompts.md file and provides functions
to generate formatted prompts for the LLM API calls.
"""

import os
import re


def load_prompts_file() -> str:
    """Load the entire prompts.md file content."""
    prompts_file = os.path.join(os.path.dirname(__file__), "..", "prompts.md")
    with open(prompts_file, "r", encoding="utf-8") as f:
        return f.read()


def extract_template_section(content: str, section_title: str) -> str:
    """
    Extract a template section from the prompts.md content.
    Handles nested code blocks properly.
    
    Args:
        content: The full content of prompts.md
        section_title: The title of the section to extract (e.g., "1. 单词生成提示词")
    
    Returns:
        str: The extracted template content
    """
    # Find the section starting with ## {section_title}
    section_pattern = rf'## {re.escape(section_title)}'
    section_match = re.search(section_pattern, content)
    if not section_match:
        raise ValueError(f"Could not find section: {section_title}")
    
    # Find the ### 模板 part after the section title
    template_start = content.find("### 模板", section_match.end())
    if template_start == -1:
        raise ValueError(f"Could not find template in section: {section_title}")
    
    # Find the opening ``` after ### 模板
    code_start = content.find("```", template_start)
    if code_start == -1:
        raise ValueError(f"Could not find opening code block in section: {section_title}")
    
    code_start += 3  # Skip past ```
    
    # Find the matching closing ``` by counting nested code blocks
    pos = code_start
    depth = 1
    while pos < len(content) and depth > 0:
        next_backtick = content.find("```", pos)
        if next_backtick == -1:
            break
        # Check if this is opening or closing
        # Opening: ``` followed by optional language specifier and newline
        # Closing: ``` followed by newline or end
        after_backtick = content[next_backtick + 3: next_backtick + 20]
        if after_backtick.startswith("\n") or after_backtick == "":
            # This is a closing block
            depth -= 1
            if depth == 0:
                return content[code_start:next_backtick].strip()
        else:
            # This is an opening block (with language specifier like json)
            depth += 1
        pos = next_backtick + 3
    
    # Fallback: return everything until the next section (##) or end
    next_section = content.find("\n---", code_start)
    if next_section == -1:
        next_section = len(content)
    return content[code_start:next_section].strip().rstrip("```").strip()


def get_word_generation_prompt(word: str) -> str:
    """
    Generate the prompt for word generation with visual isolation.
    Loads the template from prompts.md and formats it with the given word.
    
    Args:
        word: The input word to generate options for
    
    Returns:
        str: The formatted prompt
    """
    content = load_prompts_file()
    template = extract_template_section(content, "1. 单词生成提示词")
    # Replace {word} placeholder with the actual word
    return template.replace("{word}", word)


def get_single_image_prompt(word: str, word_type: str) -> str:
    """
    Generate the prompt for a single image generation.
    Loads the template from prompts.md and formats it with the given word.
    
    Args:
        word: The word to generate an image prompt for
        word_type: Type of word (A/B/C/D)
    
    Returns:
        str: The formatted prompt
    """
    content = load_prompts_file()
    template = extract_template_section(content, "2. 单图提示词生成")
    # Replace placeholders with actual values
    return template.replace("{word}", word).replace("{word_type}", word_type)


def get_cloze_test_prompt(word1: str, word2: str) -> str:
    """
    Generate the prompt for cloze test generation with distractors.
    This generates a cloze test with:
    - Two main words
    - Two distractor words
    - Chinese sentence with blanks
    - English sentence with blanks
    
    Loads the template from prompts.md and formats it with the given words.
    
    Args:
        word1: First English word
        word2: Second English word
    
    Returns:
        str: The formatted prompt
    """
    content = load_prompts_file()
    template = extract_template_section(content, "6. 完形填空题目生成提示词")
    # Replace placeholders with actual values
    return template.replace("{word1}", word1).replace("{word2}", word2)


def get_listening_exercise_prompt(scene_description: str) -> str:
    """
    Generate the prompt for listening exercise generation.
    Loads the template from prompts.md and formats it with the given scene description.
    
    Args:
        scene_description: User's description of the scene
    
    Returns:
        str: The formatted prompt
    """
    content = load_prompts_file()
    template = extract_template_section(content, "8. 听力练习生成提示词")
    # Replace placeholder with actual value
    return template.replace("{scene_description}", scene_description)
