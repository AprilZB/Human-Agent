import json
import codecs

with open('d:/DEV/Human-Agent/get_all_headers.py', 'r', encoding='utf-8') as f:
    pass # just to check we can write Python

data = {
  "AI BOM档案.xlsx": [
    "BOM\\u7f16\\u7801",
    "\\u7236\\u4ef6\\u7f16\\u7801",
    "\\u5b50\\u4ef6\\u7f16\\u7801",
    "\\u7528\\u91cf"
  ],
  "AI不良原因档案.xlsx": [
    "\\u672c\\u5730\\u4e0d\\u826f\\u4ee3\\u7801",
    "SAP\\u4e0d\\u826f\\u4ee3\\u7801",
    "\\u4e0d\\u826f\\u540d\\u79f0",
    "\\u63cf\\u8ff0"
  ],
  "AI工序档案.xlsx": [
    "\\u5de5\\u5e8f\\u4ee3\\u7801",
    "\\u5de5\\u5e8f\\u540d\\u79f0",
    "\\u6807\\u51c6\\u5de5\\u65f6(\\u79d2)",
    "\\u6240\\u9700\\u6280\\u80fd"
  ],
  "AI打卡记录.xlsx": [
    "ID",
    "\\u8003\\u52e4\\u65e5\\u671f",
    "\\u5de5\\u53f7",
    "\\u6392\\u73ed\\u73ed\\u6b21",
    "\\u662f\\u5426\\u8282\\u5047\\u65e5",
    "\\u5b9e\\u9645\\u7b7e\\u5230",
    "\\u5b9e\\u9645\\u7b7e\\u9000",
    "\\u8003\\u52e4\\u72b6\\u6001",
    "\\u6838\\u7b97\\u52a0\\u73ed(H)"
  ],
  "AI报工.xlsx": [
    "\\u5de5\\u5382",
    "\\u5de5\\u4f5c\\u4e2d\\u5fc3",
    "\\u751f\\u4ea7\\u6279\\u6b21\\u53f7",
    "\\u751f\\u4ea7\\u5355\\u53f7",
    "\\u54c1\\u53f7",
    "\\u5408\\u683c\\u54c1\\u6570",
    "\\u62a5\\u5de5\\u5de5\\u65f6",
    "\\u4e0d\\u5408\\u683c\\u6570",
    "\\u62a5\\u5e9f\\u54c1\\u6570"
  ],
  "AI物料.xlsx": [
    "\\u7269\\u6599\\u7f16\\u7801",
    "\\u7269\\u6599\\u63cf\\u8ff0"
  ],
  "AI物料组.xlsx": [
    "\\u672c\\u5730\\u7269\\u6599\\u7ec4\\u7f16\\u7801",
    "SAP\\u5bf9\\u7167\\u7801",
    "\\u7269\\u6599\\u7ec4\\u540d\\u79f0"
  ],
  "AI车间档案.xlsx": [
    "\\u8f66\\u95f4\\u7f16\\u7801",
    "\\u8f66\\u95f4\\u540d\\u79f0",
    "SAP\\u5de5\\u4f5c\\u4e2d\\u5fc3\\u5bf9\\u7167"
  ]
}

for k, v in data.items():
    print(k)
    for c in v:
        print("  " + codecs.decode(c, 'unicode_escape'))
