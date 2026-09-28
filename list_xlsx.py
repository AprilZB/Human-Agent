import os
files = []
for root, dirs, fnames in os.walk('d:/DEV/Human-Agent'):
    for f in fnames:
        if f.endswith('.xlsx'):
            files.append(os.path.join(root, f))
print(files)
