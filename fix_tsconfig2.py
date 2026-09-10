with open('frontend/tsconfig.app.json', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('"allowArbitraryExtensions": true,', '"allowArbitraryExtensions": true,\n    "baseUrl": ".",\n    "paths": { "@/*": ["./src/*"] },')

with open('frontend/tsconfig.app.json', 'w', encoding='utf-8') as f:
    f.write(code)
