import os
import time
import json
import logging
import urllib.request
import urllib.parse
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

from app.core.database import SessionLocal
from app.models.master_data import BaseEmployee
from app.models.system import SysConfig

logger = logging.getLogger(__name__)

# 全局后台调度器实例
aphr_scheduler = BackgroundScheduler(timezone="Asia/Shanghai")

DEFAULT_APHR_URL = os.getenv("APHR_BASE_URL", "http://10.11.100.151:8092")
if "aphr.internal" in DEFAULT_APHR_URL:
    DEFAULT_APHR_URL = "http://10.11.100.151:8092"

DEFAULT_CONFIGS = {
    "APHR_BASE_URL": DEFAULT_APHR_URL,
    "APHR_USERNAME": "admin",
    "APHR_PASSWORD": "admin123",
    "APHR_DEPT_ID": "38",  # 生产部
    "APHR_DEFAULT_WORKSHOP": "中包车间",
    "APHR_SYNC_ENABLED": "true",
    "APHR_SYNC_INTERVAL_MIN": "60",
    "APHR_LAST_SYNC_TIME": "",
    "APHR_LAST_SYNC_STATUS": "PENDING",
    "APHR_LAST_SYNC_REPORT": "{}"
}

def get_config_dict(db):
    """从 SysConfig 读取 APHR 相关全部配置"""
    configs = db.query(SysConfig).filter(SysConfig.config_key.like("APHR_%")).all()
    res = DEFAULT_CONFIGS.copy()
    for c in configs:
        if c.config_value is not None:
            res[c.config_key] = c.config_value
    return res

def set_config_dict(db, new_configs):
    """保存 APHR 相关配置到 SysConfig"""
    for k, v in new_configs.items():
        if not k.startswith("APHR_"):
            continue
        c = db.query(SysConfig).filter(SysConfig.config_key == k).first()
        if c:
            c.config_value = str(v)
        else:
            c = SysConfig(config_key=k, config_value=str(v), description=f"APHR对接配置 - {k}")
            db.add(c)
    db.commit()

