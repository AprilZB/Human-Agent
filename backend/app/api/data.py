from flask import Blueprint, jsonify, request
from app.core.database import SessionLocal
import app.models.master_data as md
import app.models.production as prod
from sqlalchemy import or_

data_bp = Blueprint('data', __name__)

TAB_HEADER_OVERRIDE = {
    "routings": {
        "路线编码": "routing_code",
        "SAP对照码": "sap_routing_code",
        "sap对照码": "sap_routing_code",
        "路线名称": "routing_name",
        "关联物料": "material_code",
        "版本": "version",
    },
    "confirmations": {
        "生产单号": "order_code",
        "生产批次号": "batch_no",
        "品号": "material_code",
        "工作中心": "work_center_code",
        "合格品数": "yield_quantity",
        "报废品数": "scrap_quantity",
        "不合格数": "scrap_quantity",
        "工序ID": "process_code",
        "工序id": "process_code",
        "工序名称": "process_name",
        "更新人编号": "employee_id",
        "创建者": "employee_id",
        "更新人名称": "employee_name",
        "建立者用户.1": "employee_name",
        "报工工时": "work_hours",
        "lbl_fb_id": "confirmation_no",
        "报工日期": "exec_datetime",
        "工厂": "plant",
        "工厂ID": "plant",
        "工厂id": "plant",
    },
    "material-groups": {
        "本地物料组编码": "group_code",
        "SAP对照码": "sap_group_code",
        "sap对照码": "sap_group_code",
        "物料组名称": "group_name",
    }
}

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
    "上岗证状态": "work_cert_status",
    "健康证状态/有效期": "health_cert_status",
    "上岗证状态/有效期": "work_cert_status",
    "技能矩阵": "skills",

    # BOM与工艺
    "BOM编码": "bom_code",
    "父件编码": "product_code",
    "子件编码": "component_code",
    "用量": "quantity",
    "本地不良代码": "defect_code",
    "SAP不良代码": "sap_defect_code",
    "不良名称": "defect_name",
    "描述": "description",
    "工序代码": "process_code",
    "工序名称": "process_name",
    "标准工时(秒)": "standard_time_sec",
    "所需技能": "required_skills",
    "排班班次": "shift_code",
    "是否节假日": "is_holiday",
    "实际签到": "actual_punch_in",
    "实际签退": "actual_punch_out",
    "考勤状态": "attendance_status",
    "核算加班(H)": "calculated_overtime",
    "工作中心": "work_center_code",
    "生产批次号": "batch_no",
    "生产单号": "order_code",
    "品号": "material_code",
    "合格品数": "yield_quantity",
    "不合格数": "scrap_quantity",
    "报废品数": "scrap_quantity",
    "本地物料组编码": "group_code",
    "SAP对照码": "sap_group_code",
    "物料组名称": "group_name",
    "车间编码": "workshop_code",
    "车间名称": "workshop_name",
    "SAP工作中心对照": "sap_work_center_code",
    "路线编码": "routing_code",
    "路线名称": "routing_name",
    "关联物料": "material_code",
    "版本": "version"
}


def paginate(query):
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    return {"total": total, "page": page, "size": size, "records": [item.__dict__ for item in items]}

import datetime
from decimal import Decimal

def clean_dict(d):
    res = {}
    for k, v in d.items():
        if not k.startswith('_'):
            if isinstance(v, (datetime.datetime, datetime.date)):
                res[k] = v.isoformat()
            elif isinstance(v, Decimal):
                res[k] = float(v)
            else:
                res[k] = v
    return res

@data_bp.route("/materials", methods=["GET"])
def get_materials():
    db = SessionLocal()
    try:
        q = db.query(md.BaseMaterial)
        keyword = request.args.get('keyword', '')
        if keyword:
            q = q.filter(or_(md.BaseMaterial.material_code.like(f"%{keyword}%"), md.BaseMaterial.material_desc.like(f"%{keyword}%")))
        res = paginate(q)
        res['records'] = [clean_dict(r) for r in res['records']]
        return jsonify(res)
    finally:
        db.close()

