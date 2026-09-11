with open('backend/app/api/report.py', 'r', encoding='utf-8') as f:
    code = f.read()

import re

# Fix get_overtime_report
code = code.replace("BaseEmployee.employee_name,", "BaseEmployee.name,")
code = code.replace("BizEmployeeAttendance.employee_id == BaseEmployee.employee_code", "BizEmployeeAttendance.employee_id == BaseEmployee.employee_id")
code = code.replace("q.group_by(BizEmployeeAttendance.employee_id, BaseEmployee.employee_name)", "q.group_by(BizEmployeeAttendance.employee_id, BaseEmployee.name)")

# Fix get_grading_report
old_grading = '''        res = []
        for e in employees:
            res.append({
                "employee_id": e.employee_code,
                "employee_name": e.employee_name,
                "grades": grade_map.get(e.employee_code, {})
            })'''

new_grading = '''        res = []
        for e in employees:
            res.append({
                "employee_id": e.employee_id,
                "employee_name": e.name,
                "grades": grade_map.get(e.employee_id, {})
            })'''
code = code.replace(old_grading, new_grading)

with open('backend/app/api/report.py', 'w', encoding='utf-8') as f:
    f.write(code)