def get_aphr_token(base_url, username, password):
    """登录 APHR 获取 JWT Access Token"""
    clean_url = base_url.rstrip('/')
    login_url = f"{clean_url}/api/v1/login/access-token"
    data = urllib.parse.urlencode({"username": username, "password": password}).encode("utf-8")
    req = urllib.request.Request(
        login_url,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body.get("access_token")
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        raise Exception(f"APHR登录鉴权失败 (HTTP {e.code}): {err_msg}")
    except Exception as e:
        raise Exception(f"无法连接到 APHR 服务 ({login_url}): {str(e)}")

def test_aphr_connection(base_url, username, password):
    """测试 APHR 连通性并获取基本统计"""
    t0 = time.time()
    token = get_aphr_token(base_url, username, password)
    latency_ms = int((time.time() - t0) * 1000)
    
    clean_url = base_url.rstrip('/')
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. 获取员工总数
    emp_url = f"{clean_url}/api/v1/employees?limit=1"
    req_emp = urllib.request.Request(emp_url, headers=headers)
    total_employees = 0
    with urllib.request.urlopen(req_emp, timeout=10) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        total_employees = body.get("total", 0)
        
    # 2. 获取部门列表树
    dept_url = f"{clean_url}/api/v1/departments/tree"
    req_dept = urllib.request.Request(dept_url, headers=headers)
    departments = []
    dept_38_count = 0
    try:
        with urllib.request.urlopen(req_dept, timeout=10) as resp:
            departments = json.loads(resp.read().decode("utf-8"))
    except:
        pass
        
    # 3. 获取部门 38 (生产部) 员工数
    try:
        dept38_url = f"{clean_url}/api/v1/employees?department_id=38&limit=1"
        req_d38 = urllib.request.Request(dept38_url, headers=headers)
        with urllib.request.urlopen(req_d38, timeout=10) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            dept_38_count = body.get("total", 0)
    except:
        dept_38_count = 0

    return {
        "success": True,
        "latency_ms": latency_ms,
        "total_employees": total_employees,
        "dept_38_employees": dept_38_count,
        "departments": departments
    }

def fetch_all_aphr_employees(base_url, token, department_id=None):
    """从 APHR 分页抓取员工列表"""
    clean_url = base_url.rstrip('/')
    headers = {"Authorization": f"Bearer {token}"}
    all_employees = []
    
    skip = 0
    limit = 100
    while True:
        url = f"{clean_url}/api/v1/employees?skip={skip}&limit={limit}"
        if department_id and str(department_id).strip() and str(department_id).lower() != 'all':
            url += f"&department_id={department_id}"
            
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            items = data.get("items", [])
            total = data.get("total", len(items))
            all_employees.extend(items)
            if len(all_employees) >= total or not items:
                break
            skip += limit
            
    return all_employees

def sync_employees_from_aphr(custom_config=None):
    """
    核心同步逻辑：从 APHR 拉取员工基础数据并安全合并进本地 BaseEmployee
    """
    db = SessionLocal()
    t0 = time.time()
    try:
        config = get_config_dict(db)
        if custom_config:
            config.update(custom_config)
            
        base_url = config.get("APHR_BASE_URL", DEFAULT_APHR_URL)
        username = config.get("APHR_USERNAME", "admin")
        password = config.get("APHR_PASSWORD", "admin123")
        dept_id = config.get("APHR_DEPT_ID", "38")
        default_workshop = config.get("APHR_DEFAULT_WORKSHOP", "中包车间")
        
        token = get_aphr_token(base_url, username, password)
        raw_employees = fetch_all_aphr_employees(base_url, token, dept_id)
        
        total_fetched = len(raw_employees)
        inserted_count = 0
        updated_count = 0
        skipped_count = 0
        
        for item in raw_employees:
            eid = str(item.get("employee_id") or "").strip()
            name = str(item.get("name") or "").strip()
            if not eid or not name:
                skipped_count += 1
                continue
                
            position = str(item.get("position") or "")
            dept_name = ""
            if isinstance(item.get("department"), dict):
                dept_name = item["department"].get("name", "")
                
            existing = db.query(BaseEmployee).filter(BaseEmployee.employee_id == eid).first()
            if existing:
                # 保留既有车间和技能，更新姓名和未指定字段
                existing.name = name
                if not existing.workshop_code:
                    existing.workshop_code = default_workshop
                if not existing.health_cert_status:
                    existing.health_cert_status = "有效"
                if not existing.work_cert_status:
                    existing.work_cert_status = "有效"
                if not existing.skills or len(existing.skills) == 0:
                    aphr_skills = item.get("skills")
                    if aphr_skills and isinstance(aphr_skills, list) and len(aphr_skills) > 0:
                        existing.skills = aphr_skills
                    elif "作业" in position or default_workshop == "中包车间":
                        existing.skills = ["PI中包装"]
                updated_count += 1
            else:
                # 新增员工
                skills = []
                aphr_skills = item.get("skills")
                if aphr_skills and isinstance(aphr_skills, list) and len(aphr_skills) > 0:
                    skills = aphr_skills
                elif "作业" in position or default_workshop == "中包车间":
                    skills = ["PI中包装"]
                    
                new_emp = BaseEmployee(
                    employee_id=eid,
                    name=name,
                    workshop_code=default_workshop,
                    health_cert_status="有效",
                    work_cert_status="有效",
                    skills=skills
                )
                db.add(new_emp)
                inserted_count += 1
                
        db.commit()
        
        duration = round(time.time() - t0, 2)
        report = {
            "total_fetched": total_fetched,
            "inserted": inserted_count,
            "updated": updated_count,
            "skipped": skipped_count,
            "duration_sec": duration,
            "sync_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "SUCCESS"
        }
        
        # 记录同步状态
        set_config_dict(db, {
            "APHR_LAST_SYNC_TIME": report["sync_time"],
            "APHR_LAST_SYNC_STATUS": "SUCCESS",
            "APHR_LAST_SYNC_REPORT": json.dumps(report, ensure_ascii=False)
        })
        
        logger.info(f"APHR员工同步完成: {report}")
        return report
        
    except Exception as e:
        db.rollback()
        duration = round(time.time() - t0, 2)
        err_msg = str(e)
        logger.error(f"APHR员工同步失败: {err_msg}")
        report = {
            "error": err_msg,
            "duration_sec": duration,
            "sync_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "FAILED"
        }
        try:
            set_config_dict(db, {
                "APHR_LAST_SYNC_TIME": report["sync_time"],
                "APHR_LAST_SYNC_STATUS": "FAILED",
                "APHR_LAST_SYNC_REPORT": json.dumps(report, ensure_ascii=False)
            })
        except:
            pass
        raise e
    finally:
        db.close()

def scheduled_sync_job():
    """定时调度任务执行体"""
    logger.info("触发 APHR 定时自动同步任务...")
    try:
        sync_employees_from_aphr()
    except Exception as e:
        logger.error(f"定时同步任务发生异常: {e}")

def init_aphr_scheduler():
    """初始化并启动后台定时调度器"""
    if aphr_scheduler.running:
        return
        
    db = SessionLocal()
    try:
        cfg = get_config_dict(db)
        enabled = cfg.get("APHR_SYNC_ENABLED", "true").lower() == "true"
        interval_min = int(cfg.get("APHR_SYNC_INTERVAL_MIN", "60"))
        
        aphr_scheduler.add_job(
            scheduled_sync_job,
            trigger="interval",
            minutes=max(1, interval_min),
            id="aphr_sync_job",
            replace_existing=True
        )
        
        aphr_scheduler.start()
        if not enabled:
            aphr_scheduler.pause_job("aphr_sync_job")
            logger.info("APHR 定时同步调度器已就绪 (状态: 已暂停)")
        else:
            logger.info(f"APHR 定时同步调度器已启动 (周期: 每 {interval_min} 分钟)")
    except Exception as e:
        logger.error(f"初始化 APHR 调度器异常: {e}")
    finally:
        db.close()

def update_scheduler_settings(enabled: bool, interval_minutes: int):
    """动态更新定时同步参数"""
    if not aphr_scheduler.running:
        init_aphr_scheduler()
        
    if aphr_scheduler.get_job("aphr_sync_job"):
        aphr_scheduler.reschedule_job(
            "aphr_sync_job",
            trigger="interval",
            minutes=max(1, interval_minutes)
        )
        if enabled:
            aphr_scheduler.resume_job("aphr_sync_job")
            logger.info(f"APHR 调度任务已启用: 每 {interval_minutes} 分钟")
        else:
            aphr_scheduler.pause_job("aphr_sync_job")
            logger.info("APHR 调度任务已暂停")
