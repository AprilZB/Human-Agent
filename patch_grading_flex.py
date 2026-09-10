with open('frontend/src/views/grading/index.vue', 'r', encoding='utf-8') as f:
    code = f.read()

# Change table height to 100%
code = code.replace('height="calc(100vh - 160px)"', 'height="100%"')

# Modify the styles
old_style = '''
.excel-table {
  font-size: 12px;
}
.grade-cell {
  padding: 2px;
}
:deep(.el-card__body) {
  padding: 10px;
}
</style>
'''

new_style = '''
.grading-container {
  height: calc(100vh - 100px);
  display: flex;
  flex-direction: column;
}
.grading-card {
  flex: 1;
  display: flex;
  flex-direction: column;
}
:deep(.grading-card .el-card__body) {
  flex: 1;
  padding: 0;
  overflow: hidden;
}
.excel-table {
  font-size: 12px;
  width: 100%;
  height: 100%;
}
.grade-cell {
  padding: 2px;
}
</style>
'''

code = code.replace(old_style.strip(), new_style.strip())
code = code.replace('<el-card shadow="hover">', '<el-card shadow="hover" class="grading-card">')

with open('frontend/src/views/grading/index.vue', 'w', encoding='utf-8') as f:
    f.write(code)
