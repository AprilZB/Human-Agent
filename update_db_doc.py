with open('项目文件/03_数据库设计.md', 'r', encoding='utf-8') as f:
    content = f.read()

old_table = '''| 字段 | 类型 | 说明 |
|---|---|---|
| id | Integer | 主键 |
| attendance_date | Date | 考勤日期 |
| employee_id | String | 员工号 |
| shift_code | String | 班次 |
| is_holiday | Boolean | 是否节假日 |
| actual_punch_in | DateTime | 实际签到时间 |
| actual_punch_out | DateTime | 实际签退时间 |
| attendance_status | String | 出勤状态 |
| calculated_overtime | Decimal | 系统核算加班时长 |'''

new_table = '''| 字段 | 类型 | 说明 |
|---|---|---|
| id | Integer | 主键 |
| attendance_date | Date | 考勤日期 (工作日期) |
| employee_id | String | 员工号 |
| shift_code | String | 班次 (同步 APHR) |
| is_holiday | Boolean | 是否节假日 |
| actual_punch_in | DateTime | 实际签到时间 (同步盖雅) |
| actual_punch_out | DateTime | 实际签退时间 (同步盖雅) |
| actual_work_hours | Decimal | 实际工时 (同步盖雅) |
| calculated_overtime | Decimal | MES核算加班时长 |
| attendance_type | String | 出勤类型 (请假/出差/外出，同步盖雅) |
| attendance_status | String | 状态标识 |
| sync_time | DateTime | 盖雅数据同步时间 |
| external_source | String | 数据来源标识 (GaiaWorks/APHR) |'''

if old_table in content:
    content = content.replace(old_table, new_table)
    with open('项目文件/03_数据库设计.md', 'w', encoding='utf-8') as f:
        f.write(content)
else:
    print("Warning: could not find exact table in documentation. It may have drifted.")
