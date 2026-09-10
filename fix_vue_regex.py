import re
with open('frontend/src/views/report/production.vue', 'r', encoding='utf-8') as f:
    code = f.read()

fetchData = '''const fetchData = async () => {
  loading.value = true
  try {
    let url = '/api/v1/report/production?'
    if (dateRange.value && dateRange.value.length === 2) {
      url += "start_date=" + dateRange.value[0] + "&end_date=" + dateRange.value[1] + "&"
    }
    if (productCode.value) {
      url += "product_code=" + productCode.value
    }
    const res = await axios.get(url)
    orders.value = res.data
  } catch (e) {
    ElMessage.error('查询失败')
  } finally {
    loading.value = false
  }
}'''
code = re.sub(r'const fetchData = async \(\) => \{.*?\n\}', fetchData, code, flags=re.DOTALL)

openDetail = '''const openDetail = async (row: any) => {
  dialogVisible.value = true
  detailLoading.value = true
  try {
    const res = await axios.get("/api/v1/report/production/" + row.order_code + "/confirmations")
    details.value = res.data
  } catch (e) {
    ElMessage.error('获取明细失败')
  } finally {
    detailLoading.value = false
  }
}'''
code = re.sub(r'const openDetail = async \(row: any\) => \{.*?\n\}', openDetail, code, flags=re.DOTALL)

with open('frontend/src/views/report/production.vue', 'w', encoding='utf-8') as f:
    f.write(code)


with open('frontend/src/views/report/overtime.vue', 'r', encoding='utf-8') as f:
    code = f.read()

fetchData_ot = '''const fetchData = async () => {
  loading.value = true
  try {
    let url = '/api/v1/report/overtime?'
    if (dateRange.value && dateRange.value.length === 2) {
      url += "start_date=" + dateRange.value[0] + "&end_date=" + dateRange.value[1]
    }
    const res = await axios.get(url)
    employees.value = res.data
  } catch (e) {
    ElMessage.error('查询失败')
  } finally {
    loading.value = false
  }
}'''
code = re.sub(r'const fetchData = async \(\) => \{.*?\n\}', fetchData_ot, code, flags=re.DOTALL)

openDetail_ot = '''const openDetail = async (row: any) => {
  dialogVisible.value = true
  detailLoading.value = true
  activeTab.value = 'this_month'
  try {
    const res = await axios.get("/api/v1/report/overtime/" + row.employee_id)
    details.value = res.data
  } catch (e) {
    ElMessage.error('获取明细失败')
  } finally {
    detailLoading.value = false
  }
}'''
code = re.sub(r'const openDetail = async \(row: any\) => \{.*?\n\}', openDetail_ot, code, flags=re.DOTALL)

with open('frontend/src/views/report/overtime.vue', 'w', encoding='utf-8') as f:
    f.write(code)
