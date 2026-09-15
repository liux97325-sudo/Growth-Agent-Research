# GA-2：Decision Packet Schema v0.2.1（现行 Draft 权威增量）

**文档编号：** GA-2-DPKT-003  
**版本：** v0.2.1  
**状态：** Draft（**现行权威增量**，待负责人确认后可升 Under Review）  
**阶段：** GA-2 Engineering Design  
**基线：**  
- `Decision_Packet_Schema_v0.1.md`（Draft，GA2-T10）— 完整字段表 / 状态机 / 样例 / JSON Schema 主体  
- `Decision_Packet_Schema_v0.2.md`（Draft，GA2-T39）— `objective_snapshot` 增量  
**主线架构：** `Architecture_Overview_v0.2.md`（GA-DEC-004）  
**对齐：** `Gate_Integration_Playbook_v0.2.1.md`（双谓词 / decision_outcome / G-00…G-09）  
**审计依据：** `GA-2_Modification_and_Design_Recommendations_2026-09-15.md` §4–§5、§14（GA2-R03/R04/R05）  
**约束：** 不改 GA-1；不改 PROJECT_SPEC；不写真实 API；所有阈值一律 **Proposed**。本文件**不构成**已确认 GA-DEC。

---

## 0. 阅读与效力声明（合并阅读约定）

### 0.1 三文件合并阅读规则

实现与评审**必须**按下列顺序合并阅读，不得只读其中一份：

| 层级 | 文件 | 覆盖内容 | 效力 |
|---|---|---|---|
| **B 基线** | `Decision_Packet_Schema_v0.1.md` | 定位；完整字段表 §2；状态机 §3；O-H-A-R-R §4；Risk/Trust/SRA §5；shadow §7；端到端样例 §8；JSON Schema 主体 §9；DPK-I1…I8 | **继承**，除非被 v0.2 / v0.2.1 显式覆盖 |
| **I-1 增量** | `Decision_Packet_Schema_v0.2.md` | `objective_snapshot.derivation_trace` / `applied_overlays`（optional, Proposed）；`schema_version`/`$id` → `0.2.x` | **继承** |
| **I-2 权威增量** | **本文件 v0.2.1** | 动作—审批对应表；DPK-I9…I12；`is_no_action` 形式定义；`decision_outcome`；基础校验；生命周期—审批收紧 | **现行 Draft 权威增量**；与 B/I-1 冲突时**以本文件为准** |

> **效力说明：** v0.2.1 是**相对 v0.1+v0.2 的权威增量**，不是对全部字段的重写。完整字段仍以 v0.1 §2 为准（并叠加 v0.2 §1.4 与本文件覆盖项）。实现者无需再拼接“v0.1 基线 + v0.2 增量 + 审计补丁”三套语义——**动作—审批—门禁结果的现行规则以本文件为唯一真相源**。

### 0.2 相对 v0.1 / v0.2 的本轮增量总表

| ID | 变更 | 性质 | 覆盖对象 |
|---|---|---|---|
| **CHG-05** | 冻结动作—审批结果唯一对应表 | **强制** | 覆盖 v0.1 §5.3「或等价 APPROVE」；覆盖 GIP v0.2 混用可执行集 |
| **CHG-06** | 新增 DPK-I9…I12 | **强制不变量** | 扩展 v0.1 §1.5 |
| **CHG-07** | 形式定义 `is_no_action(packet)` | **强制** | 澄清 DPK-I4；禁止空 actions 被识别为 NO_ACTION |
| **CHG-08** | 定义 `decision_outcome` 五值语义 | **强制**（与 GIP v0.2.1 对齐） | 废止单一 `allowed: bool` 混用 |
| **CHG-09** | 基础 Schema 校验清单（审计 §4.5） | **强制**（校验器） | 扩展 v0.1 §9.1 |
| **CHG-10** | 生命周期进入 `Executed` 的审批条件收紧 | **强制** | 覆盖 v0.1 §3.3 宽松表述 |

### 0.3 明确不做

