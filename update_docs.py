import os

with open('项目文件/02_功能配置.md', 'a', encoding='utf-8') as f:
    f.write('''

## 新增业务：角色工作台分离与数据维护 (Data Maintenance)

系统已根据登录角色实现严格的路由与菜单隔离：
- **班组长 (TEAM_LEADER)**：仅可访问“生产工作台 (Dashboard)”。
- **系统管理员 (SYS_ADMIN)**：仅可访问“系统设置 (Settings)”，支持全局系统参数管理。
- **数据管理员 (DATA_ADMIN)**：仅可访问“数据维护 (Data)”，进行主数据管理。

### 1. SAP 延伸主数据
由于本系统作为 SAP 在执行层的延伸，建立了以下 6 大对标模块：
- **物料档案**：隐藏了手工新增按钮（需从 SAP 同步），补充了 有效起始期、货架寿命、安全库存 等十余项明细指标。
- **物料组档案**：维护分类与 SAP 的对照码。
- **不良原因档案**：本地不良代码与 SAP 字典对照。
- **工艺路线档案**：管理 SAP 下发的生产路径版本。
- **工序档案**：管理具体的生产工序动作，**并补充了绑定BOM (bound_bom_code) 的能力，由工序主动拉取并分配物料组件**（对齐 SAP 的组件分配 Component Allocation 逻辑）。
- **BOM 档案**：呈现产品、子件及用量清单，支持 替代物料同行号 的逻辑映射。

### 2. APHR 延伸主数据
系统通过独立页面作为 APHR 数据的查询抓手：
- **员工档案**：从 APHR 抓取，仅供查看员工的基本信息、所属车间、健康证有效期、上岗证有效期及技能矩阵。
- **车间档案**：支持与 SAP 工作中心 (Work Center) 的 N 对 N 映射。

### 3. 生产订单留痕
- **生产订单记录**：沉淀所有从 SAP 同步的生产订单及本地流转情况，支持时间检索和未来导出的扩展。

以上所有基础数据均接入统一的后端分页查询接口，保证海量数据加载性能。
''')

with open('项目文件/03_数据库设计.md', 'w', encoding='utf-8') as f:
    f.write('''# 数据库设计文档 (Master Data & MES Structure)

当前数据库使用轻量级 MySQL 结构，采用 SQLAlchemy ORM 映射。

## 1. 基础架构及主数据对接 (SAP/APHR)

为了承接和缓冲 ERP (SAP) 及人事系统 (APHR) 的数据流，进行了彻底的数据库重构。

### 1.1 SAP 关联数据域
- **base_material (物料档案)**: material_code (PK), material_desc, ase_uom, plant_status, alid_from, min_shelf_life, safety_stock, default_storage_loc
- **base_material_group (物料组)**: group_code, sap_group_code, group_name
- **base_defect_reason (不良原因)**: defect_code, sap_defect_code
- **base_routing (工艺路线)**: outing_code, sap_routing_code, ersion
- **base_routing_detail (工艺路线-工序关联)**: step_seq, process_code, sap_operation_code
- **base_process (工序字典)**: process_code, process_name, equired_skills, **ound_bom_code (绑定BOM编码 - 由工序拉取所需消耗组件)**
- **base_bom (BOM明细)**: om_code, product_code, component_code, quantity, lt_group (替代物料同行号)

### 1.2 APHR 关联数据域
- **base_employee (员工基本档)**: employee_id, 
ame, workshop_code, health_cert_status (有效状态), work_cert_status (有效状态), skills (JSON)
- **base_workshop (车间管理)**: workshop_code, workshop_name, sap_work_center_code (映射SAP工作中心)

## 2. 生产单流转

### 2.1 biz_production_order (生产订单表)
- 来源于 ERP，作为计划的顶层。包含 plan_start_time, 	arget_quantity, status。新增作为“数据维护-生产订单”的分页拉取底层。

### 2.2 biz_work_order (生产工单表 / 派工单)
- **status (状态流转)**:
  - PENDING: 待处理。
  - UNASSIGNED: 人员未满编。
  - DISPATCHED: **已确认派工** (一旦派工，前端隐藏)。

### 2.3 task_personnel_assignment (工单人员分配表)
- work_order_code, employee_id。无唯一约束，支持 **一人多单**。
- status: AI_RECOMMENDED -> CONFIRMED。

## 3. 全局配置
### 3.1 sys_config (系统参数)
- KV 键值对表，支持前端动态界面保存生效。
''')

print("Documentation updated successfully!")
