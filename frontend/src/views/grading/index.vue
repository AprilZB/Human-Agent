<template>
  <div class="grading-container">
    <el-card shadow="hover" class="grading-card">
      <template #header>
        <div class="flex-between">
          <div class="header-left">
            <span class="page-title">员工日考评</span>
            <div class="legend-bar">
              <span class="legend-item">
                <span class="legend-badge badge-today">今</span> 当天 ({{ todayLabel }})
              </span>
              <span class="legend-item">
                <span class="legend-bar-indicator"></span> 当前周 ({{ currentWeekRangeLabel }})
              </span>
              <span class="legend-item">
                <span class="legend-color-box bg-weekend"></span> 周末
              </span>
              <span class="legend-item">
                <span class="legend-badge badge-holiday">休</span> 节假日
              </span>
            </div>
          </div>
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
          width="48"
          align="center"
          :class-name="getColumnClassName(day)"
          :label-class-name="getHeaderClassName(day)"
        >
          <template #header>
            <div class="col-header-box" :title="getDateTooltip(day)">
              <div class="header-day-num">{{ day }}</div>
              <div class="header-weekday">{{ getWeekdayText(day) }}</div>
              <span v-if="isToday(day)" class="header-badge badge-today">今</span>
              <span v-else-if="getHolidayName(day)" class="header-badge badge-holiday">
                {{ getHolidayName(day).length <= 2 ? getHolidayName(day) : '休' }}
              </span>
            </div>
          </template>
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
        <p style="color: #909399; font-size: 13px; margin-top: 4px;">
          {{ selectedMonth }}-{{ String(currentDay).padStart(2, '0') }} ({{ getWeekdayText(currentDay) }})
          <span v-if="isToday(currentDay)" style="color: #409eff; font-weight: bold; margin-left: 6px;">[当天]</span>
          <span v-else-if="getHolidayName(currentDay)" style="color: #f56c6c; font-weight: bold; margin-left: 6px;">[{{ getHolidayName(currentDay) }}]</span>
        </p>
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

const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

// 常见法定节假日配置
const holidays: Record<string, string> = {
  '2026-01-01': '元旦',
  '2026-02-16': '除夕',
  '2026-02-17': '春节',
  '2026-02-18': '春节',
  '2026-02-19': '春节',
  '2026-02-20': '春节',
  '2026-02-21': '春节',
  '2026-02-22': '春节',
  '2026-04-05': '清明节',
  '2026-05-01': '劳动节',
  '2026-05-02': '劳动节',
  '2026-05-03': '劳动节',
  '2026-06-19': '端午节',
  '2026-09-25': '中秋节',
  '2026-09-26': '中秋假',
  '2026-09-27': '中秋假',
  '2026-10-01': '国庆节',
  '2026-10-02': '国庆假',
  '2026-10-03': '国庆假',
  '2026-10-04': '国庆假',
  '2026-10-05': '国庆假',
  '2026-10-06': '国庆假',
  '2026-10-07': '国庆假',
}

const daysInMonth = computed(() => {
  if (!selectedMonth.value) return []
  const [year, month] = selectedMonth.value.split('-').map(Number)
  const days = new Date(year, month, 0).getDate()
  return Array.from({ length: days }, (_, i) => i + 1)
})

// 判断基准当天：若是2026-09则取业务基准日24日，若为当前系统所在月份则取真实今天，否则该月无当天
const getTodayDay = () => {
  if (!selectedMonth.value) return -1
  const now = new Date()
  const realYearMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
  if (selectedMonth.value === '2026-09') {
    return 24 // 系统演示与业务测试基准日 (2026-09-24)
  } else if (selectedMonth.value === realYearMonth) {
    return now.getDate()
  }
  return -1
}

const isToday = (day: number) => {
  return day === getTodayDay()
}

