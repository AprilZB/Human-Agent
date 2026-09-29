with open('backend/app/api/data.py', 'r', encoding='utf-8') as f:
    code = f.read()

bad = "        if 'id' in df.columns:\n            df.drop(columns=['id'], inplace=True)\n            \n        # Keep only"
good = "        if 'id' in df.columns:\n            df.drop(columns=['id'], inplace=True)\n            \n        # Keep only"

code = code.replace("                if 'id' in df.columns:", "        if 'id' in df.columns:")

with open('backend/app/api/data.py', 'w', encoding='utf-8') as f:
    f.write(code)
