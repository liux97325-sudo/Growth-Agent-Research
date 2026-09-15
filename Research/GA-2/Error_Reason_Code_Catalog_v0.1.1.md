# GA-2：全局错误码 / 原因码目录 v0.1.1（门禁 outcome 增量）

**文档编号：** GA-2-ERR-002  
**版本：** v0.1.1  
**状态：** Draft（**现行门禁相关增量**）  
**阶段：** GA-2 Engineering Design  
**基线：** `Error_Reason_Code_Catalog_v0.1.md`（Draft）  
**对齐：** `Decision_Packet_Schema_v0.2.1.md`；`Gate_Integration_Playbook_v0.2.1.md`  
**审计依据：** GA-2 审计 §5.2 / §12 / §14  
**约束：** 码表为工程契约；不改 GA-1；不写真实 API；数值阈值 Proposed。

---

## 0. 效力与取代

| 层级 | 文件 | 效力 |
|---|---|---|
| 基线 | `Error_Reason_Code_Catalog_v0.1.md` | 继承；码段划分与既有 GATE/ADAPT/ENV/DP/LR/KE/SYS 码继续有效 |
| **本增量** | **v0.1.1** | **现行门禁相关权威增量**：新增动作—审批串用码、decision_outcome 映射、Executed 重试码；**澄清并局部取代** `GATE-1003` 语义 |

冲突时：门禁 outcome / 动作—审批语义相关码以 **v0.1.1** 为准；其余仍以 v0.1 为准。

---

## 1. 相对 v0.1 的增量总表

| ID | 变更 |
|---|---|
| CHG-E1 | 新增 `GATE-1006…1009`：动作形态 × 审批串用 / 空 actions / 缺 no_action_reason |
| CHG-E2 | 新增 `GATE-2008`：`NO_ACTION_APPROVE` 不得批准副作用动作 |
| CHG-E3 | 新增 `ADAPT-2006/2007`：Executed 重试约束 / 禁止改写重入 |
| CHG-E4 | 新增 `DP-1005`：`is_no_action` / 空动作不变量 |
| CHG-E5 | 定义 `decision_outcome` ↔ reason_code 映射表（§4） |
| CHG-E6 | 澄清 `GATE-1003`：不再把 `NO_ACTION_APPROVE` 与 `APPROVE` 混为同一“可执行”检查 |

---

## 2. 码表增量

### 2.1 GATE 增量

| 码 | 短名（建议） | 含义 | severity | retryable | default_outcome | human_action_required | owner | introduced_in |
|---|---|---|---|---|---|---|---|---|
| **GATE-1006** | ACTION_REVIEW_SEMANTIC_MISMATCH | 动作形态与 `review_result` 语义不匹配（含：副作用动作 + `NO_ACTION_APPROVE`） | high | false | REJECT | 否（除非反复出现） | SRA / Gate | v0.1.1 |
| **GATE-1007** | NO_ACTION_REVIEW_MISMATCH | `is_no_action(packet)` 但 `review_result != NO_ACTION_APPROVE`（如误用 `APPROVE`） | high | false | REJECT | 否 | SRA / Gate | v0.1.1 |
| **GATE-1008** | EMPTY_ACTIONS_INVALID | `proposed_actions` 为空；或包被当作 NO_ACTION 但动作列表空 | high | false | REJECT | 否 | RE / Schema | v0.1.1 |
| **GATE-1009** | NO_ACTION_REASON_MISSING | NO_ACTION 包缺 `no_action_reason`，或非 NO_ACTION 包非法携带该原因 | medium | false | REJECT | 否 | RE / SRA | v0.1.1 |
| **GATE-2008** | NO_ACTION_APPROVE_SIDE_EFFECT_FORBIDDEN | `NO_ACTION_APPROVE` 试图批准任何带副作用动作（DPK-I12） | critical | false | REJECT | 是（审计告警） | SRA / Gate | v0.1.1 |

