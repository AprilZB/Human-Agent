import re

with open('frontend/src/views/data/index.vue', 'r', encoding='utf-8') as f:
    code = f.read()

# Fix the broken JS literal by regex since exact string matching might fail due to indentation
pattern = r"ElMessageBox\.alert\(\s*文档读取总数: <br/> \+\s*成功导入数: <span style=\"color: green\"></span><br/> \+\s*失败数量: <span style=\"color: red\"></span> \+ \s*\(res\.errors && res\.errors\.length > 0 \? <br/><br/><span style=\"color: gray; font-size: 12px\">错误详情 \(部分\): </span> : \'\'\),\s*\'导入结果详细报告\',\s*\{\s*dangerouslyUseHTMLString: true,\s*type: res\.fail > 0 \? \'warning\' : \'success\'\s*\}\s*\)\.then\(\(\) => \{\s*fetchData\(\)\s*\}\)\.catch\(\(\) => \{\s*fetchData\(\)\s*\}\)"

fixed = """ElMessageBox.alert(
      `文档读取总数: ${res.total_read || 0}<br/>` +
      `成功导入数: <span style="color: green">${res.success || 0}</span><br/>` +
      `失败数量: <span style="color: red">${res.fail || 0}</span>` + 
      (res.errors && res.errors.length > 0 ? `<br/><br/><span style="color: gray; font-size: 12px">错误详情 (部分): ${res.errors[0]}</span>` : ''),
      '导入结果详细报告',
      {
        dangerouslyUseHTMLString: true,
        type: res.fail > 0 ? 'warning' : 'success'
      }
    ).then(() => {
      fetchData()
    }).catch(() => {
      fetchData()
    })"""

code = re.sub(pattern, fixed, code)

with open('frontend/src/views/data/index.vue', 'w', encoding='utf-8') as f:
    f.write(code)
