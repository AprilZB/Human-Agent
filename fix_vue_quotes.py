with open('frontend/src/views/report/production.vue', 'r', encoding='utf-8') as f:
    code = f.read()

# fix the string interpolation that powershell mangled
code = code.replace("url += start_date=", "url += fstart_date=&end_date=&".replace("f", ""))
code = code.replace("url += product_code=", "url += fproduct_code=".replace("f", ""))
code = code.replace("const res = await axios.get(/api/v1/report/production//confirmations)", "const res = await axios.get(f/api/v1/report/production//confirmations)".replace("f", ""))

with open('frontend/src/views/report/production.vue', 'w', encoding='utf-8') as f:
    f.write(code)

with open('frontend/src/views/report/overtime.vue', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace("url += start_date=", "url += fstart_date=&end_date=".replace("f", ""))
code = code.replace("const res = await axios.get(/api/v1/report/overtime/)", "const res = await axios.get(f/api/v1/report/overtime/)".replace("f", ""))

with open('frontend/src/views/report/overtime.vue', 'w', encoding='utf-8') as f:
    f.write(code)
