import asyncio
import subprocess
import json
import os
import shutil
import httpx
from typing import Optional


class OpenCodeService:
    """Service to integrate with OpenCode CLI or E2B for skill execution"""
    
    def __init__(self):
        self.e2b_api_key = os.environ.get("E2B_API_KEY")
        self.e2b_sandbox_id = os.environ.get("E2B_SANDBOX_ID")
        self.use_e2b = bool(self.e2b_api_key and self.e2b_sandbox_id)
        self.timeout = 120.0
        # Avoid concurrent CLI runs stepping on shared cwd/session state.
        max_parallel = int(os.environ.get("OPENCODE_MAX_PARALLEL", "1"))
        self._semaphore = asyncio.Semaphore(max_parallel)

        # Build a subprocess environment that guarantees the npm global bin
        # directory (/usr/local/bin) is on PATH, regardless of how the Python
        # process was launched.
        self._subprocess_env = os.environ.copy()
        npm_bin = "/usr/local/bin"
        current_path = self._subprocess_env.get("PATH", "")
        if npm_bin not in current_path.split(os.pathsep):
            self._subprocess_env["PATH"] = f"{npm_bin}{os.pathsep}{current_path}"

        # Resolve the opencode binary to its full path so subprocess never
        # has to rely on PATH lookup at call time.
        cmd_override = os.environ.get("OPENCODE_CMD", "opencode")
        resolved = shutil.which(cmd_override, path=self._subprocess_env["PATH"])
        self.opencode_cmd = resolved if resolved else cmd_override
    
    async def execute_skill(self, prompt: str, context: Optional[dict] = None) -> dict:
        """
        Execute a skill using OpenCode CLI or E2B
        
        Args:
            prompt: The skill prompt to execute
            context: Optional context (chapter content, parameters, etc.)
        
        Returns:
            dict with success status and output/error
        """
        full_prompt = self._build_prompt(prompt, context)
        
        async with self._semaphore:
            if self.use_e2b:
                return await self._execute_via_e2b(full_prompt)
            
            # Local fallback when OpenCode CLI is unavailable
            if not await self.health_check():
                return self._execute_via_local_fallback(context)
            
            return await self._execute_via_cli(full_prompt)
    
    async def _execute_via_e2b(self, prompt: str) -> dict:
        """Execute via E2B cloud sandbox"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"https://api.e2b.dev/v1/sandboxes/{self.e2b_sandbox_id}/run",
                    json={
                        "model": "gpt-4o",
                        "prompt": prompt,
                        "stream": False
                    },
                    headers={
                        "Authorization": f"Bearer {self.e2b_api_key}",
                        "Content-Type": "application/json"
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                return {
                    "success": True,
                    "output": result.get("output", ""),
                    "usage": result.get("usage", {})
                }
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "执行超时，请稍后重试"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"E2B 执行失败: {str(e)}"
            }
    
    async def _execute_via_cli(self, prompt: str) -> dict:
        """Execute via local OpenCode CLI"""
        try:
            # Use opencode run with JSON format
            result = subprocess.run(
                [self.opencode_cmd, "run", "--format", "json", "--", prompt],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=os.environ.get("OPENCODE_CWD", "/home/node/.openclaw/workspace"),
                env=self._subprocess_env,
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"OpenCode error: {result.stderr or 'unknown error'}"
                }
            
            # Parse JSON output - last line contains the final response
            output_lines = result.stdout.strip().split('\n')
            final_output = ""
            
            for line in reversed(output_lines):
                try:
                    event = json.loads(line)
                    if event.get("type") == "text" and "text" in event.get("part", {}):
                        final_output = event["part"]["text"]
                        break
                except json.JSONDecodeError:
                    continue
            
            # If no text found in events, try to get the last text event
            if not final_output:
                for line in output_lines:
                    try:
                        event = json.loads(line)
                        if event.get("type") == "text":
                            final_output = event.get("part", {}).get("text", "")
                    except json.JSONDecodeError:
                        continue
            
            return {
                "success": True,
                "output": final_output,
                "usage": {}
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "执行超时，请稍后重试"
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": "OpenCode CLI 未找到，请确保已安装: npm install -g opencode-ai"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"执行失败: {str(e)}"
            }

    def _execute_via_local_fallback(self, context: Optional[dict]) -> dict:
        """Fallback execution when OpenCode CLI is not installed."""
        chapter_content = (context or {}).get("chapter_content", "")
        parameters = (context or {}).get("parameters", {})

        if chapter_content:
            polished = chapter_content.strip()
            polished = "\n".join(line.rstrip() for line in polished.splitlines())
            while "\n\n\n" in polished:
                polished = polished.replace("\n\n\n", "\n\n")
            focus = parameters.get("focus", "节奏与可读性")
            output = (
                "【本地降级模式】未检测到 OpenCode CLI，已返回基础润色结果。\n\n"
                "修改后正文：\n"
                f"{polished}\n\n"
                "修改说明：\n"
                f"1. 保留原剧情与设定，仅做轻量文本整理。\n"
                f"2. 清理多余空行与行尾空白，提升可读性。\n"
                f"3. 建议安装 OpenCode CLI 以获得更强的智能润色效果（当前关注点：{focus}）。"
            )
        else:
            output = (
                "【本地降级模式】未检测到 OpenCode CLI，且未提供章节内容。\n"
                "请先传入 chapter_content（或 chapter_id），"
                "或安装 OpenCode CLI：npm install -g opencode-ai。"
            )

        return {
            "success": True,
            "output": output,
            "usage": {"fallback": "local_without_opencode_cli"}
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
        """Check if OpenCode CLI is available"""
        if self.use_e2b:
            return True  # E2B is always available if configured
        try:
            result = subprocess.run(
                [self.opencode_cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                env=self._subprocess_env,
            )
            return result.returncode == 0
        except:
            return False


# Singleton instance
opencode_service = OpenCodeService()