@data_bp.route("/employees", methods=["GET"])
def get_employees():
    db = SessionLocal()
    try:
        q = db.query(md.BaseEmployee)
        keyword = request.args.get('keyword', '')
        if keyword:
            q = q.filter(or_(md.BaseEmployee.employee_id.like(f"%{keyword}%"), md.BaseEmployee.name.like(f"%{keyword}%")))
        res = paginate(q)
        res['records'] = [clean_dict(r) for r in res['records']]
        return jsonify(res)
    finally:
        db.close()

@data_bp.route("/production-orders", methods=["GET"])
def get_production_orders():
    db = SessionLocal()
    try:
        q = db.query(prod.BizProductionOrder)
        keyword = request.args.get('keyword', '')
        if keyword:
            q = q.filter(or_(prod.BizProductionOrder.order_code.like(f"%{keyword}%"), prod.BizProductionOrder.material_code.like(f"%{keyword}%")))
        res = paginate(q)
        res['records'] = [clean_dict(r) for r in res['records']]
        return jsonify(res)
    finally:
        db.close()

@data_bp.route("/workshops", methods=["GET"])
def get_workshops():
    db = SessionLocal()
    try:
        q = db.query(md.BaseWorkshop)
        res = paginate(q)
        res['records'] = [clean_dict(r) for r in res['records']]
        return jsonify(res)
    finally:
        db.close()

@data_bp.route("/defect-reasons", methods=["GET"])
def get_defect_reasons():
    db = SessionLocal()
    try:
        q = db.query(md.BaseDefectReason)
        res = paginate(q)
        res['records'] = [clean_dict(r) for r in res['records']]
        return jsonify(res)
    finally:
        db.close()

@data_bp.route("/material-groups", methods=["GET"])
def get_material_groups():
    db = SessionLocal()
    try:
        q = db.query(md.BaseMaterialGroup)
        keyword = request.args.get('keyword', '')
        if keyword:
            q = q.filter(or_(md.BaseMaterialGroup.group_code.like(f"%{keyword}%"), md.BaseMaterialGroup.group_name.like(f"%{keyword}%")))
        res = paginate(q)
        res['records'] = [clean_dict(r) for r in res['records']]
        return jsonify(res)
    finally:
        db.close()

@data_bp.route("/routings", methods=["GET"])
def get_routings():
    db = SessionLocal()
    try:
        q = db.query(md.BaseRouting)
        keyword = request.args.get('keyword', '')
        if keyword:
            q = q.filter(or_(md.BaseRouting.routing_code.like(f"%{keyword}%"), md.BaseRouting.routing_name.like(f"%{keyword}%"), md.BaseRouting.material_code.like(f"%{keyword}%")))
        res = paginate(q)
        res['records'] = [clean_dict(r) for r in res['records']]
        return jsonify(res)
    finally:
        db.close()

@data_bp.route("/processes", methods=["GET"])
def get_processes():
    db = SessionLocal()
    try:
        q = db.query(prod.BaseProcess)
        res = paginate(q)
        res['records'] = [clean_dict(r) for r in res['records']]
        return jsonify(res)
    finally:
        db.close()

@data_bp.route("/boms", methods=["GET"])
def get_boms():
    db = SessionLocal()
    try:
        q = db.query(md.BaseBom)
        res = paginate(q)
        res['records'] = [clean_dict(r) for r in res['records']]
        return jsonify(res)
    finally:
        db.close()

from flask import send_file
import pandas as pd
import io

# Generic Import/Export Map
TAB_MODEL_MAP = {
    "materials": md.BaseMaterial,
    "production-orders": prod.BizProductionOrder,
    "employees": md.BaseEmployee,
    "workshops": md.BaseWorkshop,
    "defect-reasons": md.BaseDefectReason,
    "material-groups": md.BaseMaterialGroup,
    "routings": md.BaseRouting,
    "processes": prod.BaseProcess,
    "boms": md.BaseBom,
    "confirmations": prod.BizProductionConfirmation,
    "attendances": prod.BizEmployeeAttendance
}