- 不重写 v0.1 全部字段表、样例全文或 JSON Schema 主体（仅列增量与覆盖）。  
- 不改变 `review_result` 仅 SRA 可写的规则（v0.1 §2.6 / GIP C5 继承）。  
- 不授权 LIVE 写路径；`execution_mode` 本轮仍仅 `SHADOW_READ_ONLY`。  
- 不修改 GA-1 / PROJECT_SPEC。

---

## 1. 动作—审批结果对应表（冻结）

> **唯一允许的对应关系。** 任何其他组合均非法，门禁必须拒绝，且不得生成“已批准可执行”回执。

| 动作形态（`proposed_actions`） | 唯一允许 `review_result` | 是否进入平台写路径 | 回执形态 | 不变量 |
|---|---|---|---|---|
| **全部** `action_class == NO_ACTION` 且 **非空** | **仅** `NO_ACTION_APPROVE` | **否** | 合成回执 `NOT_APPLICABLE_NO_ACTION`（`synthetic=true`, `platform_ack_ref=null`） | DPK-I9 / I10 / I12 |
| **至少一个** `action_class != NO_ACTION` | 可执行时 **仅** `APPROVE` | 视完整 G-00…G-09 与 envelope 而定 | 平台/模拟回执；禁止用 `NO_ACTION_APPROVE` 放行 | DPK-I11 / I12 |
| `REVISE` / `HOLD` / `REJECT` / `ESCALATE_HUMAN` | （审批结果本身） | **不允许执行** | 不得生成 approved / 可执行回执 | GA2-R04 |

### 1.1 负向组合（必须拒绝）

| # | 动作形态 | `review_result` | 期望 `decision_outcome` | 原因码（见 Error Catalog v0.1.1） |
|---|---|---|---|---|
| N1 | 至少一个副作用动作 | `NO_ACTION_APPROVE` | `REJECT` | `GATE-1006` / `GATE-2008` |
| N2 | 全部 NO_ACTION（非空） | `APPROVE` | `REJECT` | `GATE-1007` |
| N3 | 全部 NO_ACTION（非空） | `REJECT` / `HOLD` / `REVISE` / `ESCALATE_HUMAN` | `REJECT` / `HOLD` / `ESCALATE` | 不得产出 approved NO_ACTION 回执（GA2-R04） |
| N4 | 空 `proposed_actions` | 任意 | `REJECT` | `GATE-1008` / `DP-1005` |
| N5 | 全部 NO_ACTION | 任意，但 `no_action_reason` 为空 | `REJECT` | `GATE-1009` |

### 1.2 与 v0.1 §5.3 的覆盖说明

v0.1 §5.3 曾写：

> SRA 谓词含 `CHK_STAB`；结果 `NO_ACTION_APPROVE`（**或等价 APPROVE + action_class=NO_ACTION**）

**v0.2.1 废止括号内“或等价 APPROVE”分支。**  
合法 NO_ACTION 包的审批结果**只能是** `NO_ACTION_APPROVE`。`APPROVE` 仅用于至少含一个非 `NO_ACTION` 动作的包。

---

## 2. 硬不变式增量：DPK-I9 … DPK-I12

> DPK-I1…I8 继承 v0.1 §1.5，效力不变。下列为 **v0.2.1 新增强制不变量**。

| ID | 不变式（形式） | 依据 |
|---|---|---|
| **DPK-I9** | `is_no_action(packet) == true` **iff** `proposed_actions` **非空** 且每个 `action.action_class == NO_ACTION` | 审计 §4.2；GA2-R03 |
| **DPK-I10** | 若 `is_no_action(packet)`，则 `review.review_result` **必须**为 `NO_ACTION_APPROVE` | 审计 §4.2 |
| **DPK-I11** | 若 `not is_no_action(packet)`，则**可执行**路径的 `review.review_result` **只能**为 `APPROVE`（不得是 `NO_ACTION_APPROVE`） | 审计 §4.2 |
| **DPK-I12** | `NO_ACTION_APPROVE` **不得**批准任何带副作用（`action_class != NO_ACTION`）的动作 | 审计 §4.2；GA2-R03 |

### 2.1 与既有不变量的关系