// 计算当前周覆盖的日期（周一至周日）
const currentWeekDays = computed(() => {
  const targetDay = getTodayDay()
  if (targetDay <= 0 || !selectedMonth.value) return new Set<number>()
  const [year, month] = selectedMonth.value.split('-').map(Number)
  const targetDate = new Date(year, month - 1, targetDay)
  
  const dayOfWeek = targetDate.getDay()
  const diffToMonday = (dayOfWeek + 6) % 7
  
  const mondayDate = new Date(year, month - 1, targetDay - diffToMonday)
  
  const weekSet = new Set<number>()
  for (let i = 0; i < 7; i++) {
    const d = new Date(mondayDate.getFullYear(), mondayDate.getMonth(), mondayDate.getDate() + i)
    if (d.getFullYear() === year && d.getMonth() === month - 1) {
      weekSet.add(d.getDate())
    }
  }
  return weekSet
})

const isCurrentWeek = (day: number) => {
  return currentWeekDays.value.has(day)
}

const getDayOfWeek = (day: number) => {
  if (!selectedMonth.value) return 0
  const [year, month] = selectedMonth.value.split('-').map(Number)
  return new Date(year, month - 1, day).getDay()
}

const getWeekdayText = (day: number) => {
  return weekDays[getDayOfWeek(day)]
}

const isWeekend = (day: number) => {
  const dow = getDayOfWeek(day)
  return dow === 0 || dow === 6
}

const getHolidayName = (day: number) => {
  if (!selectedMonth.value) return ''
  const dateStr = `${selectedMonth.value}-${String(day).padStart(2, '0')}`
  return holidays[dateStr] || ''
}

const isHoliday = (day: number) => {
  return !!getHolidayName(day)
}

const todayLabel = computed(() => {
  const d = getTodayDay()
  return d > 0 ? `${d}日` : '无'
})

const currentWeekRangeLabel = computed(() => {
  if (currentWeekDays.value.size === 0) return '无'
  const days = Array.from(currentWeekDays.value).sort((a, b) => a - b)
  return `${days[0]}日 ~ ${days[days.length - 1]}日`
})

const getDateTooltip = (day: number) => {
  const dateStr = `${selectedMonth.value}-${String(day).padStart(2, '0')}`
  const weekday = getWeekdayText(day)
  const holiday = getHolidayName(day)
  let tip = `${dateStr} (${weekday})`
  if (isToday(day)) tip += '【当天】'
  if (holiday) tip += `【${holiday}】`
  else if (isWeekend(day)) tip += '【周末】'
  return tip
}

const getHeaderClassName = (day: number) => {
  const classes: string[] = ['col-day-th']
  if (isToday(day)) {
    classes.push('th-today')
  } else if (isHoliday(day)) {
    classes.push('th-holiday')
  } else if (isWeekend(day)) {
    classes.push('th-weekend')
  }
  if (isCurrentWeek(day)) {
    classes.push('th-current-week')
  }
  return classes.join(' ')
}

