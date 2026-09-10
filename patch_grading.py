with open('frontend/src/views/grading/index.vue', 'r', encoding='utf-8') as f:
    code = f.read()

# Change title
code = code.replace("员工考评 (月度打分)", "员工日考评")

# Change el-table styling to reduce font size, eliminate scrollbars
# Reduce width="60" to width="45"
code = code.replace('width="60"', 'width="45"')
code = code.replace('width="100"', 'width="80"')

# Add size="small" to el-table
code = code.replace('<el-table ', '<el-table size="small" ')

# The height is calc(100vh - 200px), let's ensure body has no margin
# In style, add custom CSS for el-table__body to decrease font size
style_addition = '''
.excel-table {
  font-size: 12px;
}
.grade-cell {
  padding: 2px;
}
.el-card__body {
  padding: 10px;
}
'''
code = code.replace('</style>', style_addition + '</style>')

# Ensure we pass workshop_code if available
fetchData_old = '''const fetchData = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/v1/report/grading?month=' + selectedMonth.value)'''
fetchData_new = '''import { useUserStore } from '@/store/user'
const fetchData = async () => {
  loading.value = true
  const userStore = useUserStore()
  try {
    let url = '/api/v1/report/grading?month=' + selectedMonth.value
    if (userStore.userInfo?.workshop_code) {
      url += '&workshop_code=' + userStore.userInfo.workshop_code
    }
    const res = await axios.get(url)'''
code = code.replace(fetchData_old, fetchData_new)

with open('frontend/src/views/grading/index.vue', 'w', encoding='utf-8') as f:
    f.write(code)
