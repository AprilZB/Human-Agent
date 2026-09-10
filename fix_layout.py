with open('frontend/src/layout/index.vue', 'r', encoding='utf-8') as f:
    code = f.read()

import re
old_menu = r'<el-menu-item index="/dashboard" v-if="userStore\.userInfo\?\.role === \'TEAM_LEADER\'">[\s\S]*?</el-menu-item>'

new_menu = '''<el-menu-item index="/dashboard" v-if="userStore.userInfo?.role === 'TEAM_LEADER'">
          <el-icon><Monitor /></el-icon>
          <span>派工工作台</span>
        </el-menu-item>
        <el-menu-item index="/report/production" v-if="userStore.userInfo?.role === 'TEAM_LEADER'">
          <el-icon><Document /></el-icon>
          <span>生产报表</span>
        </el-menu-item>
        <el-menu-item index="/report/overtime" v-if="userStore.userInfo?.role === 'TEAM_LEADER'">
          <el-icon><Timer /></el-icon>
          <span>加班报表</span>
        </el-menu-item>
        <el-menu-item index="/grading" v-if="userStore.userInfo?.role === 'TEAM_LEADER'">
          <el-icon><Star /></el-icon>
          <span>员工考评</span>
        </el-menu-item>'''

code = re.sub(old_menu, new_menu, code)

with open('frontend/src/layout/index.vue', 'w', encoding='utf-8') as f:
    f.write(code)
