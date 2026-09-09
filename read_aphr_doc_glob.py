import glob
for file in glob.glob('D:/DEV/APHR/APHR_*v1.5.md'):
    print(f"Reading {file}")
    with open(file, 'r', encoding='utf-8') as f:
        print(f.read())
