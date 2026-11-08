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

aphr_scheduler = BackgroundScheduler(timezone="Asia/Shanghai")

DEFAULT_APHR_URL = os.getenv("APHR_BASE_URL", "http://10.11.100.151:8092")
if "aphr.internal" in DEFAULT_APHR_URL:
    DEFAULT_APHR_URL = "http://10.11.100.151:8092"

DEFAULT_CONFIGS = {
    "APHR_BASE_URL": DEFAULT_APHR_URL,
    "APHR_USERNAME": "admin",
    "APHR_PASSWORD": "admin123",
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
    
    # 获取 APHR 员工总数
    emp_url = f"{clean_url}/api/v1/employees?limit=1"
    req_emp = urllib.request.Request(emp_url, headers=headers)
    total_employees = 0
    with urllib.request.urlopen(req_emp, timeout=10) as resp:
        body = json.loads(resp.read().decode("utf-8"))
        total_employees = body.get("total", 0)

    return {
        "success": True,
        "latency_ms": latency_ms,
        "total_employees": total_employees
    }

def fetch_all_aphr_employees(base_url, token):
    """从 APHR 分批次抓取全量员工列表"""
    clean_url = base_url.rstrip('/')
    headers = {"Authorization": f"Bearer {token}"}
    all_employees = []
    
    skip = 0
    limit = 1000
    while True:
        url = f"{clean_url}/api/v1/employees?skip={skip}&limit={limit}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
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
    核心同步逻辑：从 APHR 拉取员工基础数据并安全同步进本地 BaseEmployee
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
        
        token = get_aphr_token(base_url, username, password)
        raw_employees = fetch_all_aphr_employees(base_url, token)
        
        total_fetched = len(raw_employees)
        inserted_count = 0
        updated_count = 0
        skipped_count = 0
        
        # 预先全量加载本地现有员工映射，极速完成内存比对
        existing_emp_map = {e.employee_id: e for e in db.query(BaseEmployee).all()}
        
        for item in raw_employees:
            eid = str(item.get("employee_id") or "").strip()
            name = str(item.get("name") or "").strip()
            if not eid or not name:
                skipped_count += 1
                continue
                
            position = str(item.get("position") or "")
            aphr_workshop = str(item.get("workshop") or "").strip()
            aphr_skills = item.get("skills")
            
            existing = existing_emp_map.get(eid)
            if existing:
                existing.name = name
                # 车间：优先保留已有车间，若为空则采用 APHR 车间
                if not existing.workshop_code and aphr_workshop:
                    existing.workshop_code = aphr_workshop
                # 状态默认有效
                if not existing.health_cert_status:
                    existing.health_cert_status = "有效"
                if not existing.work_cert_status:
                    existing.work_cert_status = "有效"
                # 技能：保留本地既有技能矩阵，若本地无技能且 APHR 有则同步
                if not existing.skills or len(existing.skills) == 0:
                    if aphr_skills and isinstance(aphr_skills, list) and len(aphr_skills) > 0:
                        existing.skills = aphr_skills
                    elif "作业" in position:
                        existing.skills = ["PI中包装"]
                updated_count += 1
            else:
                skills = []
                if aphr_skills and isinstance(aphr_skills, list) and len(aphr_skills) > 0:
                    skills = aphr_skills
                elif "作业" in position:
                    skills = ["PI中包装"]
                    
                new_emp = BaseEmployee(
                    employee_id=eid,
                    name=name,
                    workshop_code=aphr_workshop or None,
                    health_cert_status="有效",
                    work_cert_status="有效",
                    skills=skills
                )
                db.add(new_emp)
                existing_emp_map[eid] = new_emp
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
        
        set_config_dict(db, {
            "APHR_LAST_SYNC_TIME": report["sync_time"],
            "APHR_LAST_SYNC_STATUS": "SUCCESS",
            "APHR_LAST_SYNC_REPORT": json.dumps(report, ensure_ascii=False)
        })
        
        logger.info(f"APHR全量员工同步完成: {report}")
        return report
        
    except Exception as e:
        db.rollback()
        duration = round(time.time() - t0, 2)
        err_msg = str(e)
        logger.error(f"APHR全量员工同步失败: {err_msg}")
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