| 既有 | 关系 | 说明 |
|---|---|---|
| DPK-I1 | **细化** | 非 NO_ACTION 写动作：仍须 `lifecycle_status ∈ {Self-reviewed, Executed}` 且 **`review_result=APPROVE`**（不再允许 `NO_ACTION_APPROVE` 混入可执行集） |
| DPK-I2 | **细化** | NO_ACTION 仍须成包；审批结果收紧为唯一 `NO_ACTION_APPROVE` |
| DPK-I4 | **澄清并收紧** | v0.1 表述「空数组仅允许 action_class=NO_ACTION」语义含糊。v0.2.1 起：**空 `proposed_actions` 一律非法**（Schema invalid）；NO_ACTION 必须以**非空**全 `NO_ACTION` 动作列表表达。与 DPK-I9 对齐 |
| DPK-I5 | 继承 | Shadow 写硬拒绝；与 `decision_outcome` 正交 |
| DPK-I6…I8 | 继承 | 删除保护 / 版本审计 / Causal 追溯 |

### 2.2 `is_no_action` 形式定义（强制）

```text
is_no_action(packet) :=
    len(packet.proposed_actions) > 0
    AND ∀ a ∈ packet.proposed_actions: a.action_class == "NO_ACTION"

# 反例（均不得为 true）：
#   all([]) == True  → 空列表不得通过
#   混合 NO_ACTION + KEYWORD_BID → false（至少一个副作用）
```

**伴随必填：**

- `is_no_action(packet)` ⇒ `no_action_reason` **非空**  
- `not is_no_action(packet)` ⇒ `no_action_reason` **必须为空**  
- 每个 `NO_ACTION` 元素**禁止**携带 `change`；非 `NO_ACTION` 元素 `change` **必填**（继承 v0.1 §2.5，并升级为硬校验）

---

## 3. `decision_outcome` 语义（与 Gate 契约对齐）

> **废止**用单一布尔 `allowed` 同时表达“允许平台写”和“允许生成合成回执”。  
> Gate / Adapter / CBA 统一返回下列枚举（对齐 `Gate_Integration_Playbook_v0.2.1`）。

### 3.1 枚举

| `decision_outcome` | 含义 | 平台副作用 | 典型触发 |
|---|---|---|---|
| **`PLATFORM_WRITE`** | 允许进入平台写路径（LIVE）或受控模拟写路径（FIXTURE/SIMULATION，仍受 envelope 约束） | LIVE 下有；本轮 FIXTURE/SIMULATION 为受控模拟 | `non_no_action_executable == true` 且 G-00…G-09 全过 |
| **`SYNTHETIC_NO_ACTION`** | 合法 NO_ACTION：只生成合成回执并进入观察 | **无** | `no_action_observable == true` |
| **`REJECT`** | 拒绝：语义非法 / 门禁失败 / 串用审批 | **无** | N1–N5；hard_block；Shadow 写；Schema 非法等 |
| **`HOLD`** | 挂起：条件未满足或等待解锁，不执行 | **无** | `review_result=HOLD`；Trust/风险暂不可放行 |
| **`ESCALATE`** | 升级人类：不执行，等待 HUMAN_* 映射回 SRA | **无** | `review_result=ESCALATE_HUMAN` |

### 3.2 禁止混用

| 禁止 | 原因 |
|---|---|
| `allowed=true` 且 `is_no_action` 被下游读成“可写” | 合成回执 ≠ 平台写（审计 §5.2） |
| `NO_ACTION_APPROVE` + `decision_outcome=PLATFORM_WRITE` | 违反 DPK-I12 |
| `APPROVE` + 全 NO_ACTION 包 + 任意“执行”结果 | 违反 DPK-I10 |
| REJECT / HOLD / ESCALATE 生成 `synthetic=true` 且标记 approved 的 NO_ACTION 回执 | 违反 GA2-R04 |

### 3.3 建议返回载荷（契约级，非真实 API）

