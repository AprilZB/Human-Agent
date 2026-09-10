import re
with open('frontend/src/views/grading/index.vue', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('calc(100vh - 100px)', 'calc(100vh - 120px)')

with open('frontend/src/views/grading/index.vue', 'w', encoding='utf-8') as f:
    f.write(code)
