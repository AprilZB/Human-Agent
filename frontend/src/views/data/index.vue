<template>
  <div class="data-container">
    <el-card shadow="hover" class="data-card">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        
        <!-- 物料档案 -->
        <el-tab-pane label="物料档案" name="materials">
          <div class="filter-bar">
            <el-input v-model="filters.materials" placeholder="物料编码/描述" style="width: 200px" class="mr-10" />
            <el-button type="primary" @click="fetchData">查询</el-button>
            <el-button type="warning" plain class="mr-10" @click="handleDownloadTemplate(activeTab)">下载导入模板</el-button>
            <el-upload :action="'/api/v1/data/materials/import'" :show-file-list="false" :on-success="handleImportSuccess" :on-error="handleImportError" class="ml-auto mr-10">
              <el-button type="success" plain>Excel 导入</el-button>
            </el-upload>
            <el-button type="info" plain @click="handleExport('materials')">Excel 导出</el-button>
          </div>
          <el-table :data="tableData.materials" v-loading="loading" border stripe height="calc(100vh - 300px)">
            <el-table-column prop="material_code" label="物料编码" width="150" fixed />
            <el-table-column prop="material_desc" label="物料描述" width="200" fixed />
            <el-table-column prop="material_group_code" label="物料组" width="120" />
            <el-table-column prop="plant_status" label="特定工厂状态" width="120" />
            <el-table-column prop="base_uom" label="基本计量单位" width="120" />
            <el-table-column prop="valid_from" label="有效起始期" width="120" />
            <el-table-column prop="max_storage_period" label="最大存储期间" width="120" />
            <el-table-column prop="time_unit" label="时间单位" width="100" />
            <el-table-column prop="min_shelf_life" label="最小剩余货架寿命" width="140" />
            <el-table-column prop="total_shelf_life" label="总货架寿命" width="120" />
            <el-table-column prop="inspection_required" label="是否需检验" width="100">
              <template #default="scope">{{ scope.row.inspection_required ? '是' : '否' }}</template>
            </el-table-column>
            <el-table-column prop="safety_stock" label="安全库存" width="100" />
            <el-table-column prop="default_storage_loc" label="默认地点" width="100" />
          </el-table>
          <div class="pagination-container">
            <el-pagination v-model:current-page="pages.materials" :total="totals.materials" layout="total, prev, pager, next" @current-change="fetchData" />
          </div>
        </el-tab-pane>

        <!-- 生产订单记录 -->
        <el-tab-pane label="生产订单记录" name="production-orders">
          <div class="filter-bar">
            <el-input v-model="filters['production-orders']" placeholder="单号/物料" style="width: 200px" class="mr-10" />
            <el-button type="primary" @click="fetchData">查询</el-button>
            <el-button type="warning" plain class="mr-10" @click="handleDownloadTemplate(activeTab)">下载导入模板</el-button>
            <el-upload :action="'/api/v1/data/production-orders/import'" :show-file-list="false" :on-success="handleImportSuccess" :on-error="handleImportError" class="ml-auto mr-10">
              <el-button type="success" plain>Excel 导入</el-button>
            </el-upload>
            <el-button type="info" plain @click="handleExport('production-orders')">Excel 导出</el-button>
          </div>
          <el-table :data="tableData['production-orders']" v-loading="loading" border stripe height="calc(100vh - 300px)">
            <el-table-column prop="order_code" label="订单编号" width="180" />
            <el-table-column prop="material_code" label="物料编码" width="150" />
            <el-table-column prop="target_quantity" label="目标数量" width="120" />
            <el-table-column prop="plan_start_time" label="计划开始" width="160" />
            <el-table-column prop="plan_end_time" label="计划结束" width="160" />
            <el-table-column prop="status" label="状态" width="120" />
          </el-table>
          <div class="pagination-container">
            <el-pagination v-model:current-page="pages['production-orders']" :total="totals['production-orders']" layout="total, prev, pager, next" @current-change="fetchData" />
          </div>
        </el-tab-pane>
        
        <!-- 确认报工记录 -->
        <el-tab-pane label="确认报工记录" name="confirmations">
          <div class="filter-bar">
            <el-input v-model="filters.confirmations" placeholder="订单号/物料" style="width: 200px" class="mr-10" />
            <el-button type="primary" @click="fetchData">查询</el-button>
            <el-button type="warning" plain class="mr-10" @click="handleDownloadTemplate(activeTab)">下载导入模板</el-button>
            <el-upload :action="'/api/v1/data/confirmations/import'" :show-file-list="false" :on-success="handleImportSuccess" :on-error="handleImportError" class="ml-auto mr-10">
              <el-button type="success" plain>Excel 导入</el-button>
            </el-upload>
            <el-button type="info" plain @click="handleExport('confirmations')">Excel 导出</el-button>
          </div>
          <el-table :data="tableData.confirmations" v-loading="loading" border stripe height="calc(100vh - 300px)">
            <el-table-column prop="id" label="ID" width="80" fixed />
            <el-table-column prop="order_code" label="生产订单号" width="150" fixed />
            <el-table-column prop="material_code" label="物料编码" width="120" />
            <el-table-column prop="work_center_code" label="工作中心" width="120" />
            <el-table-column prop="batch_no" label="批次号" width="120" />
            <el-table-column prop="yield_quantity" label="产量" width="100" />
            <el-table-column prop="scrap_quantity" label="报废数量" width="100" />
            <el-table-column prop="confirmation_no" label="确认单号" width="120" />
            <el-table-column prop="plant" label="工厂" width="100" />
            <el-table-column prop="exec_datetime" label="执行时间" width="160" />
            <el-table-column prop="cancel_flag" label="取消标志" width="100" />
            <el-table-column prop="reversed_flag" label="冲销标志" width="100" />
          </el-table>
          <div class="pagination-container">
            <el-pagination v-model:current-page="pages.confirmations" :total="totals.confirmations" layout="total, prev, pager, next" @current-change="fetchData" />
          </div>
        </el-tab-pane>

        <!-- 员工档案 -->
        <el-tab-pane label="员工档案" name="employees">
          <div class="filter-bar">
            <el-input v-model="filters.employees" placeholder="工号/姓名" style="width: 200px" class="mr-10" />
            <el-button type="primary" @click="fetchData">查询</el-button>
            <el-button type="warning" plain class="mr-10" @click="handleDownloadTemplate(activeTab)">下载导入模板</el-button>
            <el-upload :action="'/api/v1/data/employees/import'" :show-file-list="false" :on-success="handleImportSuccess" :on-error="handleImportError" class="ml-auto mr-10">
              <el-button type="success" plain>Excel 导入</el-button>
            </el-upload>
            <el-button type="info" plain @click="handleExport('employees')">Excel 导出</el-button>
          </div>
          <el-table :data="tableData.employees" v-loading="loading" border stripe height="calc(100vh - 300px)">
            <el-table-column prop="employee_id" label="工号" width="150" />
            <el-table-column prop="name" label="姓名" width="150" />
            <el-table-column prop="workshop_code" label="车间" width="150" />
            <el-table-column prop="health_cert_status" label="健康证状态/有效期" width="180" />
            <el-table-column prop="work_cert_status" label="上岗证状态/有效期" width="180" />
            <el-table-column prop="skills" label="技能矩阵" />
          </el-table>
          <div class="pagination-container">
            <el-pagination v-model:current-page="pages.employees" :total="totals.employees" layout="total, prev, pager, next" @current-change="fetchData" />
          </div>
        </el-tab-pane>

        
        <!-- 出勤排班记录 -->
        <el-tab-pane label="出勤排班记录" name="attendances">
          <div class="filter-bar">
            <el-input v-model="filters.attendances" placeholder="工号" style="width: 200px" class="mr-10" />
            <el-button type="primary" @click="fetchData">查询</el-button>
            <el-button type="warning" plain class="mr-10" @click="handleDownloadTemplate(activeTab)">下载导入模板</el-button>
            <el-upload :action="'/api/v1/data/attendances/import'" :show-file-list="false" :on-success="handleImportSuccess" :on-error="handleImportError" class="ml-auto mr-10">
              <el-button type="success" plain>Excel 导入</el-button>
            </el-upload>
            <el-button type="info" plain @click="handleExport('attendances')">Excel 导出</el-button>
          </div>
          <el-table :data="tableData.attendances" v-loading="loading" border stripe height="calc(100vh - 300px)">
            <el-table-column prop="id" label="ID" width="80" fixed />
            <el-table-column prop="attendance_date" label="考勤日期" width="120" fixed />
            <el-table-column prop="employee_id" label="工号" width="120" />
            <el-table-column prop="shift_code" label="排班班次" width="120" />
            <el-table-column prop="is_holiday" label="是否节假日" width="100">
              <template #default="scope">{{ scope.row.is_holiday ? '是' : '否' }}</template>
            </el-table-column>
            <el-table-column prop="actual_punch_in" label="实际签到" width="160" />
            <el-table-column prop="actual_punch_out" label="实际签退" width="160" />
            <el-table-column prop="attendance_status" label="考勤状态" width="120" />
            <el-table-column prop="calculated_overtime" label="核算加班(H)" width="120" />
          </el-table>
          <div class="pagination-container">
            <el-pagination v-model:current-page="pages.attendances" :total="totals.attendances" layout="total, prev, pager, next" @current-change="fetchData" />
          </div>
        </el-tab-pane>

        <!-- 车间档案 -->
        <el-tab-pane label="车间档案" name="workshops">
          <div class="filter-bar">
            <el-button type="primary" @click="fetchData">刷新</el-button>
            <el-button type="warning" plain class="mr-10" @click="handleDownloadTemplate(activeTab)">下载导入模板</el-button>
            <el-upload :action="'/api/v1/data/workshops/import'" :show-file-list="false" :on-success="handleImportSuccess" :on-error="handleImportError" class="ml-auto mr-10">
              <el-button type="success" plain>Excel 导入</el-button>
            </el-upload>
            <el-button type="info" plain @click="handleExport('workshops')">Excel 导出</el-button>
          </div>
          <el-table :data="tableData.workshops" v-loading="loading" border stripe height="calc(100vh - 300px)">
            <el-table-column prop="workshop_code" label="车间编码" width="150" />
            <el-table-column prop="workshop_name" label="车间名称" width="200" />
            <el-table-column prop="sap_work_center_code" label="SAP工作中心对照" />
            <el-table-column prop="manager_id" label="负责人ID" width="150" />
          </el-table>
          <div class="pagination-container">
            <el-pagination v-model:current-page="pages.workshops" :total="totals.workshops" layout="total, prev, pager, next" @current-change="fetchData" />
          </div>
        </el-tab-pane>

        <!-- 不良原因档案 -->
        <el-tab-pane label="不良原因档案" name="defect-reasons">
          <div class="filter-bar">
            <el-button type="primary" @click="fetchData">刷新</el-button>
            <el-button type="warning" plain class="mr-10" @click="handleDownloadTemplate(activeTab)">下载导入模板</el-button>
            <el-upload :action="'/api/v1/data/defect-reasons/import'" :show-file-list="false" :on-success="handleImportSuccess" :on-error="handleImportError" class="ml-auto mr-10">
              <el-button type="success" plain>Excel 导入</el-button>
            </el-upload>
            <el-button type="info" plain @click="handleExport('defect-reasons')">Excel 导出</el-button>
          </div>
          <el-table :data="tableData['defect-reasons']" v-loading="loading" border stripe height="calc(100vh - 300px)">
            <el-table-column prop="defect_code" label="本地不良代码" width="150" />
            <el-table-column prop="sap_defect_code" label="SAP不良代码" width="150" />
            <el-table-column prop="defect_name" label="不良名称" width="200" />
            <el-table-column prop="description" label="描述" />
          </el-table>
          <div class="pagination-container">
            <el-pagination v-model:current-page="pages['defect-reasons']" :total="totals['defect-reasons']" layout="total, prev, pager, next" @current-change="fetchData" />
          </div>
        </el-tab-pane>

        <!-- 物料组档案 -->
        <el-tab-pane label="物料组档案" name="material-groups">
          <div class="filter-bar">
            <el-button type="primary" @click="fetchData">刷新</el-button>
            <el-button type="warning" plain class="mr-10" @click="handleDownloadTemplate(activeTab)">下载导入模板</el-button>
            <el-upload :action="'/api/v1/data/material-groups/import'" :show-file-list="false" :on-success="handleImportSuccess" :on-error="handleImportError" class="ml-auto mr-10">
              <el-button type="success" plain>Excel 导入</el-button>
            </el-upload>
            <el-button type="info" plain @click="handleExport('material-groups')">Excel 导出</el-button>
          </div>
          <el-table :data="tableData['material-groups']" v-loading="loading" border stripe height="calc(100vh - 300px)">
            <el-table-column prop="group_code" label="本地物料组编码" width="150" />
            <el-table-column prop="sap_group_code" label="SAP对照码" width="150" />
            <el-table-column prop="group_name" label="物料组名称" />
          </el-table>
          <div class="pagination-container">
            <el-pagination v-model:current-page="pages['material-groups']" :total="totals['material-groups']" layout="total, prev, pager, next" @current-change="fetchData" />
          </div>
        </el-tab-pane>

        <!-- 工艺路线档案 -->
        <el-tab-pane label="工艺路线档案" name="routings">
          <div class="filter-bar">
            <el-button type="primary" @click="fetchData">刷新</el-button>
            <el-button type="warning" plain class="mr-10" @click="handleDownloadTemplate(activeTab)">下载导入模板</el-button>
            <el-upload :action="'/api/v1/data/routings/import'" :show-file-list="false" :on-success="handleImportSuccess" :on-error="handleImportError" class="ml-auto mr-10">
              <el-button type="success" plain>Excel 导入</el-button>
            </el-upload>
            <el-button type="info" plain @click="handleExport('routings')">Excel 导出</el-button>
          </div>
          <el-table :data="tableData.routings" v-loading="loading" border stripe height="calc(100vh - 300px)">
            <el-table-column prop="routing_code" label="路线编码" width="150" />
            <el-table-column prop="sap_routing_code" label="SAP对照码" width="150" />
            <el-table-column prop="routing_name" label="路线名称" width="200" />
            <el-table-column prop="material_code" label="关联物料" width="150" />
            <el-table-column prop="version" label="版本" width="100" />
          </el-table>
          <div class="pagination-container">
            <el-pagination v-model:current-page="pages.routings" :total="totals.routings" layout="total, prev, pager, next" @current-change="fetchData" />
          </div>
        </el-tab-pane>

        <!-- 工序档案 -->
        <el-tab-pane label="工序档案" name="processes">
          <div class="filter-bar">
            <el-button type="primary" @click="fetchData">刷新</el-button>
            <el-button type="warning" plain class="mr-10" @click="handleDownloadTemplate(activeTab)">下载导入模板</el-button>
            <el-upload :action="'/api/v1/data/processes/import'" :show-file-list="false" :on-success="handleImportSuccess" :on-error="handleImportError" class="ml-auto mr-10">
              <el-button type="success" plain>Excel 导入</el-button>
            </el-upload>
            <el-button type="info" plain @click="handleExport('processes')">Excel 导出</el-button>
          </div>
          <el-table :data="tableData.processes" v-loading="loading" border stripe height="calc(100vh - 300px)">
            <el-table-column prop="process_code" label="工序代码" width="150" />
            <el-table-column prop="process_name" label="工序名称" width="200" />
            <el-table-column prop="standard_time_sec" label="标准工时(秒)" width="150" />
            <el-table-column prop="required_skills" label="所需技能" />
            <el-table-column prop="bound_bom_code" label="绑定BOM" width="150" />
          </el-table>
          <div class="pagination-container">
            <el-pagination v-model:current-page="pages.processes" :total="totals.processes" layout="total, prev, pager, next" @current-change="fetchData" />
          </div>
        </el-tab-pane>

        <!-- BOM档案 -->
        <el-tab-pane label="BOM档案" name="boms">
          <div class="filter-bar">
            <el-button type="primary" @click="fetchData">刷新</el-button>
            <el-button type="warning" plain class="mr-10" @click="handleDownloadTemplate(activeTab)">下载导入模板</el-button>
            <el-upload :action="'/api/v1/data/boms/import'" :show-file-list="false" :on-success="handleImportSuccess" :on-error="handleImportError" class="ml-auto mr-10">
              <el-button type="success" plain>Excel 导入</el-button>
            </el-upload>
            <el-button type="info" plain @click="handleExport('boms')">Excel 导出</el-button>
          </div>
          <el-table :data="tableData.boms" v-loading="loading" border stripe height="calc(100vh - 300px)">
            <el-table-column prop="bom_code" label="BOM编码" width="150" />
            <el-table-column prop="product_code" label="父件编码" width="150" />
            <el-table-column prop="component_code" label="子件编码" width="150" />
            <el-table-column prop="quantity" label="用量" width="100" />
            <el-table-column prop="alt_group" label="替代物料同行号" width="150" />
          </el-table>
          <div class="pagination-container">
            <el-pagination v-model:current-page="pages.boms" :total="totals.boms" layout="total, prev, pager, next" @current-change="fetchData" />
          </div>
        </el-tab-pane>

      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const activeTab = ref('materials')
