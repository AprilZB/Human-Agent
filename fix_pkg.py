import json
with open('frontend/package.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data['scripts']['build'] = "vite build"

with open('frontend/package.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)
