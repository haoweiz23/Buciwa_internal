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
    Generate the prompt for cloze test generation.
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


def get_cloze_test_with_distractors_prompt(word1: str, word2: str) -> str:
    """
    Generate the prompt for cloze test with distractors generation.
    This generates a cloze test with:
    - Two main words
    - Two distractor words
    - Chinese sentence with blanks
    - English sentence with blanks
    
    Args:
        word1: First English word (main)
        word2: Second English word (main)
    
    Returns:
        str: The formatted prompt
    """
    return f"""你是一个英语教学专家。请为以下两个英语单词生成一个完形填空练习。

主要单词：
- {word1}
- {word2}

要求：
1. 生成一个包含这两个单词的中文句子，用 ___ 表示空格（两个空格）
2. 生成一个包含这两个单词的英文句子，用 ___ 表示空格（两个空格）
3. 生成两个干扰选项（与句子语境相关但不是正确答案的英语单词）
4. 干扰选项应该是与主要单词词性相同、但意思不同的词
5. 生成一个用于生成配图的提示词（中文描述场景）

请严格按照以下JSON格式返回，不要添加任何其他内容：

```json
{{
    "sentence": "中文句子，包含两个___空格",
    "sentence_with_answers": "中文句子，包含{word1}和{word2}",
    "sentence_en": "English sentence with two ___ blanks",
    "sentence_with_answers_en": "English sentence with {word1} and {word2}",
    "word1_meaning": "{word1}的中文释义",
    "word2_meaning": "{word2}的中文释义",
    "distractor1": "干扰词1",
    "distractor2": "干扰词2",
    "distractor1_meaning": "干扰词1的中文释义",
    "distractor2_meaning": "干扰词2的中文释义",
    "image_prompt": "用于生成配图的中文提示词，描述句子场景"
}}
```

注意：
- 句子应该自然流畅，符合日常使用场景
- 空格位置应该合理，使得填空练习有意义
- 干扰词应该有一定的迷惑性，但不能是正确答案
- 英文句子和中文句子的意思应该对应"""


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
    template = extract_template_section(content, "7. 听力练习生成提示词")
    # Replace placeholder with actual value
    return template.replace("{scene_description}", scene_description)
