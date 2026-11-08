<template>
  <div class="grading-container">
    <el-card shadow="hover" class="grading-card">
      <template #header>
        <div class="flex-between">
          <span>员工日考评</span>
          <div>
            <el-date-picker
              v-model="selectedMonth"
              type="month"
              placeholder="选择月份"
              value-format="YYYY-MM"
              @change="fetchData"
              class="mr-10"
            />
            <el-button type="primary" @click="fetchData">刷新</el-button>
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
      </el-table>
    </el-card>

    <el-dialog title="快捷打分" v-model="dialogVisible" width="300px" center>
      <div style="text-align: center; margin-bottom: 20px;">
        <p><strong>{{ currentRow?.employee_name }}</strong> - {{ selectedMonth }}-{{ String(currentDay).padStart(2, '0') }}</p>
      </div>
      <div class="quick-grade-btns">
        <el-button type="danger" @click="saveGrade(-4)">-4 (极差)</el-button>
        <el-button type="warning" @click="saveGrade(-2)">-2 (较差)</el-button>
        <el-button type="info" @click="saveGrade(0)">0 (一般)</el-button>
        <el-button type="success" @click="saveGrade(2)">2 (良好)</el-button>
        <el-button type="primary" @click="saveGrade(4)">4 (优秀)</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

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

import { useUserStore } from '@/store/user'
const fetchData = async () => {
  loading.value = true
  const userStore = useUserStore()
  try {
    let url = '/api/v1/report/grading?month=' + selectedMonth.value
    if (userStore.userInfo?.workshop_code) {
      url += '&workshop_code=' + userStore.userInfo.workshop_code
    }
    const res = await axios.get(url)
    employees.value = res.data
  } catch (e) {
    ElMessage.error('获取评分数据失败')
  } finally {
    loading.value = false
  }
}

const getGrade = (row: any, day: number) => {
  const dateStr = selectedMonth.value + '-' + String(day).padStart(2, '0')
  const score = row.grades ? row.grades[dateStr] : undefined
  if (score === undefined || score === 0) return '休'
  return score
}

const getGradeClass = (score: any) => {
  if (score === '休') return 'color-muted'
  if (score === 4 || score >= 90) return 'color-primary fw-bold'
  if (score === 2 || score >= 88) return 'color-success fw-bold'
  if (score === -2 || (typeof score === 'number' && score < 86 && score >= 80)) return 'color-warning fw-bold'
  if (score === -4 || (typeof score === 'number' && score < 80)) return 'color-danger fw-bold'
  return 'color-info'
}

const openEdit = (row: any, day: number) => {
  currentRow.value = row
  currentDay.value = day
  dialogVisible.value = true
}

const saveGrade = async (deltaScore: number) => {
  const dateStr = selectedMonth.value + '-' + String(currentDay.value).padStart(2, '0')
  const totalScore = 86 + deltaScore
  try {
    await axios.post('/api/v1/report/grading', {
      employee_id: currentRow.value.employee_id,
      grade_date: dateStr,
      score: totalScore,
      remark: `班组长快捷评定 (加减分: ${deltaScore >= 0 ? '+' : ''}${deltaScore})`
    })
    ElMessage.success('打分成功')
    dialogVisible.value = false
    // local update
    if (!currentRow.value.grades) currentRow.value.grades = {}
    currentRow.value.grades[dateStr] = totalScore
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
