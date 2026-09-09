import os
for root, dirs, files in os.walk('项目文件'):
    for file in files:
        if file.endswith('.md'):
            print(os.path.join(root, file))
