<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <!-- 待处理任务区 -->
      <el-col :span="16">
        <el-card class="box-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>待指派工单 (AI推荐)</span>
              <el-button type="primary" size="small" @click="fetchWorkOrders">刷新拉取</el-button>
            </div>
          </template>
          
          <div v-if="workOrders.length === 0" class="empty-text">暂无待指派工单</div>
          
          <div v-for="wo in workOrders" :key="wo.work_order_code" class="wo-item">
            <div class="wo-info">
              <h4>{{ wo.work_order_code }}</h4>
              <p>工序: {{ wo.process_name }}</p>
            </div>
            <div class="wo-ai-recommendation">
              <el-alert
                :title="'AI 推荐: ' + wo.recommend_reason"
                type="success"
                :closable="false"
                show-icon
              />
            </div>
            <div class="wo-actions">
              <el-button type="success" size="small" @click="confirmAssign(wo.work_order_code)">一键确认派工</el-button>
              <el-button type="warning" size="small" plain>换人</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 右侧辅助信息区 -->
      <el-col :span="8">
        <el-card class="box-card mb-20" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>本班组出勤概览</span>
            </div>
          </template>
          <div class="attendance-chart" ref="chartRef"></div>
        </el-card>

        <el-card class="box-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>快捷操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button type="primary" plain class="w-full mb-10">录入员工日评分</el-button>
            <el-button type="danger" plain class="w-full mb-10">发起加班审批</el-button>
            <el-button type="info" plain class="w-full">生产质量填报</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const workOrders = ref<any[]>([])
const chartRef = ref<HTMLElement | null>(null)

const fetchWorkOrders = () => {
  // 模拟从后端拉取 AI 匹配完成的工单
  workOrders.value = [
    {
      work_order_code: 'WO-20260908-10',
      process_name: '激光切割',
      recommend_reason: '推荐张师傅(EMP003)：拥有激光切割认证，本月加班38h超出红线，但他已申请豁免并处于空班，故作为备选推荐。'
    },
    {
      work_order_code: 'WO-20260908-20',
      process_name: '超声波清洗',
      recommend_reason: '推荐李师傅(EMP002)：完全匹配清洗技能，本周连续上班仅2天，状态极佳。'
    }
  ]
  ElMessage.success('已拉取最新智能推荐排产结果')
}

const confirmAssign = (woCode: string) => {
  ElMessage.success(`工单 ${woCode} 已确认指派！`)
  workOrders.value = workOrders.value.filter(wo => wo.work_order_code !== woCode)
}

const initChart = () => {
  if (!chartRef.value) return
  const myChart = echarts.init(chartRef.value)
  const option = {
    tooltip: { trigger: 'item' },
    legend: { top: '5%', left: 'center' },
    series: [
      {
        name: '出勤情况',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: { show: false, position: 'center' },
        emphasis: {
          label: { show: true, fontSize: 18, fontWeight: 'bold' }
        },
        labelLine: { show: false },
        data: [
          { value: 18, name: '正常出勤', itemStyle: { color: '#409EFF' } },
          { value: 2, name: '请假', itemStyle: { color: '#E6A23C' } },
          { value: 1, name: '旷工', itemStyle: { color: '#F56C6C' } }
        ]
      }
    ]
  }
  myChart.setOption(option)
}

onMounted(() => {
  fetchWorkOrders()
  initChart()
})
</script>

<style scoped>
.dashboard-container {
  height: 100%;
}
.box-card {
  background-color: var(--bg-card);
  border-color: var(--border-color);
  color: var(--text-primary);
  border-radius: var(--border-radius-base);
  box-shadow: var(--box-shadow-card);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.empty-text {
  text-align: center;
  color: var(--text-secondary);
  padding: 40px 0;
}
.wo-item {
  border: 1px solid var(--border-color);
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.wo-info h4 {
  margin: 0 0 5px 0;
  color: var(--text-primary);
}
.wo-info p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}
.wo-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
.mb-20 {
  margin-bottom: 20px;
}
.mb-10 {
  margin-bottom: 10px;
}
.w-full {
  width: 100%;
  margin-left: 0;
}
.attendance-chart {
  height: 250px;
  width: 100%;
}

:deep(.el-card__header) {
  border-bottom: 1px solid var(--border-color);
}
</style>
