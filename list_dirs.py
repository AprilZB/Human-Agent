import os
for f in os.listdir('d:/DEV/Human-Agent'):
    if os.path.isdir(os.path.join('d:/DEV/Human-Agent', f)):
        print(f)
