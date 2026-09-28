import ast
with open('backend/app/api/data.py', 'r', encoding='utf-8') as f:
    code = f.read()
print(code[-1000:])
