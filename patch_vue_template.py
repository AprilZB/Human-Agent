with open('frontend/src/views/data/index.vue', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace the upload button block in all tabs to include a template download button
import re

# We can find all instances of <el-upload and insert a template button before it
code = re.sub(r'(<el-upload :action="[^"]+" :show-file-list="false"[^>]*>)', 
              r'<el-button type="warning" plain class="mr-10" @click="handleDownloadTemplate(activeTab)">下载导入模板</el-button>\n            \1', 
              code)

# Add handleDownloadTemplate method
if 'const handleDownloadTemplate' not in code:
    code = code.replace('const handleExport = (tab: string) => {',
'''const handleDownloadTemplate = (tab: string) => {
  window.open('http://localhost:8100/api/v1/data/' + tab + '/export?template=1')
}

const handleExport = (tab: string) => {''')

with open('frontend/src/views/data/index.vue', 'w', encoding='utf-8') as f:
    f.write(code)
