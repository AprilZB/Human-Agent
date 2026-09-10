<template>
  <div class="settings-container">
    <el-card shadow="hover" class="settings-card">
      <el-tabs v-model="activeTab">
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
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const activeTab = ref('params')
const configs = ref<any[]>([])
const rules = ref<any[]>([])
const loading = ref(false)

const dialogVisible = ref(false)
const dialogTitle = ref('新增班次')
const isEdit = ref(false)
const form = ref<any>({})

const fetchConfigs = async () => {
  loading.value = true
  try {
    const res = await axios.get('http://localhost:8100/api/v1/configs')
    configs.value = res.data
  } catch (error) {
    ElMessage.error('获取配置失败')
  } finally {
    loading.value = false
  }
}

const saveConfig = async (row: any) => {
  try {
    await axios.put('http://localhost:8100/api/v1/configs/' + row.config_key, {
      config_value: row.config_value
    })
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const fetchRules = async () => {
  loading.value = true
  try {
    const res = await axios.get('http://localhost:8100/api/v1/attendance-rules')
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
    await axios.post('http://localhost:8100/api/v1/attendance-rules', form.value)
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
    await axios.delete('http://localhost:8100/api/v1/attendance-rules/' + code)
    ElMessage.success('删除成功')
    fetchRules()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchConfigs()
  fetchRules()
})
</script>

<style scoped>
.settings-container {
  padding: 20px;
}
.header {
  margin-bottom: 20px;
}
</style>
