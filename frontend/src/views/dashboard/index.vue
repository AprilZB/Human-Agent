<template>
  <div class="dashboard-container">
    <!-- 顶部基础信息 -->
    <el-row :gutter="20" class="mb-20">
      <el-col :span="6">
        <el-card shadow="hover" class="info-card">
          <div class="info-header">所属班组</div>
          <div class="info-value">冲压一班</div>
          <div class="info-desc">当前班次: 早班 (08:00 - 16:00)</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="info-card">
          <div class="info-header">人员出勤</div>
          <div class="info-value text-primary">18 / 20</div>
          <div class="info-desc">2人请假/缺勤</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="info-card">
          <div class="info-header">车间环境</div>
          <div class="info-value text-success">运行正常</div>
          <div class="info-desc">温度: 24°C | 湿度: 55%</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="info-card">
          <div class="info-header">设备状态</div>
          <div class="info-value text-warning">9 / 10</div>
          <div class="info-desc">1台设备正在维保</div>
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
  { type: '超时', color: '#F56C6C', content: '张三本周加班已超规定时长', detail: '员工张三 (EMP001) 本周累计加班达到 38 小时，超过了车间规定的单周 36 小时上限。为了员工身心健康与合规，已将其从本周候选名单中暂时移除，建议班组长关注。' },
  { type: '设备', color: '#E6A23C', content: '冲压机#03 需要例行保养', detail: '设备编号：EQ-P-03\n下次保养日期应为今日。当前状态可能影响加工精度，请及时联系设备科或提交保养工单。' },
  { type: '生产', color: '#409EFF', content: '存在1笔紧急插单任务待处理', detail: '工单号：WO-URGENT-001\n客户要求在明日前完成交付。该单已进入加急队列，请优先派工。' },
  { type: '品质', color: '#F56C6C', content: 'A工序昨日出现轻微尺寸偏移', detail: '涉及批次：LOT-20260907\n质检部反馈昨日的冲压件存在 0.02mm 的尺寸公差偏移，建议今天开工前重新校准模具。' }
])

const showAlertDetail = (item: any) => {
  currentAlert.value = item
  alertDetailVisible.value = true
}
// 待派工数据
const pendingDate = ref(dayjs().format('YYYY-MM-DD'))
const pendingOrders = ref<any[]>([])

// 已派工数据 (默认当周)
const startOfWeek = dayjs().startOf('week').add(1, 'day').format('YYYY-MM-DD') // 周一
const endOfWeek = dayjs().endOf('week').add(1, 'day').format('YYYY-MM-DD')     // 周日
const dispatchedDateRange = ref([startOfWeek, endOfWeek])
const dispatchedOrders = ref<any[]>([])

// 弹窗相关
const dialogVisible = ref(false)
const matchLoading = ref(false)
const currentWo = ref<any>(null)
const selectedEmployees = ref<string[]>([])
const aiReasons = ref<Record<string, string>>({})

// 模拟的班组全体员工数据
const allEmployees = ref([
  { key: 'EMP001', label: '张三 (高级工)' },
  { key: 'EMP002', label: '李四 (中级工)' },
  { key: 'EMP003', label: '王五 (初级工)' },
  { key: 'EMP004', label: '赵六 (高级工)' },
  { key: 'EMP005', label: '钱七 (学徒)' },
  { key: 'EMP006', label: '孙八 (中级工)' }
])

const getEmpLabel = (empId: string) => {
  const emp = allEmployees.value.find(e => e.key === empId)
  return emp ? emp.label : empId
}

const fetchPendingOrders = async () => {
  try {
    const res = await axios.get('http://localhost:8100/api/v1/prod/work-orders?date=' + pendingDate.value + '&status=PENDING,UNASSIGNED')
    pendingOrders.value = res.data
  } catch (error) {
    ElMessage.error('拉取待派工单失败')
  }
}

const fetchDispatchedOrders = async () => {
  try {
    const [start, end] = dispatchedDateRange.value || ['', '']
    let url = 'http://localhost:8100/api/v1/prod/work-orders?status=ASSIGNED'
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
    await axios.post('http://localhost:8100/api/v1/prod/work-orders/' + wo.work_order_code + '/confirm-dispatch', {
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
      const res = await axios.post('http://localhost:8100/api/v1/prod/work-orders/' + wo.work_order_code + '/match')
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
    await axios.post('http://localhost:8100/api/v1/prod/work-orders/' + currentWo.value.work_order_code + '/confirm-dispatch', {
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
  try {
    await axios.post('http://localhost:8100/api/v1/prod/dingtalk-push', {
      phone: '15957270693',
      message: '【派工提醒】您被分配到了工单：' + currentWo.value?.work_order_code
    })
    ElMessage.success('钉钉消息已推送到 15957270693')
  } catch (error) {
    ElMessage.error('钉钉推送失败')
  }
}

onMounted(() => {
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
  animation: marquee 20s linear infinite;
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
