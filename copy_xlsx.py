import os
import shutil
for root, dirs, files in os.walk('d:/DEV/Human-Agent'):
    for f in files:
        if f.endswith('.xlsx'):
            src = os.path.join(root, f)
            dst = 'd:/DEV/Human-Agent/import_test.xlsx'
            shutil.copy(src, dst)
            print("Copied to import_test.xlsx")
