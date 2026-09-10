import re

css_addition = '''
.flex-col-container {
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
}
.flex-col-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-bottom: 0;
}
:deep(.flex-col-card .el-card__body) {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 15px; /* Keep some padding for reports, not 0 like grading */
}
'''

def patch_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()
    
    code = code.replace('class="report-container"', 'class="report-container flex-col-container"')
    code = code.replace('<el-card shadow="hover">', '<el-card shadow="hover" class="flex-col-card">')
    code = code.replace('height="calc(100vh - 200px)"', 'height="100%"')
    
    if '.flex-col-container' not in code:
        code = code.replace('</style>', css_addition + '\n</style>')
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(code)

patch_file('frontend/src/views/report/production.vue')
patch_file('frontend/src/views/report/overtime.vue')

