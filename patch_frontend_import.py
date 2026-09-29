import re

with open('frontend/src/views/data/index.vue', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace <el-upload> to include :before-upload="beforeImport"
code = re.sub(r'<el-upload (:action=".*?/import".*?)>', r'<el-upload \1 :before-upload="beforeImport">', code)

# Update imports
if 'ElMessageBox' not in code:
    code = code.replace("import { ElMessage } from 'element-plus'", "import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'")

# Add beforeImport logic
before_import_logic = '''
let importLoadingInstance: any = null

const beforeImport = () => {
  importLoadingInstance = ElLoading.service({
    lock: true,
    text: '正在读取文档并极速导入中，请勿进行其他操作...',
    background: 'rgba(0, 0, 0, 0.7)',
  })
  return true
}
'''
if 'const beforeImport =' not in code:
    code = code.replace("const handleImportSuccess = (res: any) => {", before_import_logic + "\nconst handleImportSuccess = (res: any) => {")

# Update handleImportSuccess
old_success = '''const handleImportSuccess = (res: any) => {
  if (res.error) {
    ElMessage.error(res.error)
  } else {
    ElMessage.success('导入成功，处理条数：' + res.count)
    fetchData()
  }
}'''

new_success = '''const handleImportSuccess = (res: any) => {
  if (importLoadingInstance) {
    importLoadingInstance.close()
  }
  if (res.error) {
    ElMessage.error(res.error)
  } else {
    ElMessageBox.alert(
      文档读取总数: <br/> +
      成功导入数: <span style="color: green"></span><br/> +
      失败数量: <span style="color: red"></span> + 
      (res.errors && res.errors.length > 0 ? <br/><br/><span style="color: gray; font-size: 12px">错误详情 (部分): </span> : ''),
      '导入结果详细报告',
      {
        dangerouslyUseHTMLString: true,
        type: res.fail > 0 ? 'warning' : 'success'
      }
    ).then(() => {
      fetchData()
    }).catch(() => {
      fetchData()
    })
  }
}'''
code = code.replace(old_success, new_success)

# Update handleImportError
old_error = '''const handleImportError = () => {
  ElMessage.error('网络或服务器异常，导入失败')
}'''
new_error = '''const handleImportError = () => {
  if (importLoadingInstance) {
    importLoadingInstance.close()
  }
  ElMessage.error('网络或服务器异常，导入失败')
}'''
code = code.replace(old_error, new_error)

with open('frontend/src/views/data/index.vue', 'w', encoding='utf-8') as f:
    f.write(code)
