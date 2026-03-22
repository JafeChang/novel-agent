from sqlalchemy.orm import Session
from app.models.skill import Skill


def ensure_default_public_novel_skill(db: Session, owner_id: int) -> None:
    """Ensure a shared public default skill exists and matches OpenCode prompt style."""
    default_name = "公共小说润色助手"
    default_description = "通用公共技能：优化章节文风、节奏与对白，保持人设一致。"
    default_config = {
        "style": "叙事流畅、细节具体、对白自然",
        "target_length": "保持原文长度上下浮动 10%",
        "focus": ["节奏", "情绪", "人设一致性", "可读性"],
    }
    default_code = """
# 公共小说润色助手

## 任务
在不改变核心剧情、世界观设定和人物关系的前提下，对用户提供的章节文本进行润色。

## 输入
- 章节原文：优先使用上下文中的 `chapter_content`
- 可选参数（来自 parameters）：
  - tone: 语气（如“克制/热烈/冷峻”）
  - focus: 重点（如“对白/节奏/氛围”）
  - min_change: 最小改动（true/false）

## 执行要求
1. 不新增关键设定，不篡改剧情走向。
2. 优先修复拗口句、重复表达和逻辑不顺。
3. 对白应符合人物身份与当前情绪。
4. 关键场景提升画面感与情绪张力。
5. 保持原文长度在目标区间（上下浮动 10%）。

## 输出格式
1. 修改后正文
2. 修改说明（3-5条，逐条解释修改意图）
"""

    default_skill = db.query(Skill).filter(Skill.name == default_name, Skill.is_public == 1).first()
    if default_skill:
        default_skill.description = default_description
        default_skill.config = default_config
        default_skill.code = default_code.strip()
        db.commit()
        return

    skill = Skill(
        user_id=owner_id,
        name=default_name,
        description=default_description,
        config=default_config,
        code=default_code.strip(),
        is_public=1,
    )
    db.add(skill)
    db.commit()
