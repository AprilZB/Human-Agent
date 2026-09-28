import os
with open('dirs.txt', 'w', encoding='utf-8') as f:
    for item in os.listdir('d:/DEV/Human-Agent'):
        f.write(item + '\n')
