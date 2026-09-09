<template>
  <div class="settings-container">
    <el-card shadow="hover" header="系统参数设置">
      <el-table :data="configs" v-loading="loading" style="width: 100%" border stripe>
        <el-table-column prop="config_key" label="参数键名" width="250" />
        <el-table-column prop="description" label="描述" />
        <el-table-column label="参数值" width="300">
          <template #default="scope">
            <el-input 
              v-model="scope.row.editValue" 
              v-if="scope.row.isEditing"
              size="small"
            >
              <template #append>
                <el-button @click="saveConfig(scope.row)">保存</el-button>
              </template>
            </el-input>
            <span v-else>{{ scope.row.config_value }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center">
          <template #default="scope">
            <el-button 
              type="primary" 
              link
              @click="editConfig(scope.row)" 
              v-if="!scope.row.isEditing"
            >编辑</el-button>
            <el-button 
              type="info" 
              link
              @click="scope.row.isEditing = false" 
              v-else
            >取消</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const configs = ref<any[]>([])
const loading = ref(false)

const fetchConfigs = async () => {
  loading.value = true
  try {
    const res = await axios.get('http://localhost:8100/api/v1/configs')
    configs.value = res.data.map((c: any) => ({
      ...c,
      isEditing: false,
      editValue: c.config_value
    }))
  } catch (error) {
    ElMessage.error('拉取系统配置失败')
  } finally {
    loading.value = false
  }
}

const editConfig = (row: any) => {
  row.editValue = row.config_value
  row.isEditing = true
}

const saveConfig = async (row: any) => {
  try {
    await axios.put('http://localhost:8100/api/v1/configs/' + row.config_key, {
      config_value: row.editValue
    })
    ElMessage.success('保存成功')
    row.config_value = row.editValue
    row.isEditing = false
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

onMounted(() => {
  fetchConfigs()
})
</script>

<style scoped>
.settings-container {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
