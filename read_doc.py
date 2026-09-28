import os
for root, dirs, files in os.walk('.'):
    for f in files:
        if '数据库' in f.encode('utf-8').decode('utf-8', 'ignore'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                print(file.read())