const loading = ref(false)

const tabs = [
  'materials', 'production-orders', 'confirmations', 'employees', 'workshops', 
  'defect-reasons', 'material-groups', 'routings', 'processes', 'boms', 'attendances'
]

const tableData = reactive<Record<string, any[]>>({})
const pages = reactive<Record<string, number>>({})
const totals = reactive<Record<string, number>>({})
const filters = reactive<Record<string, string>>({})

tabs.forEach(t => {
  tableData[t] = []
  pages[t] = 1
  totals[t] = 0
  filters[t] = ''
})

const fetchData = async () => {
  loading.value = true
  const tab = activeTab.value
  try {
    const res = await axios.get('/api/v1/data/' + tab, {
      params: {
        page: pages[tab],
        size: 10,
        keyword: filters[tab] || ''
      }
    })
    tableData[tab] = res.data.records
    totals[tab] = res.data.total
  } catch (error) {
    ElMessage.error('拉取数据失败')
  } finally {
    loading.value = false
  }
}

const handleTabChange = () => {
  fetchData()
}

const handleDownloadTemplate = (tab: string) => {
  window.open('/api/v1/data/' + tab + '/export?template=1')
}

const handleExport = (tab: string) => {
  window.open('/api/v1/data/' + tab + '/export')
}

const handleImportSuccess = (res: any) => {
  if (res.error) {
    ElMessage.error(res.error)
  } else {
    ElMessage.success('导入成功，处理条数：' + res.count)
    fetchData()
  }
}

const handleImportError = () => {
  ElMessage.error('网络或服务器异常，导入失败')
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.data-container {
  height: 100%;
}
.data-card {
  height: 100%;
}
.filter-bar {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}
.mr-10 { margin-right: 10px; }
.ml-auto { margin-left: auto; }
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
:deep(.el-card__body) {
  height: 100%;
  display: flex;
  flex-direction: column;
}
:deep(.el-tabs) {
  flex: 1;
  display: flex;
  flex-direction: column;
}
:deep(.el-tabs__content) {
  flex: 1;
  overflow: auto;
}
</style>
