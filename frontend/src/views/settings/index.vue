<template>
  <div class="settings-container">
    <el-card shadow="hover" class="settings-card">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <!-- Tab 1: APHR 人事系统对接与同步 (优先突出) -->
        <el-tab-pane label="人事系统 (APHR) 对接与同步" name="aphr">
          <!-- 顶部状态卡片行 -->
          <el-row :gutter="16" class="mb-16">
            <el-col :span="8">
              <el-card shadow="never" class="status-card">
                <template #header>
                  <div class="card-header-flex">
                    <span class="font-bold">APHR 接口连接状态</span>
                    <el-tag :type="connStatus.tested ? (connStatus.success ? 'success' : 'danger') : 'info'" size="small">
                      {{ connStatus.tested ? (connStatus.success ? '连通正常' : '连接失败') : '未测试' }}
                    </el-tag>
                  </div>
                </template>
                <div class="status-metric">
                  <div class="metric-item">
                    <span class="metric-label">接口地址：</span>
                    <span class="metric-val text-ellipsis" :title="aphrForm.APHR_BASE_URL">{{ aphrForm.APHR_BASE_URL }}</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">响应延迟：</span>
                    <span class="metric-val">{{ connStatus.tested && connStatus.success ? `${connStatus.latency_ms} ms` : '-' }}</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">APHR 员工库总数：</span>
                    <span class="metric-val text-blue font-bold">{{ connStatus.tested && connStatus.success ? `${connStatus.total_employees} 人` : '-' }}</span>
                  </div>
                </div>
                <div class="card-actions">
                  <el-button type="primary" plain size="small" :loading="testLoading" @click="handleTestConnection">测试连接</el-button>
                </div>
              </el-card>
            </el-col>

            <el-col :span="8">
              <el-card shadow="never" class="status-card">
                <template #header>
                  <div class="card-header-flex">
                    <span class="font-bold">定时同步调度器</span>
                    <el-tag :type="aphrForm.APHR_SYNC_ENABLED ? 'success' : 'warning'" size="small">
                      {{ aphrForm.APHR_SYNC_ENABLED ? '自动同步运行中' : '已暂停' }}
                    </el-tag>
                  </div>
                </template>
                <div class="status-metric">
                  <div class="metric-item">
                    <span class="metric-label">自动同步开关：</span>
                    <el-switch v-model="aphrForm.APHR_SYNC_ENABLED" active-text="开启" inactive-text="关闭" @change="handleSaveConfig(false)" />
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">同步周期：</span>
                    <span class="metric-val">每 {{ aphrForm.APHR_SYNC_INTERVAL_MIN }} 分钟</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">下次自动同步：</span>
                    <span class="metric-val text-gray">{{ schedulerNextRun || '暂未计划' }}</span>
                  </div>
                </div>
                <div class="card-actions">
                  <el-button type="success" size="small" :loading="syncLoading" @click="handleManualSync">立即同步</el-button>
                </div>
              </el-card>
            </el-col>

            <el-col :span="8">
              <el-card shadow="never" class="status-card">
                <template #header>
                  <div class="card-header-flex">
                    <span class="font-bold">最近同步记录</span>
                    <el-tag :type="lastReport.status === 'SUCCESS' ? 'success' : (lastReport.status === 'FAILED' ? 'danger' : 'info')" size="small">
                      {{ lastReport.status === 'SUCCESS' ? '同步成功' : (lastReport.status === 'FAILED' ? '同步失败' : '无记录') }}
                    </el-tag>
                  </div>
                </template>
                <div class="status-metric">
                  <div class="metric-item">
                    <span class="metric-label">执行时间：</span>
                    <span class="metric-val">{{ aphrForm.APHR_LAST_SYNC_TIME || '-' }}</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">拉取统计：</span>
                    <span class="metric-val">
                      抓取 <b>{{ lastReport.total_fetched || 0 }}</b> | 
                      新增 <b class="text-green">{{ lastReport.inserted || 0 }}</b> | 
                      更新 <b class="text-blue">{{ lastReport.updated || 0 }}</b>
                    </span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">执行耗时：</span>
                    <span class="metric-val">{{ lastReport.duration_sec ? `${lastReport.duration_sec} 秒` : '-' }}</span>
                  </div>
                </div>
                <div class="card-actions">
                  <el-button type="info" plain size="small" @click="fetchAphrEmployees">刷新员工列表</el-button>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <!-- 中部：对接连接与同步配置表单 -->
          <el-card shadow="never" class="mb-16">
            <template #header>
              <div class="card-header-flex">
                <span class="font-bold">APHR 接口连接与同步配置</span>
                <el-button type="primary" size="small" :loading="saveLoading" @click="handleSaveConfig(true)">保存配置</el-button>
              </div>
            </template>
            <el-form :model="aphrForm" label-width="120px">
              <el-row :gutter="20">
                <el-col :span="8">
                  <el-form-item label="APHR 接口地址">
                    <el-input v-model="aphrForm.APHR_BASE_URL" placeholder="http://10.11.100.151:8092" />
                  </el-form-item>
                </el-col>
                <el-col :span="5">
                  <el-form-item label="接口账号">
                    <el-input v-model="aphrForm.APHR_USERNAME" placeholder="admin" />
                  </el-form-item>
                </el-col>
                <el-col :span="5">
                  <el-form-item label="接口密钥">
                    <el-input v-model="aphrForm.APHR_PASSWORD" type="password" show-password placeholder="admin123" />
                  </el-form-item>
                </el-col>
                <el-col :span="6">
                  <el-form-item label="定时同步周期">
                    <el-select v-model="aphrForm.APHR_SYNC_INTERVAL_MIN" placeholder="选择周期" style="width: 100%">
                      <el-option label="每 15 分钟" value="15" />
                      <el-option label="每 30 分钟" value="30" />
                      <el-option label="每 60 分钟 (推荐)" value="60" />
                      <el-option label="每 2 小时" value="120" />
                      <el-option label="每 12 小时" value="720" />
                      <el-option label="每天一次 (24 小时)" value="1440" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </el-card>

          <!-- 底部：已同步员工数据看板 -->
          <el-card shadow="never">
            <template #header>
              <div class="card-header-flex">
                <span class="font-bold">系统内已同步员工基础数据 (共 {{ empTotal }} 人)</span>
                <div class="search-box">
                  <el-input v-model="empKeyword" placeholder="输入工号 / 姓名 / 车间过滤" clearable style="width: 250px" class="mr-10" @keyup.enter="fetchAphrEmployees" />
                  <el-button type="primary" size="small" @click="fetchAphrEmployees">查询</el-button>
                </div>
              </div>
            </template>
            <el-table :data="empList" v-loading="empLoading" border stripe style="width: 100%" height="320px">
              <el-table-column prop="employee_id" label="员工工号" width="140" fixed />
              <el-table-column prop="name" label="姓名" width="120" fixed />
              <el-table-column prop="workshop_code" label="所属车间" width="130">
                <template #default="scope">
                  <el-tag size="small" :type="scope.row.workshop_code ? 'success' : 'info'">{{ scope.row.workshop_code || '未设置' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="skills" label="技能矩阵">
                <template #default="scope">
                  <el-tag v-for="s in scope.row.skills" :key="s" size="small" class="mr-5">{{ s }}</el-tag>
                  <span v-if="!scope.row.skills || scope.row.skills.length === 0" style="color: #909399; font-size: 12px">暂无技能</span>
                </template>
              </el-table-column>
              <el-table-column prop="health_cert_status" label="健康证状态" width="120">
                <template #default="scope">
                  <el-tag size="small" :type="scope.row.health_cert_status === '有效' ? 'success' : 'danger'">
                    {{ scope.row.health_cert_status || '未知' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="work_cert_status" label="上岗证状态" width="120">
                <template #default="scope">
                  <el-tag size="small" :type="scope.row.work_cert_status === '有效' ? 'success' : 'warning'">
                    {{ scope.row.work_cert_status || '未知' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="入库/同步时间" width="180" />
            </el-table>
            <div class="pagination-box">
              <el-pagination v-model:current-page="empPage" v-model:page-size="empSize" :total="empTotal" layout="total, prev, pager, next" @current-change="fetchAphrEmployees" />
            </div>
          </el-card>
        </el-tab-pane>

        <!-- Tab 2: 全局系统参数 -->
        <el-tab-pane label="全局系统参数" name="params">
          <div class="header">
            <el-button type="primary" @click="fetchConfigs">刷新配置</el-button>
          </div>
          <el-table :data="configs" v-loading="loading" border stripe>
            <el-table-column prop="config_key" label="配置项 (Key)" width="250" />
            <el-table-column label="配置值 (Value)">
              <template #default="scope">
                <el-input v-model="scope.row.config_value" @change="saveConfig(scope.row)" />
              </template>
            </el-table-column>
            <el-table-column prop="description" label="说明" />
          </el-table>
        </el-tab-pane>

        <!-- Tab 3: 考勤规则配置 -->
        <el-tab-pane label="考勤规则配置" name="attendance">
          <div class="header">
            <el-button type="primary" @click="openAddRuleDialog">新增班次规则</el-button>
            <el-button type="success" plain @click="fetchRules">刷新规则</el-button>
          </div>
          <el-table :data="rules" v-loading="loading" border stripe>
            <el-table-column prop="shift_code" label="班次代码" width="120" />
            <el-table-column prop="shift_name" label="班次名称" width="150" />
            <el-table-column prop="start_time" label="上班时间" width="100" />
            <el-table-column prop="end_time" label="下班时间" width="100" />
            <el-table-column prop="is_cross_day" label="是否跨天" width="100">
              <template #default="scope">{{ scope.row.is_cross_day ? '是' : '否' }}</template>
            </el-table-column>
            <el-table-column prop="meal_break_hours" label="扣除就餐(小时)" width="120" />
            <el-table-column prop="standard_work_hours" label="标准工时(小时)" width="120" />
            <el-table-column prop="is_overtime_counted" label="计入加班" width="100">
              <template #default="scope">{{ scope.row.is_overtime_counted ? '是' : '否' }}</template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="scope">
                <el-button type="primary" link @click="editRule(scope.row)">编辑</el-button>
                <el-button type="danger" link @click="deleteRule(scope.row.shift_code)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 考勤规则新增/编辑弹窗 -->
    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="500px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="班次代码">
          <el-input v-model="form.shift_code" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="班次名称">
          <el-input v-model="form.shift_name" />
        </el-form-item>
        <el-form-item label="上班时间">
          <el-time-picker v-model="form.start_time" format="HH:mm:ss" value-format="HH:mm:ss" />
        </el-form-item>
        <el-form-item label="下班时间">
          <el-time-picker v-model="form.end_time" format="HH:mm:ss" value-format="HH:mm:ss" />
        </el-form-item>
        <el-form-item label="是否跨天">
          <el-switch v-model="form.is_cross_day" />
        </el-form-item>
        <el-form-item label="扣除就餐(小时)">
          <el-input-number v-model="form.meal_break_hours" :step="0.5" />
        </el-form-item>
        <el-form-item label="标准工时(小时)">
          <el-input-number v-model="form.standard_work_hours" :step="0.5" />
        </el-form-item>
        <el-form-item label="计入加班">
          <el-switch v-model="form.is_overtime_counted" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRule">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'

const activeTab = ref('aphr')
const loading = ref(false)

// ================= APHR 人事系统对接 =================
const aphrForm = reactive({
  APHR_BASE_URL: 'http://10.11.100.151:8092',
  APHR_USERNAME: 'admin',
  APHR_PASSWORD: 'admin123',
  APHR_SYNC_ENABLED: true,
  APHR_SYNC_INTERVAL_MIN: '60',
  APHR_LAST_SYNC_TIME: '',
  APHR_LAST_SYNC_STATUS: 'PENDING'
})

const lastReport = ref<any>({})
const schedulerNextRun = ref('')
const testLoading = ref(false)
const syncLoading = ref(false)
const saveLoading = ref(false)

const connStatus = reactive({
  tested: false,
  success: false,
  latency_ms: 0,
  total_employees: 0,
  error: ''
})

const empList = ref<any[]>([])
const empTotal = ref(0)
const empPage = ref(1)
const empSize = ref(10)
const empKeyword = ref('')
const empLoading = ref(false)

const fetchAphrConfig = async () => {
  try {
    const res = await axios.get('/api/v1/aphr/config')
    const cfg = res.data.config || {}
    aphrForm.APHR_BASE_URL = cfg.APHR_BASE_URL || 'http://10.11.100.151:8092'
    aphrForm.APHR_USERNAME = cfg.APHR_USERNAME || 'admin'
    aphrForm.APHR_PASSWORD = cfg.APHR_PASSWORD || 'admin123'
    aphrForm.APHR_SYNC_ENABLED = String(cfg.APHR_SYNC_ENABLED).toLowerCase() === 'true'
    aphrForm.APHR_SYNC_INTERVAL_MIN = String(cfg.APHR_SYNC_INTERVAL_MIN || '60')
    aphrForm.APHR_LAST_SYNC_TIME = cfg.APHR_LAST_SYNC_TIME || ''
    aphrForm.APHR_LAST_SYNC_STATUS = cfg.APHR_LAST_SYNC_STATUS || ''
    
    if (cfg.APHR_LAST_SYNC_REPORT) {
      try {
        lastReport.value = JSON.parse(cfg.APHR_LAST_SYNC_REPORT)
      } catch {
        lastReport.value = {}
      }
    }
    schedulerNextRun.value = res.data.next_run_time || ''
  } catch (error) {
    ElMessage.error('获取 APHR 配置失败')
  }
}

const handleTestConnection = async () => {
  testLoading.value = true
  try {
    const res = await axios.post('/api/v1/aphr/test', {
      base_url: aphrForm.APHR_BASE_URL,
      username: aphrForm.APHR_USERNAME,
      password: aphrForm.APHR_PASSWORD
    })
    connStatus.tested = true
    connStatus.success = res.data.success
    connStatus.latency_ms = res.data.latency_ms || 0
    connStatus.total_employees = res.data.total_employees || 0
    ElNotification({
      title: 'APHR 连接测试成功',
      message: `连通正常 (延迟: ${connStatus.latency_ms}ms)，员工总数: ${connStatus.total_employees} 人`,
      type: 'success'
    })
  } catch (error: any) {
    connStatus.tested = true
    connStatus.success = false
    const errMsg = error.response?.data?.error || error.message || '连接失败'
    ElNotification({
      title: 'APHR 连接失败',
      message: errMsg,
      type: 'error'
    })
  } finally {
    testLoading.value = false
  }
}

const handleSaveConfig = async (showNotice = true) => {
  saveLoading.value = true
  try {
    await axios.post('/api/v1/aphr/config', {
      ...aphrForm,
      APHR_SYNC_ENABLED: String(aphrForm.APHR_SYNC_ENABLED)
    })
    if (showNotice) {
      ElMessage.success('APHR 配置与调度设置已保存')
    }
    fetchAphrConfig()
  } catch (error) {
    ElMessage.error('保存 APHR 配置失败')
  } finally {
    saveLoading.value = false
  }
}

const handleManualSync = async () => {
  syncLoading.value = true
  try {
    const res = await axios.post('/api/v1/aphr/sync', {
      APHR_BASE_URL: aphrForm.APHR_BASE_URL,
      APHR_USERNAME: aphrForm.APHR_USERNAME,
      APHR_PASSWORD: aphrForm.APHR_PASSWORD
    })
    lastReport.value = res.data
    aphrForm.APHR_LAST_SYNC_TIME = res.data.sync_time
    aphrForm.APHR_LAST_SYNC_STATUS = res.data.status
    ElMessageBox.alert(
      `<b>同步状态:</b> <span style="color: green">成功完成</span><br/>` +
      `<b>抓取员工总数:</b> ${res.data.total_fetched || 0} 人<br/>` +
      `<b>本地新增人数:</b> <span style="color: green">${res.data.inserted || 0}</span> 人<br/>` +
      `<b>本地更新人数:</b> <span style="color: #409EFF">${res.data.updated || 0}</span> 人<br/>` +
      `<b>同步耗时:</b> ${res.data.duration_sec || 0} 秒`,
      'APHR 员工数据同步报告',
      { dangerouslyUseHTMLString: true, type: 'success' }
    )
    fetchAphrEmployees()
  } catch (error: any) {
    const errMsg = error.response?.data?.error || error.message || '同步异常'
    ElMessageBox.alert(`同步失败原因: ${errMsg}`, '同步失败', { type: 'error' })
  } finally {
    syncLoading.value = false
  }
}

const fetchAphrEmployees = async () => {
  empLoading.value = true
  try {
    const res = await axios.get('/api/v1/aphr/employees', {
      params: {
        page: empPage.value,
        size: empSize.value,
        keyword: empKeyword.value
      }
    })
    empList.value = res.data.records || []
    empTotal.value = res.data.total || 0
  } catch (error) {
    ElMessage.error('拉取员工数据失败')
  } finally {
    empLoading.value = false
  }
}

// ================= 全局系统参数 =================
const configs = ref<any[]>([])
const fetchConfigs = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/v1/configs')
    configs.value = res.data
  } catch (error) {
    ElMessage.error('获取配置失败')
  } finally {
    loading.value = false
  }
}

const saveConfig = async (row: any) => {
  try {
    await axios.put('/api/v1/configs/' + row.config_key, {
      config_value: row.config_value
    })
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

// ================= 考勤规则配置 =================
const rules = ref<any[]>([])
const dialogVisible = ref(false)
const dialogTitle = ref('新增班次')
const isEdit = ref(false)
const form = ref<any>({})

const fetchRules = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/v1/attendance-rules')
    rules.value = res.data
  } catch (error) {
    ElMessage.error('获取规则失败')
  } finally {
    loading.value = false
  }
}

const openAddRuleDialog = () => {
  isEdit.value = false
  dialogTitle.value = '新增班次'
  form.value = {
    shift_code: '',
    shift_name: '',
    start_time: '08:00:00',
    end_time: '20:00:00',
    is_cross_day: false,
    meal_break_hours: 1.25,
    standard_work_hours: 8.0,
    is_overtime_counted: true
  }
  dialogVisible.value = true
}

const editRule = (row: any) => {
  isEdit.value = true
  dialogTitle.value = '编辑班次'
  form.value = { ...row }
  dialogVisible.value = true
}

const saveRule = async () => {
  try {
    await axios.post('/api/v1/attendance-rules', form.value)
    ElMessage.success('保存成功')
    dialogVisible.value = false
    fetchRules()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const deleteRule = async (code: string) => {
  try {
    await ElMessageBox.confirm('确认删除该班次规则吗?', '提示', { type: 'warning' })
    await axios.delete('/api/v1/attendance-rules/' + code)
    ElMessage.success('删除成功')
    fetchRules()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleTabChange = (tabName: string) => {
  if (tabName === 'aphr') {
    fetchAphrConfig()
    fetchAphrEmployees()
  } else if (tabName === 'params') {
    fetchConfigs()
  } else if (tabName === 'attendance') {
    fetchRules()
  }
}

onMounted(() => {
  fetchAphrConfig()
  fetchAphrEmployees()
})
</script>

<style scoped>
.settings-container {
  padding: 16px;
  height: 100%;
  box-sizing: border-box;
  overflow-y: auto;
}
.settings-card {
  min-height: calc(100vh - 120px);
}
.header {
  margin-bottom: 16px;
}
.mb-16 {
  margin-bottom: 16px;
}
.mr-10 {
  margin-right: 10px;
}
.mr-5 {
  margin-right: 5px;
}
.font-bold {
  font-weight: 600;
}
.text-blue {
  color: #409EFF;
}
.text-green {
  color: #67C23A;
}
.text-gray {
  color: #909399;
}
.card-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.status-card {
  background: #fbfbfc;
  border: 1px solid #ebeef5;
}
.status-metric {
  font-size: 13px;
  line-height: 24px;
}
.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.metric-label {
  color: #606266;
}
.metric-val {
  color: #303133;
}
.text-ellipsis {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.card-actions {
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px dashed #ebeef5;
  display: flex;
  justify-content: flex-end;
}
.search-box {
  display: flex;
  align-items: center;
}
.pagination-box {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}
</style>
