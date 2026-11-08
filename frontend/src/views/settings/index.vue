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
                  <el-select v-model="empStatusFilter" placeholder="在职状态" clearable style="width: 110px" class="mr-10" @change="fetchAphrEmployees">
                    <el-option label="在职" value="在职" />
                    <el-option label="离职" value="离职" />
                  </el-select>
                  <el-input v-model="empKeyword" placeholder="工号/姓名/部门/上级/职位" clearable style="width: 240px" class="mr-10" @keyup.enter="fetchAphrEmployees" />
                  <el-button type="primary" size="small" @click="fetchAphrEmployees">查询</el-button>
                  <el-button size="small" @click="resetSearch">重置</el-button>
                </div>
              </div>
            </template>
            <el-table :data="empList" v-loading="empLoading" border stripe style="width: 100%" height="340px">
              <el-table-column prop="employee_id" label="工号" width="120" fixed />
              <el-table-column prop="name" label="姓名" width="100" fixed />
              <el-table-column prop="department_name" label="所属部门" width="170" show-overflow-tooltip />
              <el-table-column prop="position" label="岗位/职位" width="130" show-overflow-tooltip />
              <el-table-column prop="status" label="在职状态" width="95" align="center">
                <template #default="scope">
                  <el-tag size="small" :type="scope.row.status === '在职' ? 'success' : 'info'">
                    {{ scope.row.status || '在职' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="direct_manager_name" label="直属上级" width="110">
                <template #default="scope">
                  <span>{{ scope.row.direct_manager_name || '-' }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="workshop_code" label="所属车间" width="110">
                <template #default="scope">
                  <el-tag size="small" :type="scope.row.workshop_code ? 'success' : 'info'">
                    {{ scope.row.workshop_code || '未设置' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="health_cert_status" label="健康证状态" width="110" align="center">
                <template #default="scope">
                  <el-tag size="small" :type="scope.row.health_cert_status === '有效' ? 'success' : 'danger'">
                    {{ scope.row.health_cert_status || '无健康证' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="work_cert_status" label="上岗证状态" width="110" align="center">
                <template #default="scope">
                  <el-tag size="small" :type="scope.row.work_cert_status === '有效' ? 'success' : 'warning'">
                    {{ scope.row.work_cert_status || '无上岗证' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="skills" label="技能矩阵" min-width="140">
                <template #default="scope">
                  <el-tag v-for="s in scope.row.skills" :key="s" size="small" class="mr-5">{{ s }}</el-tag>
                  <span v-if="!scope.row.skills || scope.row.skills.length === 0" style="color: #909399; font-size: 12px">-</span>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="入库/同步时间" width="170" />
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
        <!-- Tab 4: 钉钉工作通知对接与测试 -->
        <el-tab-pane label="钉钉工作通知对接与测试" name="dingtalk">
          <!-- 顶部状态卡片行 -->
          <el-row :gutter="16" class="mb-16">
            <el-col :span="8">
              <el-card shadow="never" class="status-card">
                <template #header>
                  <div class="card-header-flex">
                    <span class="font-bold">钉钉中台服务状态</span>
                    <el-tag :type="dtConn.tested ? (dtConn.success ? 'success' : 'danger') : 'info'" size="small">
                      {{ dtConn.tested ? (dtConn.success ? '服务连通正常' : '连接异常') : '待检测' }}
                    </el-tag>
                  </div>
                </template>
                <div class="status-metric">
                  <div class="metric-item">
                    <span class="metric-label">服务 Base URL：</span>
                    <span class="metric-val text-ellipsis" :title="dtConn.url">{{ dtConn.url }}</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">接口文档：</span>
                    <a href="http://10.11.100.154:8089/api/docs" target="_blank" style="color: #409EFF; text-decoration: none;">
                      http://10.11.100.154:8089/api/docs ↗
                    </a>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">响应延迟：</span>
                    <span class="metric-val">{{ dtConn.tested && dtConn.success ? `${dtConn.latency_ms} ms` : '-' }}</span>
                  </div>
                </div>
                <div class="card-actions">
                  <el-button type="primary" plain size="small" :loading="dtConnLoading" @click="testDtConnection">检测服务连通</el-button>
                </div>
              </el-card>
            </el-col>

            <el-col :span="8">
              <el-card shadow="never" class="status-card">
                <template #header>
                  <div class="card-header-flex">
                    <span class="font-bold">测试员工 1：张勃</span>
                    <el-tag type="primary" size="small">工号: 404256402</el-tag>
                  </div>
                </template>
                <div class="status-metric">
                  <div class="metric-item">
                    <span class="metric-label">所属部门：</span>
                    <span class="metric-val">企划部 / 智能制造部</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">钉钉 UserID：</span>
                    <span class="metric-val font-bold text-blue">1636684046776099</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">绑定手机：</span>
                    <span class="metric-val">15957270693</span>
                  </div>
                </div>
                <div class="card-actions">
                  <el-button type="primary" size="small" :loading="dtSending" @click="sendSingleTest('404256402', '张勃')">
                    向张勃推送测试消息
                  </el-button>
                </div>
              </el-card>
            </el-col>

            <el-col :span="8">
              <el-card shadow="never" class="status-card">
                <template #header>
                  <div class="card-header-flex">
                    <span class="font-bold">测试员工 2：李丽丽</span>
                    <el-tag type="success" size="small">工号: 404191243</el-tag>
                  </div>
                </template>
                <div class="status-metric">
                  <div class="metric-item">
                    <span class="metric-label">所属部门：</span>
                    <span class="metric-val">百通-生产部</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">钉钉 UserID：</span>
                    <span class="metric-val font-bold text-green">311642243526055534</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">绑定手机：</span>
                    <span class="metric-val">15905838558</span>
                  </div>
                </div>
                <div class="card-actions">
                  <el-button type="success" size="small" :loading="dtSending" @click="sendSingleTest('404191243', '李丽丽')">
                    向李丽丽推送测试消息
                  </el-button>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <!-- 中部：按工号发送钉钉工作通知表单 -->
          <el-card shadow="never" class="mb-16">
            <template #header>
              <div class="card-header-flex">
                <span class="font-bold">自定义工号解析与工作消息发送</span>
                <div>
                  <el-button size="small" @click="dtSendForm.employee_id = '404256402'; resolveDtUser()">填入张勃 (404256402)</el-button>
                  <el-button size="small" @click="dtSendForm.employee_id = '404191243'; resolveDtUser()">填入李丽丽 (404191243)</el-button>
                </div>
              </div>
            </template>
            <el-form :model="dtSendForm" label-width="120px">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="员工工号">
                    <div style="display: flex; width: 100%; gap: 10px;">
                      <el-input v-model="dtSendForm.employee_id" placeholder="输入员工工号，如 404256402" clearable />
                      <el-button type="primary" plain :loading="userResolveLoading" @click="resolveDtUser">解析钉钉身份</el-button>
                    </div>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="消息标题">
                    <el-input v-model="dtSendForm.title" placeholder="通知标题" />
                  </el-form-item>
                </el-col>
              </el-row>

              <!-- 解析出的用户信息展示 -->
              <div v-if="resolvedUser" class="resolved-user-box mb-16">
                <span class="font-bold mr-10">已解析人员：</span>
                <el-tag type="primary" class="mr-10">{{ resolvedUser.name }}</el-tag>
                <span class="mr-10"><b>部门:</b> {{ resolvedUser.department || '-' }}</span>
                <span class="mr-10"><b>职位:</b> {{ resolvedUser.position || '-' }}</span>
                <span class="mr-10"><b>手机:</b> {{ resolvedUser.mobile || '-' }}</span>
                <span class="mr-10"><b>钉钉 UserID:</b> <code style="color: #409EFF">{{ resolvedUser.dingtalkUserId }}</code></span>
              </div>

              <el-form-item label="消息正文">
                <el-input v-model="dtSendForm.message" type="textarea" :rows="3" placeholder="请输入工作通知详细内容" />
              </el-form-item>

              <el-form-item>
                <el-button type="primary" :loading="dtSending" @click="handleCustomSend">发送钉钉工作通知</el-button>
                <el-button type="warning" plain :loading="dtSending" @click="handleBatchSendAll">一键同时向张勃和李丽丽发送</el-button>
              </el-form-item>
            </el-form>
          </el-card>

          <!-- 底部：推送执行记录 -->
          <el-card shadow="never">
            <template #header>
              <div class="card-header-flex">
                <span class="font-bold">钉钉工作通知发送记录 (最近 {{ pushResults.length }} 条)</span>
                <el-button size="small" link type="danger" v-if="pushResults.length > 0" @click="pushResults = []">清空记录</el-button>
              </div>
            </template>
            <el-table :data="pushResults" border stripe style="width: 100%" height="240px">
              <el-table-column prop="time" label="发送时间" width="110" align="center" />
              <el-table-column prop="employee_id" label="员工工号" width="120" />
              <el-table-column prop="name" label="姓名" width="100">
                <template #default="scope">
                  <span>{{ scope.row.name || '-' }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="department" label="所属部门" width="150" show-overflow-tooltip />
              <el-table-column prop="dingtalkUserId" label="钉钉 UserID" width="180">
                <template #default="scope">
                  <code>{{ scope.row.dingtalkUserId || '-' }}</code>
                </template>
              </el-table-column>
              <el-table-column prop="message" label="消息内容" min-width="220" show-overflow-tooltip />
              <el-table-column prop="success" label="推送结果" width="100" align="center">
                <template #default="scope">
                  <el-tag :type="scope.row.success ? 'success' : 'danger'" size="small">
                    {{ scope.row.success ? '发送成功' : '失败' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="任务号 / 接口回执" min-width="160" show-overflow-tooltip>
                <template #default="scope">
                  <span v-if="scope.row.detail?.workflow_result?.response?.task_id" style="color: #67C23A">
                    Task ID: {{ scope.row.detail.workflow_result.response.task_id }}
                  </span>
                  <span v-else-if="scope.row.detail?.post_result?.errcode === 0" style="color: #409EFF">
                    POST: success (errcode 0)
                  </span>
                  <span v-else-if="scope.row.error" style="color: #F56C6C">
                    {{ scope.row.error }}
                  </span>
                  <span v-else style="color: #909399">-</span>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
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
const empStatusFilter = ref('')
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
        keyword: empKeyword.value,
        status: empStatusFilter.value
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

const resetSearch = () => {
  empKeyword.value = ''
  empStatusFilter.value = ''
  empPage.value = 1
  fetchAphrEmployees()
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

// ================= 钉钉工作通知对接 =================
const dtConn = reactive({
  tested: false,
  success: false,
  latency_ms: 0,
  url: 'http://10.11.100.154:8089',
  message: ''
})
const dtConnLoading = ref(false)

const dtSendForm = reactive({
  employee_id: '404256402',
  title: '【甲丁智能体】生产工作通知',
  message: '【派工提醒】您已被分配至生产任务工单：WO-13551286-01，工序：中包装，请按时出勤开工。'
})

const resolvedUser = ref<any>(null)
const userResolveLoading = ref(false)
const dtSending = ref(false)
const pushResults = ref<any[]>([])

const testDtConnection = async () => {
  dtConnLoading.value = true
  try {
    const res = await axios.get('/api/v1/dingtalk/test-connection')
    dtConn.tested = true
    dtConn.success = res.data.success
    dtConn.latency_ms = res.data.latency_ms
    dtConn.url = res.data.url
    dtConn.message = res.data.message
    if (res.data.success) {
      ElNotification({
        title: '钉钉服务连接正常',
        message: `服务地址: ${dtConn.url} (延迟: ${dtConn.latency_ms}ms)`,
        type: 'success'
      })
    } else {
      ElNotification({
        title: '钉钉服务连接失败',
        message: res.data.error || '无法连接钉钉服务',
        type: 'error'
      })
    }
  } catch (error: any) {
    dtConn.tested = true
    dtConn.success = false
    ElNotification({
      title: '钉钉服务连接失败',
      message: error.message || '网络异常',
      type: 'error'
    })
  } finally {
    dtConnLoading.value = false
  }
}

const resolveDtUser = async () => {
  if (!dtSendForm.employee_id.trim()) {
    ElMessage.warning('请输入要解析的员工工号')
    return
  }
  userResolveLoading.value = true
  try {
    const res = await axios.get(`/api/v1/dingtalk/user/${dtSendForm.employee_id.trim()}`)
    resolvedUser.value = res.data.user
    ElMessage.success(`成功解析工号 ${dtSendForm.employee_id}：${res.data.user.name}`)
  } catch (error: any) {
    resolvedUser.value = null
    ElMessage.error(error.response?.data?.message || '未查询到该工号对应的钉钉用户')
  } finally {
    userResolveLoading.value = false
  }
}

const sendSingleTest = async (empId: string, empName: string) => {
  dtSending.value = true
  try {
    const res = await axios.post('/api/v1/dingtalk/test', {
      employee_id: empId,
      title: '【测试】钉钉工作消息',
      message: `【甲丁智能体】工号打通测试：${empName}收到中包车间生产派工通知。`
    })
    const item = res.data
    pushResults.value.unshift({
      ...item,
      time: new Date().toLocaleTimeString()
    })
    if (item.success) {
      ElNotification({
        title: `向 ${empName} (${empId}) 推送成功`,
        message: `钉钉 UserID: ${item.dingtalkUserId}，工作流 TaskId: ${item.detail?.workflow_result?.response?.task_id || '已接收'}`,
        type: 'success'
      })
    } else {
      ElNotification({
        title: `向 ${empName} 推送失败`,
        message: item.error || '请检查钉钉接口状态',
        type: 'error'
      })
    }
  } catch (error: any) {
    ElMessage.error('推送请求失败')
  } finally {
    dtSending.value = false
  }
}

const handleCustomSend = async () => {
  if (!dtSendForm.employee_id.trim()) {
    ElMessage.warning('请输入目标员工工号')
    return
  }
  dtSending.value = true
  try {
    const res = await axios.post('/api/v1/dingtalk/test', {
      employee_id: dtSendForm.employee_id.trim(),
      title: dtSendForm.title,
      message: dtSendForm.message
    })
    const item = res.data
    pushResults.value.unshift({
      ...item,
      time: new Date().toLocaleTimeString()
    })
    if (item.success) {
      ElNotification({
        title: `消息已推送至 ${item.name || item.employee_id}`,
        message: `钉钉 UserID: ${item.dingtalkUserId}`,
        type: 'success'
      })
    } else {
      ElNotification({
        title: '推送失败',
        message: item.error || '发送异常',
        type: 'error'
      })
    }
  } catch (error: any) {
    ElMessage.error('推送失败')
  } finally {
    dtSending.value = false
  }
}

const handleBatchSendAll = async () => {
  dtSending.value = true
  try {
    const res = await axios.post('/api/v1/dingtalk/test', {
      employee_id: 'ALL',
      title: dtSendForm.title,
      message: dtSendForm.message
    })
    const results = res.data.results || []
    results.forEach((item: any) => {
      pushResults.value.unshift({
        ...item,
        time: new Date().toLocaleTimeString()
      })
    })
    ElNotification({
      title: '批量推送完成',
      message: `成功: ${res.data.success_count} 人，失败: ${res.data.fail_count} 人`,
      type: res.data.success_count > 0 ? 'success' : 'error'
    })
  } catch (error: any) {
    ElMessage.error('批量推送失败')
  } finally {
    dtSending.value = false
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
  } else if (tabName === 'dingtalk') {
    if (!dtConn.tested) {
      testDtConnection()
    }
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

.resolved-user-box {
  background: #f4f4f5;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 13px;
  border-left: 4px solid #409EFF;
}
</style>
