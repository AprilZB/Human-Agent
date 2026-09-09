with open('backend/app/api/system.py', 'r', encoding='utf-8') as f:
    code = f.read()

new_api = '''
from app.models.system import SysAttendanceRule
from sqlalchemy.orm import Session
from app.core.database import SessionLocal

@sys_bp.route("/attendance-rules", methods=["GET"])
def get_attendance_rules():
    db = SessionLocal()
    try:
        rules = db.query(SysAttendanceRule).all()
        # manual clean dict
        data = []
        for r in rules:
            d = r.__dict__.copy()
            d.pop('_sa_instance_state', None)
            if d.get('start_time'):
                d['start_time'] = str(d['start_time'])
            if d.get('end_time'):
                d['end_time'] = str(d['end_time'])
            if d.get('created_at'):
                d['created_at'] = str(d['created_at'])
            data.append(d)
        return jsonify(data)
    finally:
        db.close()

@sys_bp.route("/attendance-rules", methods=["POST"])
def create_attendance_rule():
    db = SessionLocal()
    try:
        data = request.json
        rule = SysAttendanceRule(**data)
        db.merge(rule)
        db.commit()
        return jsonify({"message": "success"})
    finally:
        db.close()

@sys_bp.route("/attendance-rules/<shift_code>", methods=["DELETE"])
def delete_attendance_rule(shift_code):
    db = SessionLocal()
    try:
        rule = db.query(SysAttendanceRule).filter_by(shift_code=shift_code).first()
        if rule:
            db.delete(rule)
            db.commit()
        return jsonify({"message": "success"})
    finally:
        db.close()
'''

if 'get_attendance_rules' not in code:
    code += "\n" + new_api

with open('backend/app/api/system.py', 'w', encoding='utf-8') as f:
    f.write(code)
