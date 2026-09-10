import re
with open('frontend/src/views/grading/index.vue', 'r', encoding='utf-8') as f:
    code = f.read()

# Change height to avoid page scrolling
code = code.replace('height="calc(100vh - 200px)"', 'height="calc(100vh - 160px)"')
code = code.replace('.el-card__body {', ':deep(.el-card__body) {')

with open('frontend/src/views/grading/index.vue', 'w', encoding='utf-8') as f:
    f.write(code)
