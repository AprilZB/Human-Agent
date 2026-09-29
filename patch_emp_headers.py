with open('backend/app/api/data.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_mapping = '''    # 员工基本信息
    "姓名": "name",
    "车间": "workshop_code",
    "健康证状态": "health_cert_status",
    "上岗证状态": "work_cert_status"'''

new_mapping = '''    # 员工基本信息
    "姓名": "name",
    "车间": "workshop_code",
    "健康证状态": "health_cert_status",
    "上岗证状态": "work_cert_status",
    "健康证状态/有效期": "health_cert_status",
    "上岗证状态/有效期": "work_cert_status",
    "技能矩阵": "skills"'''

code = code.replace(old_mapping, new_mapping)

with open('backend/app/api/data.py', 'w', encoding='utf-8') as f:
    f.write(code)
