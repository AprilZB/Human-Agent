with open('backend/app/api/report.py', 'r', encoding='utf-8') as f:
    code = f.read()

import re
old_get = '''        # Get all employees
        employees = db.query(BaseEmployee).all()'''
new_get = '''        workshop_code = request.args.get('workshop_code')
        # Get all employees
        q = db.query(BaseEmployee)
        if workshop_code:
            q = q.filter_by(workshop_code=workshop_code)
        employees = q.all()'''

code = code.replace(old_get, new_get)
with open('backend/app/api/report.py', 'w', encoding='utf-8') as f:
    f.write(code)