### 2.2 ADAPT 增量

| 码 | 短名（建议） | 含义 | severity | retryable | default_outcome | human_action_required | owner | introduced_in |
|---|---|---|---|---|---|---|---|---|
| **ADAPT-2006** | RETRY_CONSTRAINT_VIOLATED | `Executed` 包重入未满足重试约束（幂等键/内容哈希/可重试状态/字段冻结） | high | false | REJECT | 否 | Adapter / JDA | v0.1.1 |
| **ADAPT-2007** | EXECUTED_REWRITE_FORBIDDEN | 试图修改已 Executed 包的核心字段后再次提交，或超过重试上限仍写 | high | false | REJECT / HOLD | 视上限策略 | Adapter / CBA | v0.1.1 |

### 2.3 DP 增量

| 码 | 含义 | severity | retryable | default_outcome | owner |
|---|---|---|---|---|---|
| **DP-1005** | `is_no_action` 不变量违反（空 actions 或全 NO_ACTION 判定失败；DPK-I9） | high | false | REJECT | Schema / Gate |

---

## 3. 既有码澄清（取代含糊语义）

### 3.1 `GATE-1003` 拆分说明

| 版本 | 表述 | v0.1.1 处理 |
|---|---|---|
| v0.1 | `REVIEW_RESULT_NOT_APPROVED`：`review_result 不在 {APPROVE, NO_ACTION_APPROVE}` | **过宽**。该集合不得再作为“可执行”单一条件 |
| **v0.1.1** | 拆为： | |
| | 写路径需要 `APPROVE` 但不是 → 用 `GATE-1006`（若串用）或保留 `GATE-1003` 表示“非 APPROVE” | 写路径专用 |
| | NO_ACTION 路径需要 `NO_ACTION_APPROVE` 但不是 → **`GATE-1007`** | 合成路径专用 |

**实现建议：**

- 写路径：`review_result != APPROVE` → `GATE-1003`；若恰好是 `NO_ACTION_APPROVE` → 优先 `GATE-1006`/`GATE-2008`。  
- NO_ACTION 路径：`review_result != NO_ACTION_APPROVE` → `GATE-1007`。

### 3.2 继承不变的码

`GATE-1001/1002/1004/1005`、`GATE-2001…2007`、`ADAPT-1001…2005`、`ENV-*`、`DP-1001…1004`、`LR-*`、`KE-*`、`SYS-*` 语义继承 v0.1。

---

## 4. `decision_outcome` ↔ 原因码映射

> 任何 Gate 评估结果必须同时给出 `decision_outcome` 与（失败时）规范 `reason_codes`。  
> **状态 ≠ 错误码**：Receipt status（如 `REJECTED_BY_GATE`）是结果形态；本表是原因与结局语义。

| `decision_outcome` | 典型 reason_codes | 平台副作用 | 回执约束 |
|---|---|---|---|
| **PLATFORM_WRITE** | （成功可空或审计成功码） | LIVE 有；本轮仅受控模拟 | 禁止 `NOT_APPLICABLE_NO_ACTION` |
| **SYNTHETIC_NO_ACTION** | `GATE-2007`（批准） | **无** | 必须 `NOT_APPLICABLE_NO_ACTION`；`synthetic=true`；`platform_ack_ref=null` |
| **REJECT** | `GATE-1001…1009`；`GATE-2002/2005/2008`；`GATE-1004`；`ADAPT-1001…2007`；`DP-1001/1002/1005`；`ENV-1001…1005` | **无** | 不得 approved 写/合成批准 |
| **HOLD** | `GATE-2004`；`GATE-2001`（策略为挂起时）；`ADAPT-2007`（超限转挂起时） | **无** | 无执行回执 |
| **ESCALATE** | `GATE-2006`；ESC-01…10 对应 reason | **无** | 等待 HUMAN_*；经 SRA 映射前不得执行 |

### 4.1 禁止组合（负向）

