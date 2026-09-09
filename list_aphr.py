import os
for root, dirs, files in os.walk('D:/DEV/APHR'):
    if root == 'D:/DEV/APHR':
        for file in files:
            print(file)
