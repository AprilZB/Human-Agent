import os
for root, dirs, files in os.walk('d:/DEV/Human-Agent'):
    for f in files:
        if f.endswith('.xlsx'):
            print(os.path.join(root, f).encode('utf-8').decode('utf-8', 'ignore'))
