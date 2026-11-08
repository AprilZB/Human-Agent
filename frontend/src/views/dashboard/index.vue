<template>
  <div class="dashboard-container">
    <!-- 顶部基础信息 -->
    <el-row :gutter="20" class="mb-20">
      <el-col :span="6">
        <el-card shadow="hover" class="info-card">
          <div class="info-header">所属班组</div>
          <div class="info-value">中包车间</div>
          <div class="info-desc">当前班次: 白班 (08:00 - 20:00)</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="info-card">
          <div class="info-header">人员出勤</div>
          <div class="info-value text-primary">8 / 8</div>
          <div class="info-desc">全部在岗 (出勤率 100%)</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="info-card">
          <div class="info-header">车间环境</div>
          <div class="info-value text-success">运行正常</div>
          <div class="info-desc">温度: 22°C | 湿度: 50%</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="info-card">
          <div class="info-header">设备状态</div>
          <div class="info-value text-success">全部正常</div>
          <div class="info-desc">设备运行正常</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 异常预警 -->
    <el-card shadow="hover" class="mb-20 alert-card" body-style="padding: 10px 20px; overflow: hidden;">
      <div class="alert-marquee" :class="{ 'paused': alertDetailVisible }">
        <el-icon color="#F56C6C" class="mr-10"><Warning /></el-icon>
        <span class="text-danger fw-bold">异常预警：</span>
        <span v-for="(item, index) in alerts" :key="index" class="alert-item" @click="showAlertDetail(item)">
          <span :style="{ color: item.color, fontWeight: 'bold', marginRight: '4px' }">[{{ item.type }}]</span>
          <span class="alert-content">{{ item.content }}</span>
        </span>
      </div>
    </el-card>

    <!-- 工单派工区 -->
    <el-card shadow="hover" class="work-order-card">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        
        <!-- 待派工任务 -->
        <el-tab-pane label="待派工任务" name="pending">
          <div class="filter-bar mb-20">
            <span class="mr-10">选择派工日期:</span>
            <el-date-picker
              v-model="pendingDate"
              type="date"
              placeholder="选择派工日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              @change="fetchPendingOrders"
            />
          </div>
          
          <el-table :data="pendingOrders" border stripe style="width: 100%">
            <el-table-column prop="work_order_code" label="工单号" width="160" />
            <el-table-column prop="material_code" label="产品代码" width="120" />
            <el-table-column prop="process_name" label="工序" width="100" />
            <el-table-column prop="target_quantity" label="目标数量" width="90" align="center" />
            <el-table-column prop="required_count" label="需人数" width="70" align="center" />
            <el-table-column label="系统派工建议">
              <template #default="scope">
                <el-tooltip v-for="emp in scope.row.assignments" :key="emp.employee_id" :content="emp.reason" placement="top">
                  <el-tag size="small" type="warning" class="mr-10 mb-10">
                    {{ getEmpLabel(emp.employee_id) }}
                  </el-tag>
                </el-tooltip>
                <span v-if="!scope.row.assignments || scope.row.assignments.length === 0" class="text-muted">暂无预案</span>
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="180" align="center">
              <template #default="scope">
                <el-button type="success" size="small" @click="quickConfirm(scope.row)">一键确认</el-button>
                <el-button type="primary" plain size="small" @click="openDispatchDialog(scope.row)">调配</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 已派工记录 -->
        <el-tab-pane label="已派工记录" name="dispatched">
          <div class="filter-bar mb-20">
            <span class="mr-10">选择周/日期:</span>
            <el-date-picker
              v-model="dispatchedDateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              @change="fetchDispatchedOrders"
            />
          </div>

          <el-table :data="dispatchedOrders" border stripe style="width: 100%">
            <el-table-column prop="work_order_code" label="工单号" width="160" />
            <el-table-column prop="material_code" label="产品代码" width="120" />
            <el-table-column prop="process_name" label="工序" width="100" />
            <el-table-column prop="created_at" label="生成时间" width="160" />
            <el-table-column label="已派发人员">
              <template #default="scope">
                <el-tag v-for="emp in scope.row.assignments" :key="emp.employee_id" size="small" type="success" class="mr-10 mb-10">
                  {{ getEmpLabel(emp.employee_id) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="80" align="center">
              <template #default>
                <el-tag type="success">已派发</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
      </el-tabs>
    </el-card>
    <!-- 预警详情弹窗 -->
    <el-dialog v-model="alertDetailVisible" :title="`预警详情 - ${currentAlert?.type}`" width="500px">
      <div style="line-height: 1.6; white-space: pre-wrap;">
        <p><strong>内容概览：</strong><br/>{{ currentAlert?.content }}</p>
        <p><strong>详细信息：</strong><br/>{{ currentAlert?.detail }}</p>
      </div>
      <template #footer>
        <el-button type="primary" @click="alertDetailVisible = false">知道了</el-button>
      </template>
    </el-dialog>

    <!-- 派工预览及调整弹窗 -->
    <el-dialog v-model="dialogVisible" title="人员分配预览与调整" width="600px" destroy-on-close>
      <div v-loading="matchLoading">
        <div class="mb-20 text-muted">
          当前工单: <strong>{{ currentWo?.work_order_code }}</strong> | 所需人数: <strong>{{ currentWo?.required_count }}</strong>
        </div>
        
        <el-transfer
          v-model="selectedEmployees"
          :data="allEmployees"
          :titles="['可用人员', '已派发人员']"
          filter-placeholder="请输入姓名"
          filterable
        >
          <template #default="{ option }">
            <el-tooltip :content="getAiReason(option.key)" placement="right" :disabled="!getAiReason(option.key)">
              <span>
                {{ option.label }} 
                <el-tag size="small" type="success" v-if="getAiReason(option.key)">AI推荐</el-tag>
              </span>
            </el-tooltip>
          </template>
        </el-transfer>
      </div>

      <template #footer>
        <div class="dialog-footer flex-between">
          <div class="left-actions">
            <el-button type="info" plain @click="printDispatch">打印派工单</el-button>
            <el-button type="warning" plain @click="dingtalkPush">钉钉推送</el-button>
          </div>
          <div class="right-actions">
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" @click="confirmDispatch" :disabled="matchLoading">确认派工</el-button>
          </div>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Warning } from '@element-plus/icons-vue'
import axios from 'axios'
import dayjs from 'dayjs'

const activeTab = ref('pending')

// 预警数据
const alertDetailVisible = ref(false)
const currentAlert = ref<any>(null)
const alerts = ref([
  { type: '生产', color: '#409EFF', content: '2026-09-24 中包装生产任务已下发，工位就绪', detail: '今日中包装车间下发批量生产订单，各工序物料与工位均已准备就绪，请及时确认派工。' },
  { type: '设备', color: '#67C23A', content: '中包封口机与装箱设备点检完毕，全部正常运行', detail: '设备编号：EQ-ZB-01 至 EQ-ZB-04\n早班前例行点检均符合工艺要求，处于完好在用状态。' },
  { type: '考勤', color: '#409EFF', content: '中包车间出勤8人全勤，无异常缺勤', detail: '中包间白班员工全部按时打卡签到，健康证及上岗证均在有效期内。' },
  { type: '品质', color: '#67C23A', content: '中包装灭菌装箱首件确认合格', detail: '中包装工序物料密封性与外盒标签核验合格，允许批量投产。' }
])

const showAlertDetail = (item: any) => {
  currentAlert.value = item
  alertDetailVisible.value = true
}
// 待派工数据（默认测试日期 2026-09-24）
const pendingDate = ref('2026-09-24')
const pendingOrders = ref<any[]>([])

// 已派工数据 (默认当周 2026-09-21 至 2026-09-27)
const dispatchedDateRange = ref(['2026-09-21', '2026-09-27'])
const dispatchedOrders = ref<any[]>([])

// 弹窗相关
const dialogVisible = ref(false)
const matchLoading = ref(false)
const currentWo = ref<any>(null)
const selectedEmployees = ref<string[]>([])
const aiReasons = ref<Record<string, string>>({})

// 中包车间员工数据
const allEmployees = ref([
  { key: '404201195', label: '王军 (高级工 - 中包/装箱)' },
  { key: '404245800', label: '刘端阳 (中级工 - 中包/装箱)' },
  { key: '404245815', label: '孙梦佳 (中级工 - 中包/装箱)' },
  { key: '404266762', label: '胡兰心 (中级工 - 中包/装箱)' },
  { key: '411265010', label: '李凌锋 (高级工 - 中包/装箱)' }
])

const loadEmployees = async () => {
  try {
    const res = await axios.get('/api/v1/data/employees?size=100')
    if (res.data?.records && res.data.records.length > 0) {
      allEmployees.value = res.data.records.map((e: any) => ({
        key: String(e.employee_id),
        label: `${e.name} (${Array.isArray(e.skills) ? e.skills.slice(0, 1).join(',') : (e.skills || '中包工')})`
      }))
    }
  } catch (e) {}
}

const getEmpLabel = (empId: any) => {
  const emp = allEmployees.value.find(e => String(e.key) === String(empId))
  return emp ? emp.label : empId
}

const fetchPendingOrders = async () => {
  try {
    const res = await axios.get('/api/v1/prod/work-orders?date=' + pendingDate.value + '&status=PENDING,UNASSIGNED')
    pendingOrders.value = res.data
  } catch (error) {
    ElMessage.error('拉取待派工单失败')
  }
}

const fetchDispatchedOrders = async () => {
  try {
    const [start, end] = dispatchedDateRange.value || ['', '']
    let url = '/api/v1/prod/work-orders?status=ASSIGNED'
    if (start && end) {
      url += '&start_date=' + start + '&end_date=' + end
    }
    const res = await axios.get(url)
    dispatchedOrders.value = res.data
  } catch (error) {
    ElMessage.error('拉取已派工记录失败')
  }
}

const handleTabChange = (name: string) => {
  if (name === 'pending') fetchPendingOrders()
  else if (name === 'dispatched') fetchDispatchedOrders()
}

const quickConfirm = async (wo: any) => {
  if (!wo.assignments || wo.assignments.length === 0) {
    ElMessage.warning('该工单暂无系统推荐方案，请手动调配')
    return
  }
  const emps = wo.assignments.map((a: any) => a.employee_id)
  
  try {
    await axios.post('/api/v1/prod/work-orders/' + wo.work_order_code + '/confirm-dispatch', {
      employees: emps
    })
    ElMessage.success('一键派工成功！')
    fetchPendingOrders()
  } catch (error) {
    ElMessage.error('确认派工失败')
  }
}

const openDispatchDialog = async (wo: any) => {
  currentWo.value = wo
  dialogVisible.value = true
  selectedEmployees.value = []
  aiReasons.value = {}
  
  if (wo.assignments && wo.assignments.length > 0) {
    // 使用已有的预分配方案
    wo.assignments.forEach((a: any) => {
      selectedEmployees.value.push(a.employee_id)
      aiReasons.value[a.employee_id] = a.reason
    })
  } else {
    // 若无预案则触发智能匹配
    matchLoading.value = true
    try {
      const res = await axios.post('/api/v1/prod/work-orders/' + wo.work_order_code + '/match')
      const assignments = res.data.assignments || []
      assignments.forEach((a: any) => {
        selectedEmployees.value.push(a.employee_id)
        aiReasons.value[a.employee_id] = a.reason
      })
    } catch (error) {
      ElMessage.warning('智能匹配失败，请手动分配')
    } finally {
      matchLoading.value = false
    }
  }
}

const getAiReason = (empId: string) => {
  return aiReasons.value[empId] || ''
}

const confirmDispatch = async () => {
  if (selectedEmployees.value.length === 0) {
    ElMessage.warning('至少需要指派一名员工')
    return
  }
  try {
    await axios.post('/api/v1/prod/work-orders/' + currentWo.value.work_order_code + '/confirm-dispatch', {
      employees: selectedEmployees.value
    })
    ElMessage.success('派工成功！工单已流转。')
    dialogVisible.value = false
    fetchPendingOrders()
  } catch (error) {
    ElMessage.error('确认派工失败')
  }
}

const printDispatch = () => {
  ElMessage.success('正在调用打印机...')
  setTimeout(() => window.print(), 500)
}

const dingtalkPush = async () => {
  const targetIds = selectedEmployees.value.length > 0 ? selectedEmployees.value : ['404256402', '404191243']
  const woCode = currentWo.value?.work_order_code || 'WO-13551286-01'
  try {
    const res = await axios.post('/api/v1/prod/dingtalk-push', {
      employee_ids: targetIds,
      work_order_code: woCode,
      message: '【派工提醒】您已被分配至生产任务工单：' + woCode + '，工序：中包装，请按时出勤开工。'
    })
    if (res.data.success) {
      ElMessage.success(res.data.message || '钉钉派工通知已推送！')
    } else {
      ElMessage.warning(res.data.message || '钉钉推送未完全成功')
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '钉钉推送失败')
  }
}

onMounted(() => {
  loadEmployees()
  fetchPendingOrders()
})
</script>

<style scoped>
.dashboard-container {
  height: 100%;
}
.info-card {
  text-align: center;
  background-color: var(--bg-card);
  border: none;
}
.info-header {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 10px;
}
.info-value {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 10px;
}
.info-desc {
  font-size: 12px;
  color: var(--text-secondary);
}
.text-primary { color: #409EFF; }
.text-success { color: #67C23A; }
.text-warning { color: #E6A23C; }
.text-danger { color: #F56C6C; }
.fw-bold { font-weight: bold; }
.mb-20 { margin-bottom: 20px; }
.mr-10 { margin-right: 10px; }
.mb-10 { margin-bottom: 10px; }
.text-muted { color: #909399; font-size: 14px; }

.alert-card {
  border-left: 4px solid #F56C6C;
}
.alert-marquee {
  display: flex;
  align-items: center;
  white-space: nowrap;
  overflow: hidden;
  animation: marquee 40s linear infinite;
}
.alert-marquee:hover, .alert-marquee.paused {
  animation-play-state: paused;
}
.alert-item {
  margin-right: 30px;
  color: #606266;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
}
.alert-content:hover {
  text-decoration: underline;
  color: #409EFF;
}
@keyframes marquee {
  0% { transform: translateX(50%); }
  100% { transform: translateX(-100%); }
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.filter-bar {
  display: flex;
  align-items: center;
}

@media print {
  body * {
    visibility: hidden;
  }
  .el-dialog, .el-dialog * {
    visibility: visible;
  }
  .el-dialog {
    position: absolute;
    left: 0;
    top: 0;
    width: 100% !important;
  }
}
</style>