const getColumnClassName = (day: number) => {
  const classes: string[] = ['col-day-td']
  if (isToday(day)) {
    classes.push('td-today')
  } else if (isHoliday(day)) {
    classes.push('td-holiday')
  } else if (isWeekend(day)) {
    classes.push('td-weekend')
  }
  if (isCurrentWeek(day)) {
    classes.push('td-current-week')
  }
  return classes.join(' ')
}

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
.header-left { display: flex; align-items: center; flex-wrap: wrap; gap: 15px; }
.page-title { font-weight: bold; font-size: 16px; color: #303133; }
.header-actions { display: flex; align-items: center; }
.inline-upload { display: inline-flex; vertical-align: middle; }
.mr-10 { margin-right: 10px; }

/* Legend Bar */
.legend-bar {
  display: inline-flex;
  align-items: center;
  gap: 14px;
  padding: 3px 10px;
  background-color: #f8f9fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  font-size: 12px;
  color: #606266;
}
.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.legend-badge {
  display: inline-block;
  font-size: 10px;
  line-height: 1;
  padding: 2px 4px;
  border-radius: 3px;
  font-weight: bold;
}
.legend-bar-indicator {
  display: inline-block;
  width: 14px;
  height: 4px;
  background-color: #409eff;
  border-radius: 2px;
}
.legend-color-box {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 2px;
}
.bg-weekend {
  background-color: #fdf6ec;
  border: 1px solid #e6a23c;
}

/* Col Header Box */
.col-header-box {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  line-height: 1.2;
  cursor: default;
  padding: 1px 0;
}
.header-day-num {
  font-size: 13px;
  font-weight: 700;
  line-height: 1.1;
}
.header-weekday {
  font-size: 11px;
  line-height: 1.1;
  margin-top: 2px;
  color: #909399;
}
.header-badge {
  position: absolute;
  top: -6px;
  right: -8px;
  font-size: 9px;
  line-height: 1;
  padding: 1px 2px;
  border-radius: 2px;
  font-weight: bold;
  transform: scale(0.85);
}
.badge-today {
  background-color: #ffffff;
  color: #409eff;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}
.badge-holiday {
  background-color: #f56c6c;
  color: #ffffff;
  box-shadow: 0 1px 2px rgba(245, 108, 108, 0.4);
}

/* Table Header Custom Colors */
:deep(.excel-table th.col-day-th) {
  padding: 3px 0 !important;
  transition: all 0.2s ease;
  user-select: none;
}

/* Today (Highest priority for th) */
:deep(.excel-table th.th-today) {
  background: #409eff !important;
  color: #ffffff !important;
  border-bottom: 2px solid #1d68c9 !important;
}
:deep(.excel-table th.th-today .header-day-num) {
  color: #ffffff !important;
  font-weight: 800;
  font-size: 14px;
}
:deep(.excel-table th.th-today .header-weekday) {
  color: #e6f1fc !important;
  font-weight: 600;
}

/* Current Week (Top blue border for all days in week) */
:deep(.excel-table th.th-current-week) {
  border-top: 3px solid #409eff !important;
}
:deep(.excel-table th.th-current-week:not(.th-today):not(.th-holiday):not(.th-weekend)) {
  background-color: #ecf5ff !important;
}
:deep(.excel-table th.th-current-week:not(.th-today):not(.th-holiday):not(.th-weekend) .header-weekday) {
  color: #409eff !important;
  font-weight: 600;
}

/* Holiday Header */
:deep(.excel-table th.th-holiday:not(.th-today)) {
  background-color: #fef0f0 !important;
}
:deep(.excel-table th.th-holiday:not(.th-today) .header-day-num) {
  color: #f56c6c !important;
  font-weight: 700;
}
:deep(.excel-table th.th-holiday:not(.th-today) .header-weekday) {
  color: #f56c6c !important;
  font-weight: 600;
}

/* Weekend Header */
:deep(.excel-table th.th-weekend:not(.th-today):not(.th-holiday)) {
  background-color: #fdf6ec !important;
}
:deep(.excel-table th.th-weekend:not(.th-today):not(.th-holiday) .header-day-num) {
  color: #d97706 !important;
  font-weight: 700;
}
:deep(.excel-table th.th-weekend:not(.th-today):not(.th-holiday) .header-weekday) {
  color: #d97706 !important;
  font-weight: 600;
}

/* Table Body Cells (td) Custom Colors */
:deep(.excel-table td.col-day-td) {
  padding: 3px 0 !important;
}

/* Today Column Cells */
:deep(.excel-table td.td-today) {
  background-color: #f0f7ff !important;
  border-left: 1px solid #c6e2ff !important;
  border-right: 1px solid #c6e2ff !important;
}
:deep(.excel-table td.td-today .grade-cell) {
  font-weight: 600;
}

/* Current Week Cells */
:deep(.excel-table td.td-current-week:not(.td-today):not(.td-holiday):not(.td-weekend)) {
  background-color: #fafcff;
}

/* Holiday Cells */
:deep(.excel-table td.td-holiday:not(.td-today)) {
  background-color: #fef8f8;
}

/* Weekend Cells */
:deep(.excel-table td.td-weekend:not(.td-today):not(.td-holiday)) {
  background-color: #fdfcf9;
}

.grade-cell {
  cursor: pointer;
  padding: 5px;
  border-radius: 4px;
}
.grade-cell:hover {
  background-color: #e8f4ff;
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
</style>
