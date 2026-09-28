import requests

with open('d:/DEV/Human-Agent/real_import.xlsx', 'rb') as f:
    files = {'file': ('AI智能体中包含生产订单信息表格.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
    resp = requests.post('http://127.0.0.1:8100/api/v1/data/import?tab=production-orders', files=files)
    
print(resp.status_code)
print(resp.text)
