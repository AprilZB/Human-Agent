<template>
  <div class="data-container">
    <el-card shadow="hover">
      <el-tabs v-model="activeTab">
        
        <el-tab-pane label="物料档案" name="materials">
          <div class="header-actions">
            <el-button type="primary">新增物料</el-button>
          </div>
          <el-table :data="materials" border stripe>
            <el-table-column prop="material_code" label="物料代码" width="150" />
            <el-table-column prop="material_name" label="物料名称" />
            <el-table-column prop="category" label="分类" width="120" />
            <el-table-column label="操作" width="120" align="center">
              <template #default>
                <el-button type="primary" link>编辑</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="工序字典" name="processes">
          <div class="header-actions">
            <el-button type="primary">新增工序</el-button>
          </div>
          <el-table :data="processes" border stripe>
            <el-table-column prop="process_code" label="工序代码" width="150" />
            <el-table-column prop="process_name" label="工序名称" />
            <el-table-column prop="standard_time_sec" label="标准工时(秒)" width="150" />
            <el-table-column label="操作" width="120" align="center">
              <template #default>
                <el-button type="primary" link>编辑</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="班组人员" name="employees">
          <div class="header-actions">
            <el-button type="primary">新增人员</el-button>
          </div>
          <el-table :data="employees" border stripe>
            <el-table-column prop="employee_id" label="工号" width="120" />
            <el-table-column prop="name" label="姓名" width="120" />
            <el-table-column prop="team_code" label="所属班组" width="120" />
            <el-table-column prop="skills" label="技能资质" />
            <el-table-column label="操作" width="120" align="center">
              <template #default>
                <el-button type="primary" link>编辑</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const activeTab = ref('materials')

// TODO: 从后端接口获取真实数据，这里先放一些 Mock 占位
const materials = ref([
  { material_code: 'MAT-001', material_name: '钣金外壳A型', category: '半成品' },
  { material_code: 'MAT-OLD', material_name: '通用支架组件', category: '原料' }
])

const processes = ref([
  { process_code: 'P-STAMP-01', process_name: '冲压工序A', standard_time_sec: 300 },
  { process_code: 'P-WELD-01', process_name: '焊接工序B', standard_time_sec: 400 }
])

const employees = ref([
  { employee_id: 'EMP001', name: '张三', team_code: 'TEAM-A', skills: '激光切割,焊接' },
  { employee_id: 'EMP002', name: '李四', team_code: 'TEAM-A', skills: '打磨' },
  { employee_id: 'EMP003', name: '王五', team_code: 'TEAM-A', skills: '激光切割' }
])
</script>

<style scoped>
.data-container {
  max-width: 1200px;
  margin: 0 auto;
}
.header-actions {
  margin-bottom: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
