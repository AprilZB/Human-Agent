<template>
  <div class="grading-container">
    <el-card shadow="hover" class="grading-card">
      <template #header>
        <div class="flex-between">
          <span style="font-weight: bold; font-size: 16px;">员工日考评</span>
          <div class="header-actions">
            <el-date-picker
              v-model="selectedMonth"
              type="month"
              placeholder="选择月份"
              value-format="YYYY-MM"
              @change="fetchData"
              class="mr-10"
              style="width: 140px;"
            />
            <el-button type="primary" @click="fetchData" class="mr-10">刷新</el-button>
            <el-button type="warning" plain class="mr-10" @click="downloadTemplate">下载导入模板</el-button>
            <el-upload
              :action="'/api/v1/report/grading/import?month=' + selectedMonth"
              :show-file-list="false"
              :before-upload="beforeImport"
              :on-success="handleImportSuccess"
              :on-error="handleImportError"
              class="mr-10 inline-upload"
            >
              <el-button type="success" plain>Excel 导入</el-button>
            </el-upload>
            <el-button type="info" plain @click="handleExport">Excel 导出</el-button>
          </div>
        </div>
      </template>

      <!-- Excel-like Table -->
      <el-table size="small" 
        :data="employees" 
        border 
        stripe 
        v-loading="loading" 
        height="100%"
        class="excel-table"
      >
        <el-table-column prop="employee_id" label="工号" width="105" fixed />
        <el-table-column prop="employee_name" label="姓名" width="80" fixed />
        
        <el-table-column 
          v-for="day in daysInMonth" 
          :key="day" 
          :label="String(day)" 
          width="45"
          align="center"
        >
          <template #default="scope">
            <div class="grade-cell" @click="openEdit(scope.row, day)">
              <span :class="getGradeClass(getGrade(scope.row, day))">
                {{ getGrade(scope.row, day) }}
              </span>
            </div>
          </template>
        </el-table-column>

        <!-- 月度分数列：计算当月合计分数 + 80，有可能超过100分 -->
        <el-table-column 
          label="月度分数" 
          width="100" 
          align="center" 
          fixed="right"
        >
          <template #default="scope">
            <el-tag 
              :type="getMonthlyScore(scope.row) >= 100 ? 'primary' : (getMonthlyScore(scope.row) >= 80 ? 'success' : 'danger')"
              size="small"
              effect="dark"
              style="font-weight: bold; font-size: 13px; min-width: 48px;"
            >
              {{ getMonthlyScore(scope.row) }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog title="快捷打分" v-model="dialogVisible" width="320px" center>
      <div style="text-align: center; margin-bottom: 16px;">
        <p style="font-size: 15px;"><strong>{{ currentRow?.employee_name }}</strong> ({{ currentRow?.employee_id }})</p>
        <p style="color: #909399; font-size: 13px; margin-top: 4px;">{{ selectedMonth }}-{{ String(currentDay).padStart(2, '0') }}</p>
      </div>
      <div class="quick-grade-btns">
        <el-button type="danger" @click="saveGrade(-4)">-4 (极差)</el-button>
        <el-button type="warning" @click="saveGrade(-2)">-2 (较差)</el-button>
        <el-button type="info" @click="saveGrade(0)">0 (一般)</el-button>
        <el-button type="success" @click="saveGrade(2)">2 (良好)</el-button>
        <el-button type="primary" @click="saveGrade(4)">4 (优秀)</el-button>
        <el-button plain type="info" @click="saveGrade(null)">设为休息 (休)</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { useUserStore } from '@/store/user'

const selectedMonth = ref('2026-09')
const employees = ref<any[]>([])
const loading = ref(false)

const dialogVisible = ref(false)
const currentRow = ref<any>(null)
const currentDay = ref<number>(1)

const daysInMonth = computed(() => {
  if (!selectedMonth.value) return []
  const [year, month] = selectedMonth.value.split('-').map(Number)
  const days = new Date(year, month, 0).getDate()
  return Array.from({ length: days }, (_, i) => i + 1)
})

const fetchData = async () => {
  loading.value = true
  const userStore = useUserStore()
  try {
    let url = '/api/v1/report/grading?month=' + selectedMonth.value + '&workshop_code=中包车间'
    if (userStore.userInfo?.employee_id) {
      url += '&team_leader_id=' + encodeURIComponent(userStore.userInfo.employee_id)
    }
    const res = await axios.get(url)
    employees.value = res.data
  } catch (e) {
    ElMessage.error('获取评分数据失败')
  } finally {
    loading.value = false
  }
}

let importLoadingInstance: any = null

const beforeImport = () => {
  importLoadingInstance = ElLoading.service({
    lock: true,
    text: '正在读取考评文档并导入中，请稍候...',
    background: 'rgba(0, 0, 0, 0.7)',
  })
  return true
}

const handleImportSuccess = (res: any) => {
  if (importLoadingInstance) {
    importLoadingInstance.close()
  }
  if (res.error) {
    ElMessage.error(res.error)
  } else {
    ElMessageBox.alert(
      `文档读取考评数: ${res.total_read || 0}<br/>` +
      `成功导入数: <span style="color: green">${res.success || 0}</span><br/>` +
      `失败数量: <span style="color: red">${res.fail || 0}</span>` + 
      (res.errors && res.errors.length > 0 ? `<br/><br/><span style="color: gray; font-size: 12px">错误详情 (部分): ${res.errors[0]}</span>` : ''),
      '考评导入结果',
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
}

const handleImportError = (err: any) => {
  if (importLoadingInstance) {
    importLoadingInstance.close()
  }
  let errorMsg = '网络或服务器异常，导入失败'
  try {
    if (err && err.message) {
      const parsed = JSON.parse(err.message)
      if (parsed.error) errorMsg = parsed.error
    }
  } catch (e) {
    if (typeof err === 'string') errorMsg = err
  }
  ElMessageBox.alert(errorMsg, '导入失败提示', {
    type: 'error',
    confirmButtonText: '确定'
  })
}

const downloadTemplate = () => {
  window.open('/api/v1/report/grading/template?month=' + selectedMonth.value)
}

const handleExport = () => {
  window.open('/api/v1/report/grading/export?month=' + selectedMonth.value)
}

const getGrade = (row: any, day: number) => {
  const dateStr = selectedMonth.value + '-' + String(day).padStart(2, '0')
  if (!row.grades || row.grades[dateStr] === undefined || row.grades[dateStr] === null) {
    return '休'
  }
  const score = row.grades[dateStr]
  if (score === '休') return '休'
  if (typeof score === 'number' && score >= 50) {
    return score - 86
  }
  return score
}

const getGradeClass = (score: any) => {
  if (score === '休') return 'color-muted'
  if (score === 4 || score === '+4') return 'color-primary fw-bold'
  if (score === 2 || score === '+2') return 'color-success fw-bold'
  if (score === 0) return 'color-info'
  if (score === -2) return 'color-warning fw-bold'
  if (score === -4) return 'color-danger fw-bold'
  return 'color-info'
}

// 计算当月合计分数 + 80（有可能会超过100分）
const getMonthlyScore = (row: any) => {
  let totalDelta = 0
  daysInMonth.value.forEach((day: number) => {
    const val = getGrade(row, day)
    if (typeof val === 'number') {
      totalDelta += val
    }
  })
  return 80 + totalDelta
}

const openEdit = (row: any, day: number) => {
  currentRow.value = row
  currentDay.value = day
  dialogVisible.value = true
}

const saveGrade = async (deltaScore: number | null) => {
  const dateStr = selectedMonth.value + '-' + String(currentDay.value).padStart(2, '0')
  try {
    if (deltaScore === null) {
      await axios.delete('/api/v1/report/grading', {
        params: {
          employee_id: currentRow.value.employee_id,
          grade_date: dateStr
        }
      })
      ElMessage.success('已设置为休息 (休)')
      if (currentRow.value.grades) {
        delete currentRow.value.grades[dateStr]
      }
    } else {
      await axios.post('/api/v1/report/grading', {
        employee_id: currentRow.value.employee_id,
        grade_date: dateStr,
        score: deltaScore,
        remark: `班组长快捷评定 (评分: ${deltaScore >= 0 ? '+' : ''}${deltaScore})`
      })
      ElMessage.success('打分成功')
      if (!currentRow.value.grades) currentRow.value.grades = {}
      currentRow.value.grades[dateStr] = deltaScore
    }
    dialogVisible.value = false
  } catch (e) {
    ElMessage.error('打分失败')
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.flex-between { display: flex; justify-content: space-between; align-items: center; }
.header-actions { display: flex; align-items: center; }
.inline-upload { display: inline-flex; vertical-align: middle; }
.mr-10 { margin-right: 10px; }
.grade-cell {
  cursor: pointer;
  padding: 5px;
  border-radius: 4px;
}
.grade-cell:hover {
  background-color: #f5f7fa;
}
.color-danger { color: #F56C6C; }
.color-warning { color: #E6A23C; }
.color-success { color: #67C23A; }
.color-primary { color: #409EFF; }
.color-info { color: #909399; }
.color-muted { color: #C0C4CC; }
.fw-bold { font-weight: bold; }
.quick-grade-btns {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.quick-grade-btns .el-button {
  margin-left: 0;
  width: 100%;
}

.grading-container {
  height: calc(100vh - 120px);
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