TEMPLATE_CONFIG = {
    "material-groups": {
        "filename": "物料组导入模板.xlsx",
        "sample": [
            {"本地物料组编码": "C.DF.02A", "SAP对照码": "D.0B.0QE-1", "物料组名称": "PIONEER球囊扩张导管（国内）PI11515"},
            {"本地物料组编码": "N.0.0499", "SAP对照码": "D.0B.0QE-1", "物料组名称": "FB2封口标签"}
        ]
    },
    "routings": {
        "filename": "工艺路线导入模板.xlsx",
        "sample": [
            {"路线编码": "OMP0010", "SAP对照码": "D.0B.13E-1", "路线名称": "中包装", "关联物料": "C.DF.26A", "版本": "/"},
            {"路线编码": "OMP0006", "SAP对照码": "C.DF.26A", "路线名称": "灭菌装箱", "关联物料": "/", "版本": "/"}
        ]
    },
    "confirmations": {
        "filename": "确认报工导入模板.xlsx",
        "sample": [{
            "工厂": "4110", "工作中心": "BT003", "生产单号": "13551286", "品号": "D.0B.0RE-1",
            "工序ID": "OMP0010", "工序名称": "中包装", "合格品数": 152, "报废品数": 0,
            "报工工时": 3, "生产批次号": "260", "更新人编号": "hulx", "更新人名称": "胡兰心",
            "lbl_fb_id": "6AB54AEB362CF20100003283", "报工日期": "2026-09-24"
        }]
    },
    "boms": {
        "filename": "BOM档案导入模板.xlsx",
        "sample": [
            {"BOM编码": "10", "父件编码": "D.0B.13E-1", "子件编码": "C.DF.26A", "用量": 1.0, "替代物料同行号": "A1"},
            {"BOM编码": "10", "父件编码": "D.0B.13E-1", "子件编码": "N.0.0499", "用量": 1.0, "替代物料同行号": "A1"}
        ]
    },
    "materials": {
        "filename": "物料档案导入模板.xlsx",
        "sample": [{
            "物料编码": "C.DF.26A", "物料描述": "PIONEER球囊扩张导管（国内）PI13020",
            "物料组": "D.0B.13E-1", "基本单位": "PCS", "特定工厂状态": "01",
            "有效起始期": "2026-01-01", "安全库存": 100, "库存默认地点": "W01"
        }]
    },
    "production-orders": {
        "filename": "生产订单导入模板.xlsx",
        "sample": [{
            "订单编号": "13551286", "物料编码": "D.0B.0RE-1", "目标数量": 500,
            "计划开始时间": "2026-09-24 08:00:00", "计划结束时间": "2026-09-24 18:00:00",
            "状态": "RELEASED", "工艺路线": "OMP0010"
        }]
    },
    "employees": {
        "filename": "员工档案导入模板.xlsx",
        "sample": [{
            "工号": "hulx", "姓名": "胡兰心", "车间": "BT003",
            "健康证状态/有效期": "有效", "上岗证状态/有效期": "有效", "技能矩阵": "中包装"
        }]
    },
    "workshops": {
        "filename": "车间档案导入模板.xlsx",
        "sample": [{
            "车间编码": "BT003", "车间名称": "中包装车间",
            "SAP工作中心对照": "BT003", "负责人ID": "hulx"
        }]
    },
    "defect-reasons": {
        "filename": "不良原因导入模板.xlsx",
        "sample": [{
            "本地不良代码": "DEF-01", "SAP不良代码": "SAP-01",
            "不良名称": "封口破损", "描述": "外包装袋封口处漏气"
        }]
    },
    "processes": {
        "filename": "工序档案导入模板.xlsx",
        "sample": [{
            "工序代码": "10", "工序名称": "中包装", "所需技能": "PI中包装",
            "标准工时(秒)": 107, "绑定的BOM编码": "10"
        }]
    },
    "attendances": {
        "filename": "考勤记录导入模板.xlsx",
        "sample": [{
            "工作日期": "2026-09-24", "工号": "hulx", "排班班次": "早班",
            "是否节假日": "否", "实际签到": "2026-09-24 08:00:00", "实际签退": "2026-09-24 17:00:00",
            "实际工时": 8.0, "出勤类型": "正常", "考勤状态": "正常", "核算加班(H)": 0.0
        }]
    }
}

