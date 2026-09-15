# GA-2：全局错误码 / 原因码目录

**文档编号：** GA-2-ERR-001  
**版本：** v0.1  
**状态：** Draft  
**阶段：** GA-2 Engineering Design  
**依据：** GA-DEC-006；完备性审计 G-03；GIP/JD/Learning 现有码表归一  
**约束：** 码表为工程契约，不是理论；新增码须 bump 本版本并写变更记录。

---

## 1. 使用规则

1. **唯一权威命名空间：** `GARP-<LAYER>-<CODE>`；实现内可短名，但审计日志必须能映射回本表。  
2. **层前缀：**  
   - `GATE`：门禁/审批  
   - `ADAPT`：Adapter/JD  
   - `ENV`：Runtime Envelope / 自检  
   - `DP`：Decision Packet Schema  
   - `ME/LE/KE`：记忆/学习/知识  
   - `FE/RE/OFG/CBA`：引擎与协调  
3. 现有文档中的短名（如 `DECISION_PACKAGE_INVALID`）在 §3 做映射，实现以本表为准。  
4. 新增码不得复用已废弃码；废弃码保留在 §5。

---

## 2. 码段划分

| 码段 | 含义 | 默认动作倾向 |
|---|---|---|
| GATE-1xxx | 可执行判定失败 | 拒绝提交 |
| GATE-2xxx | Risk/Trust/SRA 谓词 | REVISE/HOLD/REJECT/ESCALATE |
| ADAPT-1xxx | 资源/数据校验 | 拒绝或降级 |
| ADAPT-2xxx | 写路径/影子/幂等 | 硬拒绝 |
| ENV-1xxx | 启动自检/信封 | Fail-closed |
| DP-1xxx | Schema/不变式 | 非法包 |
| LR-1xxx | 学习反思隔离 | 隔离/降权 |
| SYS-1xxx | 通用超时/未知 | 记录+告警 |

---

## 3. 归一码表（Draft）

### 3.1 GATE

| 码 | 短名（旧） | 含义 |
|---|---|---|
| GATE-1001 | DECISION_PACKAGE_INVALID | 双字段可执行条件不满足 |
| GATE-1002 | LIFECYCLE_NOT_EXECUTABLE | lifecycle_status 不在 {Self-reviewed, Executed} |
| GATE-1003 | REVIEW_RESULT_NOT_APPROVED | review_result 不在 {APPROVE, NO_ACTION_APPROVE} |
| GATE-1004 | SHADOW_WRITE_FORBIDDEN | Shadow/只读模式写路径 |
| GATE-1005 | HARD_BLOCK_PRESENT | risk.hard_block 非空 |
| GATE-2001 | TRUST_CAPABILITY_INSUFFICIENT | 动作类超 Trust Level |
| GATE-2002 | RISK_LEVEL_FORBIDDEN | R4/硬红线 |
| GATE-2003 | SRA_REVIEW_REVISE | SRA=REVISE |
| GATE-2004 | SRA_REVIEW_HOLD | SRA=HOLD |
| GATE-2005 | SRA_REVIEW_REJECT | SRA=REJECT |
| GATE-2006 | SRA_ESCALATE_HUMAN | SRA=ESCALATE_HUMAN |
| GATE-2007 | NO_ACTION_APPROVED | 合法 NO_ACTION 获批 |

### 3.2 ADAPT

| 码 | 短名（旧） | 含义 |
|---|---|---|
| ADAPT-1001 | DRY_RUN_REQUIRED | 未 dry_run |
| ADAPT-1002 | VALIDATION_FAILED | BDV 未通过 |
| ADAPT-1003 | STALE_STATE | 状态过期 |
| ADAPT-1004 | INVENTORY_OR_BUDGET_CHANGED | G-06 类变化 |
| ADAPT-1005 | PLAN_STATE_DRIFT | G-04 类漂移 |
| ADAPT-2001 | SHADOW_WRITE_FORBIDDEN | 同 GATE-1004（Adapter 侧） |
| ADAPT-2002 | IDEMPOTENT_REPLAY | G-05 幂等命中 |
| ADAPT-2003 | PLAN_MODE_NOT_ALLOWED | G-09 |
| ADAPT-2004 | FREQ_WINDOW_VIOLATION | G-08 |
| ADAPT-2005 | SOURCE_ENV_INVALID | source_env 非法/未归一 |

