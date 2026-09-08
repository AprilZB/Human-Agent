from app.core.database import engine
from sqlalchemy import text
import datetime

today = datetime.datetime.now()
start_of_week = today - datetime.timedelta(days=today.weekday())

with engine.begin() as conn:
    conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    
    # 1. Base Process
    conn.execute(text("INSERT IGNORE INTO base_process (process_code, process_name, required_skills, standard_time_sec) VALUES ('P-STAMP-01', '冲压工序A', '[\"STAMPING\"]', 300)"))
    conn.execute(text("INSERT IGNORE INTO base_process (process_code, process_name, required_skills, standard_time_sec) VALUES ('P-WELD-01', '焊接工序B', '[\"WELDING\"]', 400)"))
    
    # 2. Production Orders
    conn.execute(text(f"INSERT IGNORE INTO biz_production_order (order_code, material_code, target_quantity, status) VALUES ('PO-{today.strftime('%Y%m%d')}-001', 'MAT-001', 100, 'RELEASED')"))
    for i in range(3):
        conn.execute(text(f"INSERT IGNORE INTO biz_production_order (order_code, material_code, target_quantity, status) VALUES ('PO-OLD-00{i}', 'MAT-OLD', 50, 'RELEASED')"))
        
    # 3. Work Orders for today (PENDING)
    for i in range(1, 4):
        woc = f"WO-{today.strftime('%Y%m%d')}-00{i}"
        proc = "P-STAMP-01" if i % 2 == 0 else "P-WELD-01"
        conn.execute(text(f"INSERT IGNORE INTO biz_work_order (work_order_code, order_code, process_code, team_code, required_count, status, created_at) VALUES ('{woc}', 'PO-{today.strftime('%Y%m%d')}-001', '{proc}', 'TEAM-A', 2, 'PENDING', '{today.strftime('%Y-%m-%d %H:%M:%S')}')"))
        
    # 4. Work Orders for earlier this week (DISPATCHED)
    for i in range(1, 4):
        woc = f"WO-DISP-{today.strftime('%Y%m%d')}-00{i}"
        dt = (start_of_week + datetime.timedelta(days=i-1)).strftime('%Y-%m-%d %H:%M:%S')
        conn.execute(text(f"INSERT IGNORE INTO biz_work_order (work_order_code, order_code, process_code, team_code, required_count, status, created_at) VALUES ('{woc}', 'PO-OLD-00{i-1}', 'P-STAMP-01', 'TEAM-A', 1, 'DISPATCHED', '{dt}')"))
        emp = "EMP001" if i % 2 == 0 else "EMP002"
        conn.execute(text(f"INSERT IGNORE INTO task_personnel_assignment (work_order_code, employee_id, recommend_reason, status, created_at) VALUES ('{woc}', '{emp}', 'Manual', 'CONFIRMED', '{dt}')"))
        
    conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))

print("Raw SQL seed data injected successfully!")