REVERSE_HEADER_MAPPING = {
    "materials": {
        "material_code": "物料编码", "material_desc": "物料描述", "material_group_code": "物料组",
        "base_uom": "基本单位", "plant_status": "特定工厂状态", "valid_from": "有效起始期",
        "safety_stock": "安全库存", "default_storage_loc": "库存默认地点"
    },
    "production-orders": {
        "order_code": "订单编号", "material_code": "物料编码", "target_quantity": "目标数量",
        "plan_start_time": "计划开始时间", "plan_end_time": "计划结束时间", "status": "状态",
        "routing_code": "工艺路线"
    },
    "confirmations": {
        "order_code": "生产单号", "material_code": "品号", "work_center_code": "工作中心",
        "batch_no": "生产批次号", "yield_quantity": "合格品数", "scrap_quantity": "报废品数",
        "confirmation_no": "lbl_fb_id", "plant": "工厂", "exec_datetime": "报工日期",
        "process_code": "工序ID", "process_name": "工序名称", "employee_id": "更新人编号",
        "employee_name": "更新人名称", "work_hours": "报工工时"
    },
    "employees": {
        "employee_id": "工号", "name": "姓名", "workshop_code": "车间",
        "health_cert_status": "健康证状态", "work_cert_status": "上岗证状态", "skills": "技能矩阵"
    },
    "workshops": {
        "workshop_code": "车间编码", "workshop_name": "车间名称", "sap_work_center_code": "SAP工作中心对照",
        "manager_id": "负责人ID"
    },
    "defect-reasons": {
        "defect_code": "本地不良代码", "sap_defect_code": "SAP不良代码", "defect_name": "不良名称",
        "description": "描述"
    },
    "material-groups": {
        "group_code": "本地物料组编码", "sap_group_code": "SAP对照码", "group_name": "物料组名称"
    },
    "routings": {
        "routing_code": "路线编码", "sap_routing_code": "SAP对照码", "routing_name": "路线名称",
        "material_code": "关联物料", "version": "版本"
    },
    "processes": {
        "process_code": "工序代码", "process_name": "工序名称", "required_skills": "所需技能",
        "standard_time_sec": "标准工时(秒)", "bound_bom_code": "绑定的BOM编码"
    },
    "boms": {
        "bom_code": "BOM编码", "product_code": "父件编码", "component_code": "子件编码",
        "quantity": "用量", "alt_group": "替代物料同行号"
    },
    "attendances": {
        "attendance_date": "工作日期", "employee_id": "工号", "shift_code": "排班班次",
        "is_holiday": "是否节假日", "actual_punch_in": "实际签到", "actual_punch_out": "实际签退",
        "actual_work_hours": "实际工时", "attendance_type": "出勤类型", "attendance_status": "考勤状态",
        "calculated_overtime": "核算加班(H)"
    }
}