```text
GateDecision {
  decision_outcome: PLATFORM_WRITE | SYNTHETIC_NO_ACTION | REJECT | HOLD | ESCALATE
  passed_gate_ids: string[]          # 已通过的门禁，如 ["G-00","G-01",...]
  failed_gate_id: string | null      # 首个失败门禁
  reason_codes: string[]             # Error Catalog 规范码
  evidence_refs: string[]
  # 禁止单独暴露可被误读为“允许写”的 bare allowed: bool
}
```

---

## 4. 生命周期与审批对应（收紧）

继承 v0.1 §3 状态机骨架；**仅覆盖**进入 `Executed` 与 NO_ACTION 观察路径的条件。

### 4.1 进入 `Executed`（修订）

| 从 → 到 | v0.1 条件 | **v0.2.1 条件（覆盖）** |
|---|---|---|
| Self-reviewed → Executed（平台/模拟写） | `APPROVE` 且非 Shadow；或 `NO_ACTION_APPROVE`；或 HUMAN_APPROVE/MODIFY | **仅当** `not is_no_action(packet)` **且** `review_result=APPROVE` **且** `decision_outcome ∈ {PLATFORM_WRITE}`（本轮 FIXTURE/SIMULATION 下为受控模拟写）；HUMAN_* 须经 SRA 映射为 `APPROVE` 后同样满足 |
| Self-reviewed → Observed（NO_ACTION） | （与 Executed 混写） | **仅当** `is_no_action(packet)` **且** `review_result=NO_ACTION_APPROVE` **且** `decision_outcome=SYNTHETIC_NO_ACTION`；**不经过**平台写；合成回执后进入 Observed |

> **消歧：** 合法 NO_ACTION 包在审计轨迹上可记“合成执行完成”，但**生命周期优先路径**为 `Self-reviewed →（合成回执）→ Observed`，与 v0.1 DPK-I2「跳过 Executed」表述兼容；若实现选择先置 `Executed` 再 `Observed`，必须保证 **零平台副作用** 且 Receipt 标记 `NOT_APPLICABLE_NO_ACTION`。

### 4.2 `REJECT` / `HOLD` / `ESCALATE` 不得产出可执行回执

| `review_result` | `decision_outcome` | 禁止事项 |
|---|---|---|
| `REJECT` | `REJECT` | 不得 `PLATFORM_WRITE`；不得 approved 合成 NO_ACTION 回执 |
| `HOLD` | `HOLD` | 同上 |
| `REVISE` | `REJECT`（或等价“不提交”） | 回 Reasoning；不缓存旧 Risk/Trust（GIP §4.3.5） |
| `ESCALATE_HUMAN` | `ESCALATE` | 等待 HUMAN_*；经 SRA 映射前不得执行 |

---

## 5. 基础 Schema 校验（审计 §4.5，强制）

校验器在 JSON Schema 之外必须执行（或由 Schema `allOf`/自定义断言覆盖）：

| # | 规则 | 失败码 |
|---|---|---|
| V1 | `proposed_actions` **最少 1 项** | `GATE-1008` / `DP-1005` |
| V2 | `action_id` 包内唯一 | `DP-1001` |
| V3 | 非 NO_ACTION ⇒ `change` 必填；NO_ACTION ⇒ `change` 禁止 | `DP-1001` / `GATE-1006` 关联 |
| V4 | `no_action_reason`：NO_ACTION 必填且非空；非 NO_ACTION 必须为空 | `GATE-1009` |
| V5 | `trust.trust_required` / `trust_actual` ∈ [0, 5] 整数 | `DP-1001` |
| V6 | `hypothesis.confidence`、`forecast_ref.confidence` ∈ [0, 1] | `DP-1001` |
| V7 | `expected_response_window`：`0 <= min_minutes <= max_minutes` | `DP-1001` |
| V8 | `created_at <= updated_at` | `DP-1001` |
| V9 | `domain` / `plan_mode` / `action_class` / `review_result` / `status` 使用受控枚举 | `DP-1001` |
| V10 | `tenant_id` / `shop_id` 非空 | `DP-1001` |
| V11 | `schema_version` 被校验器支持（`0.1.0` / `0.2.0` / `0.2.1`） | `DP-1001` |
| V12 | `is_no_action` 与 `review_result` 满足 DPK-I9…I12（当 `status >= Self-reviewed`） | `GATE-1006/1007/1008/1009` |

