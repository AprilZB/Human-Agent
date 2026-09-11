with open('项目文件/03_数据库设计.md', 'a', encoding='utf-8') as f:
    f.write('''
## 4. 考勤与盖雅工厂集成 (GaiaWorks Integration)
为了未来平滑对接“盖雅工厂”的排班、请假、外出、加班等全流程管理，系统设计了考勤中枢表。

### 4.1 biz_employee_attendance (出勤排班记录)
作为 APHR（排班数据）与 第三方盖雅工厂（打卡、请假、出差等）的聚合归口。
- **attendance_date (工作日期)**
- **employee_id (工号)**
- **shift_code (排班)**: 来源于 APHR
- **actual_punch_in / out (签到/签退时间)**: 同步自盖雅工厂
- **actual_work_hours (实际工时)**: 来源于盖雅工厂
- **attendance_type (出勤类型)**: 例如正常、请假、外出、出差，同步自盖雅工厂
- **calculated_overtime (核算加班工时)**: MES 本地计算逻辑
- **sync_time (同步时间)**: 数据下发/同步的时间戳
- **external_source**: 标记数据来源（如 GaiaWorks / APHR）
''')