@data_bp.route("/confirmations", methods=["GET"])
def get_confirmations():
    db = SessionLocal()
    try:
        q = db.query(prod.BizProductionConfirmation)
        keyword = request.args.get('keyword', '')
        if keyword:
            q = q.filter(or_(
                prod.BizProductionConfirmation.order_code.like(f"%{keyword}%"),
                prod.BizProductionConfirmation.material_code.like(f"%{keyword}%"),
                prod.BizProductionConfirmation.confirmation_no.like(f"%{keyword}%"),
                prod.BizProductionConfirmation.employee_name.like(f"%{keyword}%"),
                prod.BizProductionConfirmation.process_name.like(f"%{keyword}%")
            ))
        res = paginate(q)
        res['records'] = [clean_dict(r) for r in res['records']]
        return jsonify(res)
    finally:
        db.close()

@data_bp.route("/<tab_name>/export", methods=["GET"])
def export_data(tab_name):
    if tab_name not in TAB_MODEL_MAP:
        return jsonify({"error": "Invalid tab"}), 400
        
    model = TAB_MODEL_MAP[tab_name]
    is_template = request.args.get('template') == '1'
    
    db = SessionLocal()
    try:
        if is_template:
            if tab_name in TEMPLATE_CONFIG:
                cfg = TEMPLATE_CONFIG[tab_name]
                df = pd.DataFrame(cfg['sample'])
                filename = cfg.get('filename', f"{tab_name}_template.xlsx")
            else:
                cols = [c.name for c in model.__table__.columns if c.name not in ['id', 'created_at']]
                df = pd.DataFrame(columns=cols)
                filename = f"{tab_name}_template.xlsx"
        else:
            items = db.query(model).all()
            data = [clean_dict(item.__dict__) for item in items]
            df = pd.DataFrame(data)
            if tab_name in REVERSE_HEADER_MAPPING:
                df.rename(columns=REVERSE_HEADER_MAPPING[tab_name], inplace=True)
            filename = f"{tab_name}.xlsx"
            
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
            
        out.seek(0)
        return send_file(out, download_name=filename, as_attachment=True)
    finally:
        db.close()

