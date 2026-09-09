with open('backend/app/api/data.py', 'r', encoding='utf-8') as f:
    code = f.read()

# add attendances to TAB_MODEL_MAP
code = code.replace('"confirmations": prod.BizProductionConfirmation', '"confirmations": prod.BizProductionConfirmation,\n    "attendances": prod.BizEmployeeAttendance')

# add GET endpoint for attendances
attendance_query = '''
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
'''

if 'get_attendances' not in code:
    code += "\n" + attendance_query

with open('backend/app/api/data.py', 'w', encoding='utf-8') as f:
    f.write(code)