| 组合 | 处理 |
|---|---|
| `SYNTHETIC_NO_ACTION` + `platform_ack_ref` 非空 | 非法；审计违规 |
| `PLATFORM_WRITE` + 全 NO_ACTION 包 | 非法；`GATE-1006`/`GATE-2008` |
| `REJECT`/`HOLD`/`ESCALATE` + `status=ACCEPTED` 回执 | 非法；回执伪造检测（GIP §6.2） |
| `NO_ACTION_APPROVE` 出现在写路径 `reason_codes` 作为放行依据 | 非法；`GATE-2008` |

---

## 5. 重试语义摘要

| 码 | retryable | 说明 |
|---|---|---|
| `SYS-1001` TIMEOUT | 有条件 | 仅 Executed 重试约束（GIP v0.2.1 §6）满足时 |
| `SYS-1002` UNKNOWN | 有条件 | 同上；不得假定失败或成功 |
| `ADAPT-2006` | false | 重试约束失败本身不可直接重试 |
| `ADAPT-2007` | false | 转 HOLD/ESCALATE |
| `GATE-1006…1009` / `GATE-2008` | false | 语义非法；须新包或修正审批 |
| `GATE-1004` / `ADAPT-2001` | false | Shadow/只读写禁止 |

---

## 6. 与文档映射更新

| 现有位置 | 原短名 / 场景 | 本表 |
|---|---|---|
| DPK v0.2.1 N1 | 副作用 + NO_ACTION_APPROVE | `GATE-1006` / `GATE-2008` → REJECT |
| DPK v0.2.1 N2 | 全 NO_ACTION + APPROVE | `GATE-1007` → REJECT |
| DPK v0.2.1 N4 | 空 actions | `GATE-1008` / `DP-1005` → REJECT |
| DPK v0.2.1 N5 | 缺 no_action_reason | `GATE-1009` → REJECT |
| GIP v0.2.1 §6 | Executed 重试约束失败 | `ADAPT-2006` |
| GIP v0.2.1 §6 | 超限仍写 / 核心字段改写 | `ADAPT-2007` |
| GIP v0.2.1 §8 | outcome 映射表 | 与本文 §4 一致 |
| Fixture FX-03 | 普通动作 + NO_ACTION_APPROVE | `GATE-1006` |
| Fixture FX-19 | 全 NO_ACTION + APPROVE | `GATE-1007` |
| Fixture FX-20 | 缺 no_action_reason | `GATE-1009` |

---

## 7. 明确非声称

1. 本目录不授权真实平台调用。  
2. `severity` / `retryable` / 重试上限均为工程 **Proposed** 默认，待标定。  
3. 完整 KE-1001–1015 与 HTTP/平台二次映射仍按 v0.1 §6 待决，不在本增量关闭。  
4. 本文为 Draft 增量，升格须负责人确认。

---

## 8. 待决

1. 是否为 `decision_outcome` 建立独立 OTel attribute（继承 v0.1 待决）。  
2. `HUMAN-*` 票码是否独立码段（继承）。  
3. `GATE-1003` 是否在下一完整版废弃短名并只保留 1006/1007（建议 RC 前裁决）。

---

## 9. 变更记录

| 日期 | 版本 | 变更 | 依据 |
|---|---|---|---|
| 2026-09-14 | v0.1 | 首次建立全局码表 | GA-DEC-006；完备性 G-03 |
| 2026-09-15 | v0.1.1 | 门禁 outcome 增量：动作—审批串用、空 actions、no_action_reason、Executed 重试、decision_outcome 映射、GATE-1003 拆分 | 审计 §5.2/§12/§14；DPK v0.2.1；GIP v0.2.1 |

---

**Document Status:** Draft（现行门禁相关权威增量）  
**Full Catalog:** 基线字段与其余码段仍读 v0.1 + 本增量  
**Explicit Non-claim:** 非 Confirmed；不改 GA-1；无真实 API。
