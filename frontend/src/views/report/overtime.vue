<template>
  <div class="report-container flex-col-container">
    <el-card shadow="hover" class="flex-col-card">
      <template #header>
        <div class="filter-bar">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            @change="fetchData"
            class="mr-10"
          />
          <el-button type="primary" @click="fetchData">查询</el-button>
          <el-button type="info" plain class="ml-auto" @click="exportExcel">Excel 导出</el-button>
        </div>
      </template>

      <el-table :data="employees" v-loading="loading" border stripe height="100%">
        <el-table-column prop="employee_id" label="工号" width="150" fixed />
        <el-table-column prop="employee_name" label="姓名" width="150" />
        <el-table-column prop="total_overtime" label="累计加班时长(H)" width="150" class-name="text-primary fw-bold" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="openDetail(scope.row)">考勤明细</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog title="考勤明细" v-model="dialogVisible" width="900px">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="当月明细" name="this_month">
          <el-table :data="thisMonthData" border stripe v-loading="detailLoading" height="400px">
            <el-table-column prop="attendance_date" label="考勤日期" width="120" />
            <el-table-column prop="shift_code" label="排班班次" width="100" />
            <el-table-column prop="is_holiday" label="节假日" width="80">
              <template #default="scope">{{ scope.row.is_holiday ? '是' : '否' }}</template>
            </el-table-column>
            <el-table-column prop="actual_punch_in" label="签到时间" width="160" />
            <el-table-column prop="actual_punch_out" label="签退时间" width="160" />
            <el-table-column prop="calculated_overtime" label="加班工时(H)" width="100" class-name="fw-bold" />
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="上月明细" name="last_month">
          <el-table :data="lastMonthData" border stripe v-loading="detailLoading" height="400px">
            <el-table-column prop="attendance_date" label="考勤日期" width="120" />
            <el-table-column prop="shift_code" label="排班班次" width="100" />
            <el-table-column prop="is_holiday" label="节假日" width="80">
              <template #default="scope">{{ scope.row.is_holiday ? '是' : '否' }}</template>
            </el-table-column>
            <el-table-column prop="actual_punch_in" label="签到时间" width="160" />
            <el-table-column prop="actual_punch_out" label="签退时间" width="160" />
            <el-table-column prop="calculated_overtime" label="加班工时(H)" width="100" class-name="fw-bold" />
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const dateRange = ref<string[]>([])
const employees = ref<any[]>([])
const loading = ref(false)

const dialogVisible = ref(false)
const activeTab = ref('this_month')
const details = ref<any[]>([])
const detailLoading = ref(false)

const thisMonthData = computed(() => {
  const thisMonthStr = new Date().toISOString().slice(0, 7)
  return details.value.filter(d => d.attendance_date.startsWith(thisMonthStr))
})

const lastMonthData = computed(() => {
  const d = new Date()
  d.setMonth(d.getMonth() - 1)
  const lastMonthStr = d.toISOString().slice(0, 7)
  return details.value.filter(d => d.attendance_date.startsWith(lastMonthStr))
})

const fetchData = async () => {
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
}

const openDetail = async (row: any) => {
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
}

const exportExcel = () => {
  ElMessage.success('暂未实现纯前端导出逻辑，实际生产可对接后端模板引擎')
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.filter-bar { display: flex; align-items: center; }
.mr-10 { margin-right: 10px; }
.ml-auto { margin-left: auto; }

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

</style>
