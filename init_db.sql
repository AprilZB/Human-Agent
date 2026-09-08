-- 初始化数据库
CREATE DATABASE IF NOT EXISTS `human_agent_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `human_agent_db`;

-- ==========================================
-- 1. 系统与权限配置
-- ==========================================
CREATE TABLE IF NOT EXISTS `sys_config` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `config_key` VARCHAR(100) NOT NULL UNIQUE COMMENT '配置键名',
    `config_value` VARCHAR(500) NOT NULL COMMENT '配置值',
    `description` VARCHAR(255) COMMENT '用途说明',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表';

INSERT IGNORE INTO `sys_config` (`config_key`, `config_value`, `description`) VALUES
('MAX_OVERTIME_HOURS_PER_MONTH', '36', '每月最大允许加班时长（小时）'),
('MAX_CONSECUTIVE_WORK_DAYS', '6', '最大连续上班天数');

CREATE TABLE IF NOT EXISTS `user_role_mapping` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `employee_id` VARCHAR(50) NOT NULL COMMENT '员工工号或域账号',
    `role_type` ENUM('WORKSHOP_SUPERVISOR', 'TEAM_LEADER', 'ADMIN') NOT NULL COMMENT '角色类型',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_emp_role` (`employee_id`, `role_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户角色关联表';

-- ==========================================
-- 2. 基础主数据 (Master Data)
-- ==========================================

-- 2.1 车间表
CREATE TABLE IF NOT EXISTS `base_workshop` (
    `workshop_code` VARCHAR(50) PRIMARY KEY COMMENT '车间编码',
    `workshop_name` VARCHAR(100) NOT NULL COMMENT '车间名称',
    `manager_id` VARCHAR(50) COMMENT '车间主管工号',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='车间主数据';

-- 2.2 班组表
CREATE TABLE IF NOT EXISTS `base_team` (
    `team_code` VARCHAR(50) PRIMARY KEY COMMENT '班组编码',
    `team_name` VARCHAR(100) NOT NULL COMMENT '班组名称',
    `workshop_code` VARCHAR(50) NOT NULL COMMENT '所属车间',
    `leader_id` VARCHAR(50) COMMENT '班组长工号',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`workshop_code`) REFERENCES `base_workshop`(`workshop_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='班组主数据';

-- 2.3 物料主数据
CREATE TABLE IF NOT EXISTS `base_material` (
    `material_code` VARCHAR(50) PRIMARY KEY COMMENT '物料编码',
    `material_name` VARCHAR(150) NOT NULL COMMENT '物料名称',
    `material_type` ENUM('RAW', 'SEMI_FINISHED', 'FINISHED') NOT NULL COMMENT '物料类型(原料/半成品/成品)',
    `unit` VARCHAR(20) NOT NULL DEFAULT 'PCS' COMMENT '计量单位',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='物料主数据';

-- 2.4 工序主数据 (包含技能要求，解决重复维护痛点)
CREATE TABLE IF NOT EXISTS `base_process` (
    `process_code` VARCHAR(50) PRIMARY KEY COMMENT '工序编码',
    `process_name` VARCHAR(100) NOT NULL COMMENT '工序名称',
    `required_skills` JSON NOT NULL COMMENT '该工序默认要求的人员技能标签集合',
    `standard_time_sec` INT COMMENT '标准工时(秒)',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工序主数据';

-- 2.5 工艺路线主数据 (产品加工顺序)
CREATE TABLE IF NOT EXISTS `base_routing` (
    `routing_code` VARCHAR(50) PRIMARY KEY COMMENT '工艺路线编码',
    `material_code` VARCHAR(50) NOT NULL COMMENT '关联成品/半成品物料',
    `version` VARCHAR(20) NOT NULL DEFAULT 'V1.0' COMMENT '版本号',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`material_code`) REFERENCES `base_material`(`material_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工艺路线主数据';

CREATE TABLE IF NOT EXISTS `base_routing_detail` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `routing_code` VARCHAR(50) NOT NULL COMMENT '工艺路线编码',
    `step_seq` INT NOT NULL COMMENT '工序序号(如10, 20, 30)',
    `process_code` VARCHAR(50) NOT NULL COMMENT '工序编码',
    FOREIGN KEY (`routing_code`) REFERENCES `base_routing`(`routing_code`) ON DELETE CASCADE,
    FOREIGN KEY (`process_code`) REFERENCES `base_process`(`process_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工艺路线明细(工序流转)';

-- 2.6 BOM主数据 (物料清单)
CREATE TABLE IF NOT EXISTS `base_bom` (
    `bom_code` VARCHAR(50) PRIMARY KEY COMMENT 'BOM编码',
    `material_code` VARCHAR(50) NOT NULL COMMENT '父项物料编码',
    `version` VARCHAR(20) NOT NULL DEFAULT 'V1.0' COMMENT '版本号',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`material_code`) REFERENCES `base_material`(`material_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='BOM主表';

CREATE TABLE IF NOT EXISTS `base_bom_detail` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `bom_code` VARCHAR(50) NOT NULL,
    `child_material_code` VARCHAR(50) NOT NULL COMMENT '子项物料编码',
    `quantity_per` DECIMAL(10,4) NOT NULL COMMENT '单件用量',
    FOREIGN KEY (`bom_code`) REFERENCES `base_bom`(`bom_code`) ON DELETE CASCADE,
    FOREIGN KEY (`child_material_code`) REFERENCES `base_material`(`material_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='BOM明细表';

-- ==========================================
-- 3. 生产与业务交易数据 (Transaction Data)
-- ==========================================

-- 3.1 生产订单
CREATE TABLE IF NOT EXISTS `biz_production_order` (
    `order_code` VARCHAR(50) PRIMARY KEY COMMENT '生产订单号',
    `material_code` VARCHAR(50) NOT NULL COMMENT '目标生产物料',
    `routing_code` VARCHAR(50) COMMENT '采用的工艺路线',
    `target_quantity` INT NOT NULL COMMENT '排产数量',
    `plan_start_time` DATETIME COMMENT '计划开始时间',
    `plan_end_time` DATETIME COMMENT '计划结束/交期',
    `status` ENUM('RELEASED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED') DEFAULT 'RELEASED' COMMENT '订单状态',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`material_code`) REFERENCES `base_material`(`material_code`),
    FOREIGN KEY (`routing_code`) REFERENCES `base_routing`(`routing_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='生产订单表';

-- 3.2 工单/工序任务 (将生产订单按工艺路线拆解，这是派工到人的实际颗粒度)
CREATE TABLE IF NOT EXISTS `biz_work_order` (
    `work_order_code` VARCHAR(50) PRIMARY KEY COMMENT '工单任务号',
    `order_code` VARCHAR(50) NOT NULL COMMENT '所属生产订单',
    `process_code` VARCHAR(50) NOT NULL COMMENT '执行工序',
    `team_code` VARCHAR(50) COMMENT '指派班组',
    `required_count` INT NOT NULL DEFAULT 1 COMMENT '工序所需人数',
    `status` ENUM('PENDING', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED') DEFAULT 'PENDING' COMMENT '派工状态',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`order_code`) REFERENCES `biz_production_order`(`order_code`) ON DELETE CASCADE,
    FOREIGN KEY (`process_code`) REFERENCES `base_process`(`process_code`),
    FOREIGN KEY (`team_code`) REFERENCES `base_team`(`team_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工单(工序)排产任务表';

-- 3.3 人岗匹配与排班结果
CREATE TABLE IF NOT EXISTS `task_personnel_assignment` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `work_order_code` VARCHAR(50) NOT NULL COMMENT '关联的具体工单/工序任务',
    `employee_id` VARCHAR(50) NOT NULL COMMENT '推荐/指派的员工工号',
    `recommend_reason` TEXT COMMENT '大模型推荐理由(记录匹配时的技能与规则依据)',
    `status` ENUM('AI_RECOMMENDED', 'CONFIRMED', 'REJECTED') DEFAULT 'AI_RECOMMENDED' COMMENT '状态',
    `confirmed_by` VARCHAR(50) COMMENT '确认人工号',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`work_order_code`) REFERENCES `biz_work_order`(`work_order_code`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='人岗匹配与排班结果表';

-- ==========================================
-- 4. 其它车间协同业务
-- ==========================================

-- 4.1 加班申请
CREATE TABLE IF NOT EXISTS `overtime_application` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `employee_id` VARCHAR(50) NOT NULL COMMENT '申请人员工工号',
    `request_date` DATE NOT NULL COMMENT '加班日期',
    `request_hours` DECIMAL(4, 1) NOT NULL COMMENT '加班时长(小时)',
    `reason` VARCHAR(255) COMMENT '加班事由',
    `status` ENUM('PENDING', 'APPROVED', 'REJECTED', 'SYNCED') DEFAULT 'PENDING',
    `approver_id` VARCHAR(50) COMMENT '审批人工号',
    `approved_at` DATETIME,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_emp_date` (`employee_id`, `request_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='加班申请表';

-- 4.2 员工日评分流水
CREATE TABLE IF NOT EXISTS `daily_employee_rating` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `employee_id` VARCHAR(50) NOT NULL COMMENT '被评分员工工号',
    `rater_id` VARCHAR(50) NOT NULL COMMENT '打分人工号',
    `rating_date` DATE NOT NULL COMMENT '评分日期',
    `score` ENUM('EXCELLENT', 'NORMAL', 'POOR') NOT NULL COMMENT '评分等级',
    `remark` VARCHAR(255),
    `sync_status` ENUM('PENDING', 'SUCCESS', 'FAILED') DEFAULT 'PENDING',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_emp_date` (`employee_id`, `rating_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='员工日评分流水表';

-- 4.3 生产数据(质量记录)
CREATE TABLE IF NOT EXISTS `production_daily_record` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `work_order_code` VARCHAR(50) NOT NULL COMMENT '关联工单任务',
    `batch_no` VARCHAR(100) NOT NULL COMMENT '批次号',
    `record_date` DATE NOT NULL,
    `pass_rate` DECIMAL(5, 2) NOT NULL COMMENT '合格率(%)',
    `defect_count` INT NOT NULL DEFAULT 0 COMMENT '不良品数量',
    `defect_types` JSON COMMENT '不良类型清单',
    `recorder_id` VARCHAR(50) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`work_order_code`) REFERENCES `biz_work_order`(`work_order_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='生产质量记录表';
