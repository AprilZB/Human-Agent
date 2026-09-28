import os
import base64
for root, dirs, files in os.walk('d:/DEV/Human-Agent'):
    for f in files:
        if f.endswith('.xlsx'):
            print(base64.b64encode(f.encode('utf-8')).decode('utf-8'))
