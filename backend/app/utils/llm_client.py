import os
import httpx
from typing import List, Dict, Any

class LLMClient:
    def __init__(self):
        self.api_base = os.getenv("VLLM_API_BASE", "http://localhost:8000/v1")
        self.model_name = os.getenv("VLLM_MODEL_NAME", "qwen2.5-14b-awq")
        self.api_key = "EMPTY" # vLLM local usually doesn't need a real key
        
    async def generate_recommendation_reason(self, work_order_code: str, process_name: str, candidate_info: Dict[str, Any]) -> str:
        prompt = f"""
请你作为车间智能排产助手，为接下来的派工生成一段自然、易读的推荐理由。
当前工单：{work_order_code} (工序: {process_name})
推荐员工：{candidate_info['name']} (工号: {candidate_info['emp_id']})
匹配依据：
- 具备该工序需要的核心技能：{', '.join(candidate_info['skills'])}
- 本月累计加班时长：{candidate_info['overtime_hours']}小时 (合规范围内)
- 当前排班状态：{candidate_info['shift_status']}

请用一句话直接输出推荐理由（无需寒暄），例如：'推荐张三：拥有切割技能认证，本月加班合规且当前处于空闲状态。'
"""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 100
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.api_base}/chat/completions", json=payload, headers=headers, timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    return data['choices'][0]['message']['content'].strip()
                return f"基于技能和排班规则自动推荐。({response.status_code})"
        except Exception as e:
            print(f"LLM Call Error: {e}")
            return "系统按规则自动推荐（模型服务暂不可用）。"

llm_client = LLMClient()
