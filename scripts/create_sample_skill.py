"""
Sample Skill: Novel Chapter Writer
This skill helps generate creative chapter content for novels.
"""

SAMPLE_SKILL = {
    "name": "小说章节写作助手",
    "description": "根据给定的情节提示，生成创意丰富、情节紧凑的小说章节内容。支持多种风格：浪漫、悬疑、科幻、奇幻等。",
    "config": {
        "style": "现实主义",
        "mood": "悬疑",
        "min_words": 1000,
        "max_words": 3000
    },
    "code": """
# 小说章节写作技能

## 任务
根据用户提供的情节要素，创作一个引人入胜的小说章节。

## 输入格式
用户会提供：
- 章节标题
- 主要人物
- 故事背景
- 上一章结尾的悬念（如果有）
- 希望发展的情节方向

## 写作要求
1. 开篇要吸引读者，可以用场景描写、对话或事件引入
2. 人物对话要符合角色性格，避免过于现代化
3. 适当添加心理描写，让人物更立体
4. 情节发展要自然流畅，避免突兀的转折
5. 设置适当的悬念或钩子，为下一章铺垫
6. 注意节奏把控，高潮部分要写得精彩

## 输出格式
直接输出章节内容，不需要额外说明。

## 风格指南
- 使用第三人称全知视角
- 场景描写要生动具体
- 对话用引号标注
- 适度使用比喻和拟人等修辞
"""
}


def get_skill_prompt(parameters: dict) -> str:
    """Generate the actual writing prompt from parameters"""
    title = parameters.get("title", "")
    characters = parameters.get("characters", "")
    setting = parameters.get("setting", "")
    previous_hook = parameters.get("previous_hook", "")
    direction = parameters.get("direction", "")
    
    return f"""请根据以下要素创作一个小说章节：

章节标题：{title}

主要人物：{characters}

故事背景：{setting}

上章悬念：{previous_hook}

本章节方向：{direction}

请创作一个引人入胜的章节内容。"""
