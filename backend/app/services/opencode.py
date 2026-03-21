import subprocess
import json
import os
from typing import Optional


class OpenCodeService:
    """Service to integrate with OpenCode CLI for skill execution"""
    
    def __init__(self):
        self.opencode_cmd = os.environ.get("OPENCODE_CMD", "opencode")
        self.timeout = 120.0
    
    async def execute_skill(self, prompt: str, context: Optional[dict] = None) -> dict:
        """
        Execute a skill using OpenCode CLI
        
        Args:
            prompt: The skill prompt to execute
            context: Optional context (chapter content, parameters, etc.)
        
        Returns:
            dict with success status and output/error
        """
        full_prompt = self._build_prompt(prompt, context)
        
        try:
            # Use opencode run with JSON format
            result = subprocess.run(
                [self.opencode_cmd, "run", "--format", "json", "--", full_prompt],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=os.environ.get("OPENCODE_CWD", "/home/node/.openclaw/workspace")
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
                    elif event.get("type") == "step_finish":
                        # Extract any text from step_finish if no direct text found yet
                        pass
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
        try:
            result = subprocess.run(
                [self.opencode_cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False


# Singleton instance
opencode_service = OpenCodeService()