@data_bp.route("/<tab_name>/import", methods=["POST"])
def import_data(tab_name):
    if tab_name not in TAB_MODEL_MAP:
        return jsonify({"error": "Invalid tab"}), 400
        
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    file = request.files['file']
    model = TAB_MODEL_MAP[tab_name]
    
    try:
        import pandas as pd
        import math
        
        df = pd.read_excel(file)
        
        # Apply tab-specific header override first
        if tab_name in TAB_HEADER_OVERRIDE:
            df.rename(columns=TAB_HEADER_OVERRIDE[tab_name], inplace=True)
            
        # Rename columns based on global mapping
        df.rename(columns=HEADER_MAPPING, inplace=True)
        # Lowercase and strip
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        # Deduplicate column names if any alias produced duplicates
        df = df.loc[:, ~df.columns.duplicated(keep='first')]
        
        if 'id' in df.columns:
            df.drop(columns=['id'], inplace=True)
            
        # Keep only columns that exist in the model
        model_cols = [c.name for c in model.__table__.columns]
        valid_cols = [c for c in df.columns if c in model_cols]
        if not valid_cols:
            return jsonify({"error": "No valid columns found in the uploaded file"}), 400
            
        df = df[valid_cols]
        
        # Handle nan -> None
        df = df.where(pd.notnull(df), None)
        
        records = df.to_dict(orient='records')
        
        # Convert Timestamps to string and JSON strings to dict
        for rec in records:
            for k, v in rec.items():
                if isinstance(v, float) and math.isnan(v):
                    rec[k] = None
                elif isinstance(v, pd.Timestamp):
                    rec[k] = v.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(v, (int, float)) and k == 'version':
                    rec[k] = str(v)
                elif isinstance(v, str) and (v.strip().startswith('{') or v.strip().startswith('[')):
                    import json
                    try:
                        rec[k] = json.loads(v)
                    except:
                        pass
                        
        pk_names = model.__table__.primary_key.columns.keys()

        # Deduplication / aggregation
        if tab_name == 'employees':
            emp_dict = {}
            for rec in records:
                eid = rec.get('employee_id')
                if eid not in emp_dict:
                    emp_dict[eid] = rec.copy()
                    skill = emp_dict[eid].get('skills')
                    if skill and isinstance(skill, str):
                        emp_dict[eid]['skills'] = [skill]
                    elif not skill:
                        emp_dict[eid]['skills'] = []
                else:
                    skill = rec.get('skills')
                    if skill and isinstance(skill, str):
                        if isinstance(emp_dict[eid].get('skills'), list):
                            emp_dict[eid]['skills'].append(skill)
            records = list(emp_dict.values())
        elif len(pk_names) == 1 and pk_names[0] == 'id':
            # For tables with auto-increment 'id' (e.g. confirmations, attendances)
            # Deduplicate by business key if present (e.g. confirmation_no), else keep all
            if any(r.get('confirmation_no') for r in records):
                agg_dict = {}
                for rec in records:
                    c_no = rec.get('confirmation_no')
                    if c_no:
                        agg_dict[c_no] = rec
                    else:
                        agg_dict[id(rec)] = rec
                records = list(agg_dict.values())
            # Otherwise keep all records
        else:
            # Generic aggregation for composite or single primary keys
            agg_dict = {}
            for rec in records:
                pval = tuple(rec.get(pk) for pk in pk_names)
                if all(p is not None for p in pval):
                    agg_dict[pval] = rec
            records = list(agg_dict.values())

        db = SessionLocal()
        success = 0
        fail = 0
        errors = []
        try:
            for i, rec in enumerate(records):
                try:
                    with db.begin_nested():
                        existing = None
                        if len(pk_names) == 1 and pk_names[0] == 'id':
                            if rec.get('confirmation_no'):
                                existing = db.query(model).filter_by(confirmation_no=rec.get('confirmation_no')).first()
                            elif rec.get('order_code') and rec.get('batch_no'):
                                existing = db.query(model).filter_by(
                                    order_code=rec.get('order_code'),
                                    batch_no=rec.get('batch_no')
                                ).first()
                        elif all(rec.get(pk) is not None for pk in pk_names):
                            filters = [getattr(model, pk) == rec.get(pk) for pk in pk_names]
                            existing = db.query(model).filter(*filters).first()
                        
                        if existing:
                            for k, v in rec.items():
                                setattr(existing, k, v)
                        else:
                            obj = model(**rec)
                            db.add(obj)
                        db.flush()
                    success += 1
                except Exception as e:
                    fail += 1
                    errors.append(f"Row {i+1} failed: {str(e)}")
            
            db.commit()
            
            # Auto-generate Work Orders for Production Orders to make them show up in dispatch
            if tab_name == 'production-orders':
                import app.models.production as prod
                first_process = db.query(prod.BaseProcess).first()
                if first_process:
                    for rec in records:
                        try:
                            with db.begin_nested():
                                order_code = rec.get('order_code')
                                existing_wo = db.query(prod.BizWorkOrder).filter_by(order_code=order_code).first()
                                if not existing_wo:
                                    wo = prod.BizWorkOrder(
                                        work_order_code=f"WO-{order_code}-01",
                                        order_code=order_code,
                                        process_code=first_process.process_code,
                                        required_count=3,
                                        status='PENDING'
                                    )
                                    db.add(wo)
                                db.flush()
                        except:
                            pass
                    db.commit()
            
            return jsonify({
                "message": "Import finished", 
                "total_read": len(records),
                "success": success,
                "fail": fail,
                "errors": errors[:10]
            })
        except Exception as e:
            db.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            db.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@data_bp.route("/attendances", methods=["GET"])
def get_attendances():
    db = SessionLocal()
    try:
        q = db.query(prod.BizEmployeeAttendance)
        keyword = request.args.get('keyword', '')
        if keyword:
            q = q.filter(prod.BizEmployeeAttendance.employee_id.like(f"%{keyword}%"))
        res = paginate(q)
        res['records'] = [clean_dict(r) for r in res['records']]
        return jsonify(res)
    finally:
        db.close()