---

## 6. JSON Schema / 版本策略增量

| 项 | 值 |
|---|---|
| 新产包建议 `schema_version` | `"0.2.1"`（或继续 `"0.2.0"` 并应用本文件语义约束；**禁止**把语义校验结果写成“仍 0.1.0 全兼容”而不声明） |
| JSON Schema `$id` | `.../decision_packet/0.2.1` |
| 向后兼容 | 缺 `derivation_trace`/`applied_overlays` 仍合法（v0.2 规则） |
| 语义不兼容 | **空 `proposed_actions` 在 0.2.1 下非法**（相对 v0.1 更严）；已历史 Executed 包不回写，仅新校验 |
| Executed 包 | 核心字段仍冻结（DPK-I7）；禁止为“补齐审批语义”原地改 `review_result` |

---

## 7. 负向 Fixture 对应（契约层，非实现）

| Fixture | 输入要点 | 期望 `decision_outcome` |
|---|---|---|
| FX-01 | 正常 NO_ACTION + `NO_ACTION_APPROVE` | `SYNTHETIC_NO_ACTION` |
| FX-02 | NO_ACTION + `REJECT`/`HOLD` | `REJECT`/`HOLD`；无 approved 回执 |
| FX-03 | 普通动作 + `NO_ACTION_APPROVE` | `REJECT` |
| FX-04 | 普通动作 + `APPROVE` + Shadow | `REJECT`（`SHADOW_WRITE_FORBIDDEN`） |
| FX-13 | 空 actions | `REJECT`（Schema invalid） |
| （新）FX-19 | 全 NO_ACTION + `APPROVE` | `REJECT` |
| （新）FX-20 | 全 NO_ACTION + 缺 `no_action_reason` | `REJECT` |

---

## 8. 明确非声称

1. 本文**不**授权真实京东/抖音 API、真实凭证或 LIVE 写路径。  
2. 全部阈值、窗口、Trust 档位均为 **Proposed**，非 GA-1 理论结论，待 GA-3 验证。  
3. 本文为 **Draft 权威增量**，升格 Confirmed 须负责人评审。  
4. 与 GA-1 冲突时以 GA-1 为准；本文只收紧工程派生语义。  
5. 未在本文覆盖的字段/样例/JSON Schema 主体，以 v0.1（+v0.2）为准。

---

## 9. 待决问题增量

| ID | 问题 | v0.2.1 处理 | 阻塞 |
|---|---|---|---|
| DPK-V021-Q01 | NO_ACTION 包是否允许实现层先 `Executed` 再 `Observed` | 允许，但必须零副作用 + 合成回执标记；优先 `Self-reviewed→Observed` | 否 |
| DPK-V021-Q02 | `schema_version` 与 v0.2 的 `0.2.0` 是否强制 bump 到 `0.2.1` | 建议 bump；语义校验与版本号解耦可接受，须在 Manifest 声明 | 否 |
| DPK-V021-Q03 | 空 actions 历史包迁移 | 不回写；新包/新提交一律 V1 拒绝 | 否 |

---

## 10. 变更记录

| 日期 | 版本 | 变更 | 依据 |
|---|---|---|---|
| 2026-09-15 | v0.2.1 | 权威增量：冻结动作—审批对应表；DPK-I9…I12；`is_no_action` 形式定义；`decision_outcome`；基础校验 V1–V12；生命周期审批收紧；废止「等价 APPROVE」；声明三文件合并阅读 | 审计 §4–§5、§14；GA2-R03/R04/R05；DPK v0.1/v0.2；GIP v0.2 |

---

**Document Status:** Draft（现行权威增量）  
**Authoritative For:** Decision Packet 动作—审批语义、DPK-I9…I12、decision_outcome、Schema 语义校验  
**Full Field Tables:** 仍以 v0.1 §2 + v0.2 §1.4 合并阅读  
**Next Review:** 项目负责人 / Research Architect  
**Explicit Non-claim:** 非 Confirmed 契约；不改 GA-1；不写真实 API；阈值 Proposed。
