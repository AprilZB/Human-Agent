import json
import codecs

data = {
  "BOM\\u7f16\\u7801": "bom_code",
  "\\u7236\\u4ef6\\u7f16\\u7801": "product_code",
  "\\u5b50\\u4ef6\\u7f16\\u7801": "component_code",
  "\\u7528\\u91cf": "quantity",
  "\\u672c\\u5730\\u4e0d\\u826f\\u4ee3\\u7801": "defect_code",
  "SAP\\u4e0d\\u826f\\u4ee3\\u7801": "sap_defect_code",
  "\\u4e0d\\u826f\\u540d\\u79f0": "defect_name",
  "\\u63cf\\u8ff0": "description",
  "\\u5de5\\u5e8f\\u4ee3\\u7801": "process_code",
  "\\u5de5\\u5e8f\\u540d\\u79f0": "process_name",
  "\\u6807\\u51c6\\u5de5\\u65f6(\\u79d2)": "standard_time_sec",
  "\\u6240\\u9700\\u6280\\u80fd": "required_skills",
  "\\u8003\\u52e4\\u65e5\\u671f": "attendance_date",
  "\\u6392\\u73ed\\u73ed\\u6b21": "shift_code",
  "\\u662f\\u5426\\u8282\\u5047\\u65e5": "is_holiday",
  "\\u5b9e\\u9645\\u7b7e\\u5230": "actual_punch_in",
  "\\u5b9e\\u9645\\u7b7e\\u9000": "actual_punch_out",
  "\\u8003\\u52e4\\u72b6\\u6001": "attendance_status",
  "\\u6838\\u7b97\\u52a0\\u73ed(H)": "calculated_overtime",
  "\\u5de5\\u5382": "plant",
  "\\u5de5\\u4f5c\\u4e2d\\u5fc3": "work_center_code",
  "\\u751f\\u4ea7\\u6279\\u6b21\\u53f7": "batch_no",
  "\\u751f\\u4ea7\\u5355\\u53f7": "order_code",
  "\\u54c1\\u53f7": "material_code",
  "\\u5408\\u683c\\u54c1\\u6570": "yield_quantity",
  "\\u4e0d\\u5408\\u683c\\u6570": "scrap_quantity",
  "\\u62a5\\u5e9f\\u54c1\\u6570": "scrap_quantity",
  "\\u7269\\u6599\\u7f16\\u7801": "material_code",
  "\\u7269\\u6599\\u63cf\\u8ff0": "material_desc",
  "\\u672c\\u5730\\u7269\\u6599\\u7ec4\\u7f16\\u7801": "group_code",
  "SAP\\u5bf9\\u7167\\u7801": "sap_group_code",
  "\\u7269\\u6599\\u7ec4\\u540d\\u79f0": "group_name",
  "\\u8f66\\u95f4\\u7f16\\u7801": "workshop_code",
  "\\u8f66\\u95f4\\u540d\\u79f0": "workshop_name",
  "SAP\\u5de5\\u4f5c\\u4e2d\\u5fc3\\u5bf9\\u7167": "sap_work_center_code"
}

decoded_data = {codecs.decode(k, 'unicode_escape'): v for k, v in data.items()}

with open('backend/app/api/data.py', 'r', encoding='utf-8') as f:
    code = f.read()

# We need to insert these into the existing HEADER_MAPPING
import re
match = re.search(r'HEADER_MAPPING = \{(.*?)\}', code, re.DOTALL)
if match:
    existing = match.group(1)
    new_entries = []
    for k, v in decoded_data.items():
        if f'"{k}"' not in existing:
            new_entries.append(f'    "{k}": "{v}"')
    
    if new_entries:
        replacement = existing + ",\n" + ",\n".join(new_entries)
        code = code.replace(existing, replacement)

# We also need to drop the 'id' column if it exists in the valid_cols, or if ID mapped to id, we just don't allow 'id'
drop_id = '''        if 'id' in df.columns:
            df.drop(columns=['id'], inplace=True)
            
        # Keep only columns that exist in the model'''

code = code.replace('# Keep only columns that exist in the model', drop_id)

with open('backend/app/api/data.py', 'w', encoding='utf-8') as f:
    f.write(code)
