import os
import json
import logging
import urllib.request
import urllib.parse
from app.core.database import SessionLocal
from app.models.system import SysConfig

logger = logging.getLogger(__name__)

DEFAULT_DINGTALK_URL = os.getenv("DINGTALK_SERVICE_URL", "http://10.11.100.154:8089")
if "dingtalk.internal" in DEFAULT_DINGTALK_URL:
    DEFAULT_DINGTALK_URL = "http://10.11.100.154:8089"

def get_dingtalk_service_url():
    """获取钉钉服务 Base URL"""
    db = SessionLocal()
    try:
        cfg = db.query(SysConfig).filter(SysConfig.config_key == "DINGTALK_SERVICE_URL").first()
        if cfg and cfg.config_value and cfg.config_value.strip():
            url = cfg.config_value.strip()
            if "dingtalk.internal" not in url:
                return url
        return DEFAULT_DINGTALK_URL
    finally:
        db.close()

def test_dingtalk_connection():
    """测试钉钉服务连通性及响应延迟"""
    import time
    start = time.time()
    base_url = get_dingtalk_service_url().rstrip('/')
    test_url = f"{base_url}/api/users?limit=1"
    try:
        req = urllib.request.Request(test_url, headers={"User-Agent": "Human-Agent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            latency = int((time.time() - start) * 1000)
            return {
                "success": resp.getcode() == 200,
                "latency_ms": latency,
                "url": base_url,
                "message": "钉钉服务连通正常"
            }
    except Exception as e:
        latency = int((time.time() - start) * 1000)
        return {
            "success": False,
            "latency_ms": latency,
            "url": base_url,
            "error": str(e),
            "message": f"连接钉钉服务失败: {e}"
        }

def get_dingtalk_user_by_employee_id(employee_id: str):
    """
    通过员工工号从钉钉服务(8089)解析对应的钉钉用户信息及 dingtalkUserId
    """
    clean_id = str(employee_id).strip()
    if not clean_id:
        return None
        
    base_url = get_dingtalk_service_url().rstrip('/')
    url = f"{base_url}/api/users?mpNumber={urllib.parse.quote(clean_id)}"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Human-Agent/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            items = data.get("items", [])
            if items:
                u = items[0]
                return {
                    "employee_id": clean_id,
                    "name": u.get("name"),
                    "dingtalkUserId": u.get("dingtalkUserId"),
                    "mobile": u.get("mobile") or u.get("hrPhoneNumber"),
                    "department": u.get("department"),
                    "email": u.get("email"),
                    "position": u.get("position"),
                    "supervisorName": u.get("supervisorName")
                }
    except Exception as e:
        logger.warning(f"通过 mpNumber 查询钉钉用户异常: {e}")
        
    # 备用方案：通过 search 参数检索
    try:
        url_search = f"{base_url}/api/users?search={urllib.parse.quote(clean_id)}"
        req = urllib.request.Request(url_search, headers={"User-Agent": "Human-Agent/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            items = data.get("items", [])
            if items:
                u = items[0]
                return {
                    "employee_id": clean_id,
                    "name": u.get("name"),
                    "dingtalkUserId": u.get("dingtalkUserId"),
                    "mobile": u.get("mobile") or u.get("hrPhoneNumber"),
                    "department": u.get("department"),
                    "email": u.get("email"),
                    "position": u.get("position"),
                    "supervisorName": u.get("supervisorName")
                }
    except Exception as e:
        logger.error(f"检索钉钉用户失败 ({clean_id}): {e}")
        
    return None

def send_dingtalk_work_notification(employee_id: str, message: str, title: str = "【甲丁智能体】工作提醒"):
    """
    利用员工工号向其钉钉发送工作消息通知
    """
    user_info = get_dingtalk_user_by_employee_id(employee_id)
    if not user_info or not user_info.get("dingtalkUserId"):
        return {
            "success": False,
            "employee_id": employee_id,
            "error": f"未在钉钉中台检索到工号 {employee_id} 对应的钉钉账号(dingtalkUserId)"
        }
        
    base_url = get_dingtalk_service_url().rstrip('/')
    userid = user_info["dingtalkUserId"]
    
    # 1. 尝试 POST /api/system-config/test-dingtalk
    post_url = f"{base_url}/api/system-config/test-dingtalk"
    payload = {
        "userId": userid,
        "msg": message,
        "title": title
    }
    
    post_success = False
    post_res = None
    try:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(post_url, data=body, headers={"Content-Type": "application/json; charset=utf-8"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            post_res = json.loads(resp.read().decode("utf-8"))
            if post_res.get("errcode") == 0 or post_res.get("success"):
                post_success = True
    except Exception as e:
        logger.warning(f"POST test-dingtalk 异常: {e}")
        
    # 2. 同时调用 GET /api/workflow/test-notify?userid=... 触发钉钉工作流通知
    notify_url = f"{base_url}/api/workflow/test-notify?userid={urllib.parse.quote(userid)}"
    get_success = False
    get_res = None
    try:
        req_get = urllib.request.Request(notify_url)
        with urllib.request.urlopen(req_get, timeout=10) as resp:
            get_res = json.loads(resp.read().decode("utf-8"))
            if get_res.get("success") or get_res.get("response", {}).get("errcode") == 0:
                get_success = True
    except Exception as e:
        logger.warning(f"GET test-notify 异常: {e}")
        
    overall_success = post_success or get_success
    
    return {
        "success": overall_success,
        "employee_id": employee_id,
        "name": user_info.get("name"),
        "dingtalkUserId": userid,
        "department": user_info.get("department"),
        "mobile": user_info.get("mobile"),
        "message": message,
        "detail": {
            "post_result": post_res,
            "workflow_result": get_res
        }
    }

def batch_send_by_employee_ids(employee_ids: list, message: str, title: str = "【甲丁智能体】工作提醒"):
    """
    批量按工号列表向员工推送钉钉工作消息
    """
    results = []
    success_count = 0
    fail_count = 0
    
    for eid in employee_ids:
        r = send_dingtalk_work_notification(eid, message, title)
        if r["success"]:
            success_count += 1
        else:
            fail_count += 1
        results.append(r)
        
    return {
        "total": len(employee_ids),
        "success_count": success_count,
        "fail_count": fail_count,
        "results": results
    }
