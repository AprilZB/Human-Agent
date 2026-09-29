with open('backend/app/api/data.py', 'r', encoding='utf-8') as f:
    code = f.read()

import_logic = '''        # Special aggregation for employees: they might have multiple rows for different skills
        if tab_name == 'employees':
            emp_dict = {}
            for rec in records:
                eid = rec.get('employee_id')
                if eid not in emp_dict:
                    emp_dict[eid] = rec.copy()
                    # Ensure skills is a list
                    skill = emp_dict[eid].get('skills')
                    if skill and isinstance(skill, str):
                        emp_dict[eid]['skills'] = [skill]
                    elif not skill:
                        emp_dict[eid]['skills'] = []
                else:
                    # Append skill
                    skill = rec.get('skills')
                    if skill and isinstance(skill, str):
                        if isinstance(emp_dict[eid].get('skills'), list):
                            emp_dict[eid]['skills'].append(skill)
            records = list(emp_dict.values())

        db = SessionLocal()'''

new_import_logic = '''        # Special aggregation for employees: they might have multiple rows for different skills
        if tab_name == 'employees':
            emp_dict = {}
            for rec in records:
                eid = rec.get('employee_id')
                if eid not in emp_dict:
                    emp_dict[eid] = rec.copy()
                    # Ensure skills is a list
                    skill = emp_dict[eid].get('skills')
                    if skill and isinstance(skill, str):
                        emp_dict[eid]['skills'] = [skill]
                    elif not skill:
                        emp_dict[eid]['skills'] = []
                else:
                    # Append skill
                    skill = rec.get('skills')
                    if skill and isinstance(skill, str):
                        if isinstance(emp_dict[eid].get('skills'), list):
                            emp_dict[eid]['skills'].append(skill)
            records = list(emp_dict.values())
        else:
            # Generic aggregation to prevent duplicate PKs in the same excel file
            pk_name = model.__table__.primary_key.columns.keys()[0]
            agg_dict = {}
            for rec in records:
                pval = rec.get(pk_name)
                if pval is not None:
                    agg_dict[pval] = rec
            records = list(agg_dict.values())

        db = SessionLocal()'''

code = code.replace(import_logic, new_import_logic)
with open('backend/app/api/data.py', 'w', encoding='utf-8') as f:
    f.write(code)
