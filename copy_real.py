import os
import shutil
import base64

for root, dirs, files in os.walk('d:/DEV/Human-Agent'):
    for f in files:
        if f.endswith('.xlsx') and 'import_test.xlsx' not in f:
            src = os.path.join(root, f)
            print("Found:", src)
            shutil.copy(src, 'd:/DEV/Human-Agent/real_import.xlsx')
