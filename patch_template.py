with open('backend/app/api/data.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the export_data function to handle ?template=true
import re

old_func = '''@data_bp.route("/<tab_name>/export", methods=["GET"])
def export_data(tab_name):
    if tab_name not in TAB_MODEL_MAP:
        return jsonify({"error": "Invalid tab"}), 400
        
    model = TAB_MODEL_MAP[tab_name]
    db = SessionLocal()
    try:
        items = db.query(model).all()
        data = [clean_dict(item.__dict__) for item in items]
        
        if not data:
            cols = [c.name for c in model.__table__.columns if c.name not in ['id', 'created_at']]
            df = pd.DataFrame(columns=cols)
        else:
            df = pd.DataFrame(data)
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
            
        out.seek(0)
        return send_file(out, download_name=f"{tab_name}.xlsx", as_attachment=True)
    finally:
        db.close()'''

new_func = '''@data_bp.route("/<tab_name>/export", methods=["GET"])
def export_data(tab_name):
    if tab_name not in TAB_MODEL_MAP:
        return jsonify({"error": "Invalid tab"}), 400
        
    model = TAB_MODEL_MAP[tab_name]
    is_template = request.args.get('template') == '1'
    
    db = SessionLocal()
    try:
        if is_template:
            data = []
        else:
            items = db.query(model).all()
            data = [clean_dict(item.__dict__) for item in items]
        
        if not data:
            cols = [c.name for c in model.__table__.columns if c.name not in ['id', 'created_at']]
            df = pd.DataFrame(columns=cols)
        else:
            # Reorder columns to ensure id and created_at are at the end or removed if not wanted.
            # But here we just use pandas defaults for data
            df = pd.DataFrame(data)
            
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
            
        out.seek(0)
        filename = f"{tab_name}_template.xlsx" if is_template else f"{tab_name}.xlsx"
        return send_file(out, download_name=filename, as_attachment=True)
    finally:
        db.close()'''

code = code.replace(old_func, new_func)

with open('backend/app/api/data.py', 'w', encoding='utf-8') as f:
    f.write(code)
