import asyncio
import json
import time
from collections import defaultdict, deque
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.user_plan import UserPlan
from app.models.project import Project


DEFAULT_PLAN_CONFIG: Dict[str, Dict[str, Any]] = {
    "free": {
        "price_monthly": 0,
        "available_models": ["gpt-4o-mini"],
        "model_rate_per_minute": 10,
        "opencode_concurrency": 1,
        "novel_limit": 3,
        "human_support": False,
    },
    "plus": {
        "price_monthly": 19,
        "available_models": ["gpt-4o-mini", "gpt-4.1-mini"],
        "model_rate_per_minute": 30,
        "opencode_concurrency": 2,
        "novel_limit": 20,
        "human_support": False,
    },
    "pro": {
        "price_monthly": 49,
        "available_models": ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1"],
        "model_rate_per_minute": 80,
        "opencode_concurrency": 4,
        "novel_limit": 100,
        "human_support": True,
    },
    "max": {
        "price_monthly": 99,
        "available_models": ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1", "gpt-4.1-pro"],
        "model_rate_per_minute": 200,
        "opencode_concurrency": 8,
        "novel_limit": 500,
        "human_support": True,
    },
}


class PlanService:
    def __init__(self):
        self._plan_cache = self._load_plan_config()
        self._lock = asyncio.Lock()
        self._user_running = defaultdict(int)
        self._user_requests = defaultdict(deque)

    def _load_plan_config(self) -> Dict[str, Dict[str, Any]]:
        raw = settings.PLAN_ENTITLEMENTS_JSON.strip() if settings.PLAN_ENTITLEMENTS_JSON else ""
        if not raw:
            return DEFAULT_PLAN_CONFIG
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
        return DEFAULT_PLAN_CONFIG

    def get_plans(self) -> Dict[str, Dict[str, Any]]:
        return self._plan_cache

    def get_plan(self, tier: str) -> Dict[str, Any]:
        return self._plan_cache.get(tier, self._plan_cache["free"])

    def get_or_create_user_tier(self, db: Session, user_id: int) -> str:
        up = db.query(UserPlan).filter(UserPlan.user_id == user_id).first()
        if up:
            return up.tier
        up = UserPlan(user_id=user_id, tier="free")
        db.add(up)
        db.commit()
        return "free"

    def set_user_tier(self, db: Session, user_id: int, tier: str) -> str:
        if tier not in self._plan_cache:
            raise ValueError("Invalid tier")
        up = db.query(UserPlan).filter(UserPlan.user_id == user_id).first()
        if not up:
            up = UserPlan(user_id=user_id, tier=tier)
            db.add(up)
        else:
            up.tier = tier
        db.commit()
        return tier

    def check_project_limit(self, db: Session, user_id: int, tier: str) -> tuple[bool, str]:
        limit = int(self.get_plan(tier).get("novel_limit", 0))
        if limit <= 0:
            return True, ""
        current = db.query(Project).filter(Project.user_id == user_id).count()
        if current >= limit:
            return False, f"当前套餐({tier})最多可创建 {limit} 本小说"
        return True, ""

    async def before_skill_execute(self, user_id: int, tier: str, model: str | None) -> tuple[bool, str]:
        plan = self.get_plan(tier)
        allowed_models = plan.get("available_models", [])
        if model and allowed_models and model not in allowed_models:
            return False, f"当前套餐({tier})不支持模型: {model}"

        async with self._lock:
            max_concurrency = int(plan.get("opencode_concurrency", 1))
            if self._user_running[user_id] >= max_concurrency:
                return False, f"当前套餐({tier})并发上限为 {max_concurrency}"

            rpm = int(plan.get("model_rate_per_minute", 0))
            if rpm > 0:
                now = time.time()
                q = self._user_requests[user_id]
                while q and now - q[0] > 60:
                    q.popleft()
                if len(q) >= rpm:
                    return False, f"当前套餐({tier})模型速率上限为 {rpm}/分钟"
                q.append(now)

            self._user_running[user_id] += 1
            return True, ""

    async def after_skill_execute(self, user_id: int) -> None:
        async with self._lock:
            if self._user_running[user_id] > 0:
                self._user_running[user_id] -= 1


plan_service = PlanService()
