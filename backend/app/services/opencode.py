import httpx
from typing import Optional
from app.core.config import settings


class OpenCodeService:
    """Service to integrate with OpenCode for skill execution"""
    
    def __init__(self):
        self.api_url = settings.OPENCODE_API_URL
        self.timeout = 120.0
    
    async def execute_skill(self, prompt: str, context: Optional[dict] = None) -> dict:
        """
        Execute a skill using OpenCode
        
        Args:
            prompt: The skill prompt to execute
            context: Optional context (chapter content, parameters, etc.)
        
        Returns:
            dict with success status and output/error
        """
        full_prompt = self._build_prompt(prompt, context)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_url}/execute",
                    json={"prompt": full_prompt},
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                result = response.json()
                return {
                    "success": True,
                    "output": result.get("output", result.get("response", "")),
                    "usage": result.get("usage", {})
                }
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "执行超时，请稍后重试"
            }
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"OpenCode API 错误: {e.response.status_code}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"执行失败: {str(e)}"
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
        """Check if OpenCode is available"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.api_url}/health")
                return response.status_code == 200
        except:
            return False


# Singleton instance
opencode_service = OpenCodeService()
