<template>
  <div class="grading-container">
    <el-card shadow="hover">
      <template #header>
        <div class="flex-between">
          <span>员工考评 (月度打分)</span>
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
      <el-table 
        :data="employees" 
        border 
        stripe 
        v-loading="loading" 
        height="calc(100vh - 200px)"
        class="excel-table"
      >
        <el-table-column prop="employee_name" label="姓名" width="100" fixed />
        
        <el-table-column 
          v-for="day in daysInMonth" 
          :key="day" 
          :label="String(day)" 
          width="60"
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

const selectedMonth = ref(new Date().toISOString().slice(0, 7))
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
  try {
    const res = await axios.get('/api/v1/report/grading?month=' + selectedMonth.value)
    employees.value = res.data
  } catch (e) {
    ElMessage.error('获取评分数据失败')
  } finally {
    loading.value = false
  }
}

const getGrade = (row: any, day: number) => {
  const dateStr = selectedMonth.value + '-' + String(day).padStart(2, '0')
  const score = row.grades[dateStr]
  return score !== undefined ? score : 0
}

const getGradeClass = (score: number) => {
  if (score === -4) return 'color-danger fw-bold'
  if (score === -2) return 'color-warning fw-bold'
  if (score === 2) return 'color-success fw-bold'
  if (score === 4) return 'color-primary fw-bold'
  return 'color-info'
}

const openEdit = (row: any, day: number) => {
  currentRow.value = row
  currentDay.value = day
  dialogVisible.value = true
}

const saveGrade = async (score: number) => {
  const dateStr = selectedMonth.value + '-' + String(currentDay.value).padStart(2, '0')
  try {
    await axios.post('/api/v1/report/grading', {
      employee_id: currentRow.value.employee_id,
      grade_date: dateStr,
      score: score
    })
    ElMessage.success('打分成功')
    dialogVisible.value = false
    // local update
    currentRow.value.grades[dateStr] = score
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
</style>
