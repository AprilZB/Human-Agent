with open('backend/app/api/data.py', 'r', encoding='utf-8') as f:
    code = f.read()

mapping_dict = '''
HEADER_MAPPING = {
    "生产订单号": "order_code",
    "订单编号": "order_code",
    "物料编码": "material_code",
    "目标数量": "target_quantity",
    "计划开始时间": "plan_start_time",
    "计划开始": "plan_start_time",
    "计划结束时间": "plan_end_time",
    "计划结束": "plan_end_time",
    "状态": "status",
    "工艺路线": "routing_code",
    
    # 员工出勤
    "考勤日期": "attendance_date",
    "工作日期": "attendance_date",
    "工号": "employee_id",
    "排班": "shift_code",
    "班次": "shift_code",
    "签到时间": "actual_punch_in",
    "签退时间": "actual_punch_out",
    "实际工时": "actual_work_hours",
    "出勤类型": "attendance_type",
    
    # 物料
    "物料描述": "material_desc",
    "基本单位": "base_uom",
    "物料组": "material_group_code",
    
    # 确认单
    "确认单号": "confirmation_no",
    "批次号": "batch_no",
    "工厂": "plant",
    "合格数量": "yield_quantity",
    "报废数量": "scrap_quantity",
    "执行日期": "exec_datetime",
    
    # 员工基本信息
    "姓名": "name",
    "车间": "workshop_code",
    "健康证状态": "health_cert_status",
    "上岗证状态": "work_cert_status"
}
'''

import_old = '''    try:
        df = pd.read_excel(file)
        # Handle nan -> None
        df = df.where(pd.notnull(df), None)
        records = df.to_dict(orient='records')'''

import_new = '''    try:
        df = pd.read_excel(file)
        # Rename columns based on mapping if they match
        df.rename(columns=HEADER_MAPPING, inplace=True)
        # Also, lowercase the headers just in case they are english but capitalized
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        # Keep only columns that exist in the model
        model_cols = [c.name for c in model.__table__.columns]
        valid_cols = [c for c in df.columns if c in model_cols]
        if not valid_cols:
            return jsonify({"error": "No valid columns found in the uploaded file"}), 400
            
        df = df[valid_cols]
        
        # Handle nan -> None
        df = df.where(pd.notnull(df), None)
        records = df.to_dict(orient='records')'''

if 'HEADER_MAPPING' not in code:
    code = code.replace("data_bp = Blueprint('data', __name__)", "data_bp = Blueprint('data', __name__)\n" + mapping_dict)
    code = code.replace(import_old, import_new)
    
    with open('backend/app/api/data.py', 'w', encoding='utf-8') as f:
        f.write(code)