### 3.3 ENV

| 码 | 含义 |
|---|---|
| ENV-1001 | SELFCHECK_FAIL |
| ENV-1002 | LIVETRANSPORT_MISASSEMBLED |
| ENV-1003 | ENVELOPE_DRIFT |
| ENV-1004 | CREDENTIAL_PROVIDER_REJECTED |
| ENV-1005 | WRITE_PROBE_UNEXPECTED_SUCCESS |

### 3.4 DP

| 码 | 含义 |
|---|---|
| DP-1001 | SCHEMA_VALIDATION_FAILED |
| DP-1002 | INVARIANT_VIOLATED（DPK-I*） |
| DP-1003 | PACKET_KIND_REQUIRED |
| DP-1004 | REVIEW_RESULT_WRITE_FORBIDDEN（非 SRA） |

### 3.5 LR / 学习

| 码 | 含义 |
|---|---|
| LR-1001 | NON_LIVE_POOL_ISOLATED |
| LR-1002 | TRUST_CREDIT_DENIED |
| LR-1003 | PROMOTE_BLOCKED_ENV |
| LR-1004 | REFLECTION_JOB_QUARANTINED |

### 3.5b KE / 知识晋升（对齐 Knowledge_Evolution_Runtime；待正式评审并入）

| 码 | 含义 |
|---|---|
| KE-1001 | PROMOTION_JOB_INVALID |
| KE-1002 | QUALITY_SCORE_BELOW_THRESHOLD |
| KE-1003 | ENV_PROMOTE_FORBIDDEN（非 LIVE 禁晋升） |
| KE-1004 | AWAITING_HUMAN_APPROVAL |
| KE-1005 | VERSION_LOCKED / SUPERSEDE_CONFLICT |
| KE-1006 | CALIBRATION_VERSION_NOT_APPROVED |
| KE-1007 | LINEAGE_BROKEN |
| KE-1008 | KERT_INVARIANT_VIOLATED |
| KE-1009 | JOB_LEASE_EXPIRED |
| KE-1010 | FEEDBACK_NOTIFY_FAILED |

（完整 KE-1001–1015 以回路 C 文档为准；实现前应 bump 本目录版本并归一。）

### 3.6 SYS

| 码 | 含义 |
|---|---|
| SYS-1001 | TIMEOUT |
| SYS-1002 | UNKNOWN |
| SYS-1003 | UPSTREAM_UNAVAILABLE |

---

## 4. 与现有文档映射

| 现有位置 | 原短名 | 本表 |
|---|---|---|
| Fixture §4.2 | DRY_RUN_REQUIRED | ADAPT-1001 |
| JD/GIP | DECISION_PACKAGE_INVALID | GATE-1001 |
| JD/GIP | SHADOW_WRITE_FORBIDDEN | GATE-1004 / ADAPT-2001 |
| Skeleton ReceiptStatus | REJECTED_BY_GATE 等 | 状态≠码；码在 reason_code |
| Learning 运行时 | 隔离/禁晋升 | LR-1001/1003 |

实现要求：`reason_code` 用本表 ID；`legacy_short_name` 可选保留。

---

## 5. 废弃

| 码/别名 | 处理 |
|---|---|
| `source=REAL` | 废弃；映射 `source_env=LIVE`（GA-DEC-006） |
| `packet_kind=live_decision` | 废弃；canonical=`standard` |

---

## 6. 待决

1. 是否需要 HTTP/平台错误二次映射层。  
2. 码是否进 OpenTelemetry attribute 规范。  
3. 人类审批票错误码（HUMAN-*）是否独立码段。

---

**Document Status:** Draft  
**变更：** 2026-09-14 首次建立（关闭完备性 G-03）
