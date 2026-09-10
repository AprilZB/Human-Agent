import os
import re

for root, dirs, files in os.walk('frontend/src'):
    for file in files:
        if file.endswith('.vue') or file.endswith('.ts'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'http://localhost:8100/api/v1' in content:
                content = content.replace('http://localhost:8100/api/v1', '/api/v1')
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Updated {path}")
