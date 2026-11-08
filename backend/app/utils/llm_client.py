import os
import httpx
from typing import List, Dict, Any, Optional

class LLMClient:
    def __init__(self):
        self.api_base = os.getenv("VLLM_API_BASE", "http://localhost:8000/v1")
        self.model_name = os.getenv("VLLM_MODEL_NAME", "qwen2.5-14b-awq")
        self.api_key = "EMPTY"
        
    async def generate_recommendation_reason(self, work_order_code: str, process_name: str, candidate_info: Dict[str, Any]) -> Optional[str]:
        prompt = f"""请作为医疗器械车间智能排产助手，生成一句话派工推荐理由（无需寒暄与客套话）。
工单编号：{work_order_code} (工序: {process_name})
推荐员工：{candidate_info['name']} (工号: {candidate_info['emp_id']})
匹配依据：
- 具备核心技能：{', '.join(candidate_info.get('skills', []))}
- 9月累计加班时长：{candidate_info.get('overtime_hours', 0)}小时 (合规范围内)
- 今日排班状态：{candidate_info.get('shift_status', '正常在岗')}
- 前一工作日考评：{candidate_info.get('recent_score', 86)}分

请一句话输出推荐理由，例如：'推荐王军：持有中包装技能认证，今日白班在岗，累计加班合规且前日考评表现优良。'"""

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 100
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.api_base}/chat/completions", json=payload, headers=headers, timeout=3.0)
                if response.status_code == 200:
                    data = response.json()
                    content = data['choices'][0]['message']['content'].strip()
                    if content and len(content) > 5:
                        return content
        except Exception:
            pass
        return None

llm_client = LLMClient()
