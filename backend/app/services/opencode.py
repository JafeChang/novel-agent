import os
import httpx
from typing import Optional


class OpenCodeService:
    """Service to integrate with E2B for skill execution (E2B-only mode)."""

    def __init__(self):
        self.e2b_api_key = os.environ.get("E2B_API_KEY", "").strip()
        self.e2b_sandbox_id = os.environ.get("E2B_SANDBOX_ID", "").strip()
        self.timeout = 120.0

    @property
    def use_e2b(self) -> bool:
        return bool(self.e2b_api_key and self.e2b_sandbox_id)

    async def execute_skill(self, prompt: str, context: Optional[dict] = None) -> dict:
        """
        Execute a skill using E2B only.

        Args:
            prompt: The skill prompt to execute
            context: Optional context (chapter content, parameters, etc.)

        Returns:
            dict with success status and output/error
        """
        if not self.use_e2b:
            return {
                "success": False,
                "error": "E2B 未配置，请设置 E2B_API_KEY 和 E2B_SANDBOX_ID"
            }

        full_prompt = self._build_prompt(prompt, context)
        return await self._execute_via_e2b(full_prompt)

    async def _execute_via_e2b(self, prompt: str) -> dict:
        """Execute via E2B cloud sandbox"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"https://api.e2b.dev/v1/sandboxes/{self.e2b_sandbox_id}/run",
                    json={
                        "model": "gpt-4o",
                        "prompt": prompt,
                        "stream": False,
                    },
                    headers={
                        "Authorization": f"Bearer {self.e2b_api_key}",
                        "Content-Type": "application/json",
                    },
                )
                response.raise_for_status()
                result = response.json()

                return {
                    "success": True,
                    "output": result.get("output", ""),
                    "usage": result.get("usage", {}),
                }
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "执行超时，请稍后重试",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"E2B 执行失败: {str(e)}",
            }

    def _build_prompt(self, skill_prompt: str, context: Optional[dict]) -> str:
        """Build a complete prompt with context"""
        if not context:
            return skill_prompt

        context_str = ""
        if "chapter_content" in context:
            context_str += f"\n\n## 当前章节内容\n{context['chapter_content']}\n"
        if "parameters" in context:
            context_str += f"\n## 用户参数\n{context['parameters']}\n"
        if "style" in context:
            context_str += f"\n## 写作风格\n{context['style']}\n"

        return f"""{skill_prompt}{context_str}

## 执行指令
请严格按照上述技能描述执行，并返回结果。"""

    async def health_check(self) -> bool:
        """Check if E2B is available and sandbox is reachable."""
        if not self.use_e2b:
            return False

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"https://api.e2b.dev/v1/sandboxes/{self.e2b_sandbox_id}",
                    headers={
                        "Authorization": f"Bearer {self.e2b_api_key}",
                        "Content-Type": "application/json",
                    },
                )
                return response.status_code < 400
        except Exception:
            return False


# Singleton instance
opencode_service = OpenCodeService()
