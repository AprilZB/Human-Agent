import json
with open('frontend/tsconfig.app.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data['compilerOptions']['baseUrl'] = '.'
data['compilerOptions']['paths'] = { "@/*": ["./src/*"] }
data['compilerOptions']['noUnusedLocals'] = False
data['compilerOptions']['noUnusedParameters'] = False

with open('frontend/tsconfig.app.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)
