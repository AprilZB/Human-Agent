import sys
import os

with open('backend/app/api/data.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Append confirmations endpoint and generic import/export
new_code = '''
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
    "confirmations": prod.BizProductionConfirmation
}

@data_bp.route("/confirmations", methods=["GET"])
def get_confirmations():
    db = SessionLocal()
    try:
        q = db.query(prod.BizProductionConfirmation)
        keyword = request.args.get('keyword', '')
        if keyword:
            q = q.filter(or_(prod.BizProductionConfirmation.order_code.like(f"%{keyword}%"), prod.BizProductionConfirmation.material_code.like(f"%{keyword}%")))
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
    db = SessionLocal()
    try:
        items = db.query(model).all()
        data = [clean_dict(item.__dict__) for item in items]
        
        df = pd.DataFrame(data)
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
            
        out.seek(0)
        return send_file(out, download_name=f"{tab_name}.xlsx", as_attachment=True)
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
        df = pd.read_excel(file)
        # Handle nan -> None
        df = df.where(pd.notnull(df), None)
        records = df.to_dict(orient='records')
        
        db = SessionLocal()
        try:
            for rec in records:
                # Merge does an upsert if primary key matches
                obj = model(**rec)
                db.merge(obj)
            db.commit()
            return jsonify({"message": "Import successful", "count": len(records)})
        except Exception as e:
            db.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            db.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 400
'''

if 'TAB_MODEL_MAP' not in code:
    with open('backend/app/api/data.py', 'a', encoding='utf-8') as f:
        f.write(new_code)
