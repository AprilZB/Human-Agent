import re

with open('frontend/src/views/data/index.vue', 'r', encoding='utf-8') as f:
    code = f.read()

# Add attendances to tabs array
code = code.replace(
    "'materials', 'production-orders', 'confirmations', 'employees', 'workshops', \n  'defect-reasons', 'material-groups', 'routings', 'processes', 'boms'",
    "'materials', 'production-orders', 'confirmations', 'employees', 'workshops', \n  'defect-reasons', 'material-groups', 'routings', 'processes', 'boms', 'attendances'"
)

# Add el-tab-pane
attendance_pane = '''
        <!-- 出勤排班记录 -->
        <el-tab-pane label="出勤排班记录" name="attendances">
          <div class="filter-bar">
            <el-input v-model="filters.attendances" placeholder="工号" style="width: 200px" class="mr-10" />
            <el-button type="primary" @click="fetchData">查询</el-button>
            <el-button type="warning" plain class="mr-10" @click="handleDownloadTemplate(activeTab)">下载导入模板</el-button>
            <el-upload :action="'http://localhost:8100/api/v1/data/attendances/import'" :show-file-list="false" :on-success="handleImportSuccess" :on-error="handleImportError" class="ml-auto mr-10">
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
'''

# Insert the pane after employees pane
code = code.replace('<!-- 车间档案 -->', attendance_pane + '\n        <!-- 车间档案 -->')

with open('frontend/src/views/data/index.vue', 'w', encoding='utf-8') as f:
    f.write(code)
