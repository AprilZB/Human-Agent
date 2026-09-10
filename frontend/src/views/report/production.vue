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
          <el-input v-model="productCode" placeholder="物料编码" style="width: 150px" class="mr-10" />
          <el-button type="primary" @click="fetchData">查询</el-button>
          <el-button type="info" plain class="ml-auto" @click="exportExcel">Excel 导出</el-button>
        </div>
      </template>

      <el-table :data="orders" v-loading="loading" border stripe height="100%">
        <el-table-column prop="order_code" label="生产订单号" width="150" fixed />
        <el-table-column prop="material_code" label="物料编码" width="150" />
        <el-table-column prop="workshop_code" label="车间(产线)" width="120" />
        <el-table-column prop="scheduled_start_date" label="计划开始" width="120" />
        <el-table-column prop="target_quantity" label="计划产量" width="100" />
        <el-table-column prop="total_completed" label="报工良品" width="100" class-name="text-success fw-bold" />
        <el-table-column prop="total_scrap" label="报工废品" width="100" class-name="text-danger" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="openDetail(scope.row)">明细记录</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog title="报工明细" v-model="dialogVisible" width="800px">
      <el-table :data="details" border stripe v-loading="detailLoading">
        <el-table-column prop="confirmation_code" label="确认单号" width="120" />
        <el-table-column prop="employee_id" label="报工人员" width="100" />
        <el-table-column prop="actual_date" label="执行日期" width="120" />
        <el-table-column prop="yield_quantity" label="合格数量" width="100" />
        <el-table-column prop="scrap_quantity" label="报废数量" width="100" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const dateRange = ref<string[]>([])
const productCode = ref('')
const orders = ref<any[]>([])
const loading = ref(false)

const dialogVisible = ref(false)
const details = ref<any[]>([])
const detailLoading = ref(false)

const fetchData = async () => {
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
}

const openDetail = async (row: any) => {
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
