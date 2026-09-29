with open('backend/app/api/data.py', 'r', encoding='utf-8') as f:
    code = f.read()

import_logic = '''        # Parse JSON fields if necessary
        import json
        for rec in records:
            for k, v in rec.items():
                if isinstance(v, str) and (v.strip().startswith('{') or v.strip().startswith('[')):'''

new_import_logic = '''        # Parse JSON fields if necessary
        import json
        import pandas as pd
        for rec in records:
            for k, v in rec.items():
                if isinstance(v, pd.Timestamp):
                    rec[k] = v.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(v, str) and (v.strip().startswith('{') or v.strip().startswith('[')):'''

code = code.replace(import_logic, new_import_logic)
with open('backend/app/api/data.py', 'w', encoding='utf-8') as f:
    f.write(code)
