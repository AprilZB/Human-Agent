with open('frontend/src/views/settings/index.vue', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace("http://localhost:8100/api/v1/sys/config", "http://localhost:8100/api/v1/configs")
code = code.replace("http://localhost:8100/api/v1/sys/attendance-rules", "http://localhost:8100/api/v1/attendance-rules")

# Fix saveConfig logic which used to be PUT on /configs/{key}
save_config_old = '''const saveConfig = async (row: any) => {
  try {
    await axios.post('http://localhost:8100/api/v1/configs', [
      { config_key: row.config_key, config_value: row.config_value }
    ])
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}'''

save_config_new = '''const saveConfig = async (row: any) => {
  try {
    await axios.put('http://localhost:8100/api/v1/configs/' + row.config_key, {
      config_value: row.config_value
    })
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}'''

code = code.replace(save_config_old, save_config_new)

with open('frontend/src/views/settings/index.vue', 'w', encoding='utf-8') as f:
    f.write(code)
