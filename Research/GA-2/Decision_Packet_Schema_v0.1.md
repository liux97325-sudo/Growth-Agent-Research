# GA-2：Decision Packet（决策包）Schema 与端到端样例

**文档编号：** GA-2-DPKT-001  
**版本：** v0.1  
**状态：** Draft  
**阶段：** GA-2 Engineering Design（GA2-T10）  
**输入基线：** `Research/GA-1/GA-1_Theory_v1.0.md`（GA-1.0 / v1.0，Confirmed）  
**主线架构：** `Research/GA-2/Architecture_Overview_v0.2.md`（Confirmed，GA-DEC-004）  
**关联详设：**  
- `Memory_Knowledge_Boundary_v0.1.md`（O-H-A-R-R / CausalRecord）  
- `Risk_Trust_SelfReview_v0.1.md`（门禁与审批状态机）  
- `JD_Adapter_Interface_v0.2.md`（DecisionPackage 对象与写门禁）  
- `Parameter_Genome_Templates_v0.1.md`（目标函数与调整策略引用）  
**授权依据：** `GA-DEC-004`（主线冻结 + 启动 GA2-T10）  
**作者角色：** Research Engineer 子代理  
**约束：** 仅 Schema / 契约 / 样例；不接真实广告 API；所有阈值与默认值一律 **Proposed**。

---

## 0. 范围声明

### 0.1 本轮要做

1. 把 Architecture_Overview_v0.2 §6「决策包最小契约」展开为字段级 Schema（类型、必填、来源组件、可变性、版本策略）。  
2. 定义 Decision Packet 生命周期状态机，覆盖 `Draft → Self-reviewed → Executed → Observed → Reflected → Archived/Superseded`。  
3. 给出与 Causal Memory O-H-A-R-R、Risk/Trust/Self-review、JD Adapter 对象契约的映射与冲突裁决。  
4. 定义只读影子模式变体 `shadow_decision`。  
5. 提供 2 个可序列化端到端样例与 JSON Schema 草案。

### 0.2 本轮明确不做

- 真实京东/抖音 API 调用、凭证、可执行投放脚本；  
- 存储引擎选型、消息队列协议终局；  
- GA-3 实验设计；  
- 修改 `GA-1_Theory_v1.0.md` / `PROJECT_SPEC.md`。

### 0.3 冲突裁决原则

> **以 Architecture_Overview_v0.2（GA-DEC-004 主线）为准。**  
> JD Adapter / Memory / Risk 详设与主线不一致处，在本文 §5「冲突与对齐」中标注，本文字段设计服从主线；详设后续版本应向本文靠拢。

---

## 1. 定位：成长最小原子

### 1.1 一句话

> **Decision Packet 是 Growth Agent 对外经营动作前形成的、可审计、可序列化、可追踪到因果记忆的最小成长原子。**  
> 没有 Decision Packet，回路 A（经营决策）无法接到回路 B（经验蒸馏），Trust / Knowledge 也无处附着。

### 1.2 为什么是“最小原子”

| 维度 | 含义 |
|---|---|
| **决策原子性** | 一次完整假设—动作—预期—结果—反思链路的唯一封装单元；不可拆成“只写动作不写假设”。 |
| **审计原子性** | Self-review / Risk / Trust / Adapter 门禁全部引用同一 `decision_id`，TRACE 可单点重建全链。 |
| **学习原子性** | 执行后必须回填 `outcome_ref`，并可映射为至少一条 `CausalRecord`（§4）；失败同样必须成包，禁止静默丢弃。 |
| **信任原子性** | Trust `T2/T8` 度量以 Decision Packet 为样本单位（批准后达成率、自审批准确性）。 |
| **影子原子性** | Shadow 变体仍是完整 Decision Packet，只改 `execution_mode` 与权限语义，不另造半成品对象。 |

### 1.3 在四条主回路中的位置

```text
回路 A（日内/单计划）:
  State → Forecast → Reasoning → [形成 Decision Packet Draft]
        → Risk / Trust / Self-review（写入 review_result）
        → Domain Agent（executor）→ Execute → Audit

回路 B（经验蒸馏）:
  Audit(outcome_ref) → Causal Memory(O-H-A-R-R)
        → Reflection → Experience Candidate → Quality Score

回路 C / D:
  经验/知识版本 → 反哺后续 Packet 的 knowledge_refs
  历史 Packet 达成率 → Trust Score → 更大动作半径
```

### 1.4 与相邻对象的边界

| 对象 | 关系 | 不做什么 |
|---|---|---|
| `AbstractActionRequest`（JD Adapter） | Packet 的 `proposed_actions[]` 元素；Adapter 只消费已 APPROVE 的 Packet | 不含假设/预测/风险；不可独立提交 |
| `ActionReceipt` | Packet 的 `outcome_ref` 指向 Receipt；Receipt.audit 必须回指 `decision_id` | Receipt 不是决策，不承载假设 |
| `CausalRecord` | Packet Observed/Reflected 后由 ME 写入；O-H-A-R-R 字段部分来源于 Packet | CausalRecord 不替代 Packet 的门禁字段 |
| `RiskAssessment` | Packet 的 `risk` 子对象快照 | Risk 不生成动作 |
| `ReviewEvent` | Packet 的 `review` 子对象 | SRA 不执行平台写操作 |
| Parameter Genome / Objective | Packet 通过引用锁定版本快照 | Packet 不改写基因 |

### 1.5 硬不变式（Invariants）

| ID | 不变式 | 依据 |
|---|---|---|
| DPK-I1 | 任何非 `NO_ACTION` 的对外写动作，必须携带 `lifecycle_status ∈ {Self-reviewed, Executed}` 且 `review_result=APPROVE` 的 Decision Packet。**完整可执行公式（含 Shadow 硬拒与 hard_block 空）以 `Gate_Integration_Playbook_v0.2.md` §1.1 为准**（GA-DEC-006 / 审计 C-04） | 架构 §6；GIP v0.2 §1.1；JD G-01 |
| DPK-I2 | `NO_ACTION` 合法，但**仍必须成包**并完整走过 Draft→Self-reviewed→（跳过 Executed）→Observed→Reflected | 架构 P5；JD §3.1 |
| DPK-I3 | 平台原始指标不得进入 `state_digest` / `forecast_ref`；必须引用 `TrustedBusinessState` / `ValidatedMetricSet` | 架构 P3；JD §5.3 |
| DPK-I4 | `proposed_actions[]` 为空数组仅允许 `action_class=NO_ACTION`；否则非法包 | 防“空包过门禁” |
| DPK-I5 | Shadow 模式下 Packet 永不产生平台副作用；`execution_mode=SHADOW` 时 Adapter 写路径必须硬拒绝 | GA-DEC-004 红线 |
| DPK-I6 | 失败/否决 Packet 不得物理删除；须进入 Observed 或直接 Archived 并写 reject/failure 标签 | 架构 P6 |
| DPK-I7 | 字段变更必须 bump `schema_version` 或写入 `revision` 审计；已进入 `Executed` 的核心字段（假设、动作、目标快照）不可原地覆盖，仅可追加 `corrections[]` | Memory I4 / MKB-Q08 同源 |
| DPK-I8 | 任一对外写动作的 Packet 必须最终可追溯到 ≥1 条 CausalRecord（`NO_ACTION` 与 REJECT 也建议写 Causal，允许 `action` 段为空） | Memory §5 硬规则 |

---

## 2. 完整字段 Schema

### 2.1 字段属性约定

| 列 | 含义 |
|---|---|
| 类型 | 逻辑类型，不绑定存储引擎 |
| 必填 | `Y` 全程必填；`Y@S` 仅在状态 S 起必填；`N` 可选 |
| 来源 | 主责写入组件（见文末缩写） |
| 可变性 | `F` 冻结后不可改（Executed 起）；`W` 状态内可写；`A` 仅追加；`R` 回填槽（Observed/Reflected 起可写） |
| 版本 | 是否进入版本比较 / supersede 语义 |

**组件缩写：** CBA / RE / FE / OFG / RKE / TE / SRA / JDA（JD Domain Agent）/ ADAPT / ME / RFE / LE / KE / STATE / BDV。

### 2.2 顶层字段

| 字段 | 类型 | 必填 | 来源 | 可变性 | 版本 | 说明 |
|---|---|---|---|---|---|---|
| `decision_id` | string | Y | CBA | F | 主键 | 全局唯一，前缀建议 `DP-`；架构主契约字段 |
| `schema_version` | semver | Y | CBA | F | 是 | 本文档版本对齐，如 `0.1.0` |
| `revision` | int | Y | CBA | A | 是 | 同一决策语义修订序号；`Superseded` 时新包新 id 或同 id +revision+1（见 §2.6） |
| `status` | enum | Y | CBA/SRA/执行链 | W→终态 | 否 | Packet 生命周期，见 §3；**不是** Self-review 结果 |
| `packet_kind` | enum | Y | CBA | F | 否 | `standard` / `shadow_decision` |
| `execution_mode` | enum | Y | CBA | F | 否 | `LIVE` / `SHADOW_READ_ONLY`；本轮仅允许 `SHADOW_READ_ONLY` |
| `created_at` | timestamp | Y | CBA | F | 否 | Draft 创建时间 |
| `updated_at` | timestamp | Y | 系统 | W | 否 | 最后更新 |
| `decided_at` | timestamp | N | SRA | R | 否 | Self-review 终态时间 |
| `executed_at` | timestamp | N | JDA/ADAPT | R | 否 | 首次执行提交时间 |
| `closed_at` | timestamp | N | CBA/ME | R | 否 | Archived/Superseded 时间 |
| `tenant_id` / `shop_id` | string | Y | CBA | F | 否 | 作用域；对齐 MKB-Q07 租户隔离 |
| `domain` | enum | Y | CBA | F | 否 | `JD_AD` / `DOUYIN_OPS`（抖音仅占位） |
| `episode_id` | string | Y | CBA/ME | F | 否 | 所属 Episode（Memory §3.3） |
| `parent_decision_id` | string | N | CBA | F | 否 | REVISE 重提或拆包时的上游引用 |
| `superseded_by` | string | N | CBA | R | 是 | 指向取代本包的 `decision_id` |

> **与主线对齐：** 架构 §6 的 `decision_id` 为本表主键；其余架构字段在下列子对象中展开。

### 2.3 目标与状态快照（决策输入）

| 字段 | 类型 | 必填 | 来源 | 可变性 | 版本 | 说明 |
|---|---|---|---|---|---|---|
| `objective_snapshot` | object | Y | OFG | F | 是 | **架构主契约字段**；当时目标函数快照 |
| `objective_snapshot.template_id` | string | Y | OFG | F | 是 | 如 `T-MHB-SEED` |
| `objective_snapshot.weights` | map&lt;string,number&gt; | Y | OFG | F | 是 | 六指标有序权重，Σ=1（Proposed 衰减，见 Genome §5.3） |
| `objective_snapshot.lifecycle_bias` | string | N | OFG | F | 是 | 如 `lifecycle_grow` |
| `objective_snapshot.explanation` | string | N | OFG | F | 否 | 可解释性，供 SRA |
| `objective_snapshot.valid_until` | timestamp | N | OFG | F | 否 | 权重有效期 |
| `state_digest` | object | Y | STATE/CBA | F | 否 | **架构主契约字段**；经营状态摘要 |
| `state_digest.state_id` | string | Y | STATE | F | 否 | `TrustedBusinessState.state_id` |
| `state_digest.as_of` | timestamp | Y | STATE | F | 否 | 状态时间 |
| `state_digest.hash` | string | Y | CBA | F | 否 | 关键字段摘要哈希（非整对象拷贝，对齐 Memory §3.9） |
| `state_digest.plan_mode` | enum | Y | JDA | F | 否 | `SEEDING` / `HARVEST` / `MIXED` / `UNKNOWN` |
| `state_digest.lifecycle_phase` | enum | Y | STATE | F | 否 | `explore`/`growth`/`mature`/`burst`/`decline` |
| `state_digest.inventory_risk` | enum | N | STATE | F | 否 | `OK`/`TIGHT`/`CRITICAL`/`OVERSTOCK` |
| `state_digest.budget_ref` | string | N | STATE | F | 否 | `BudgetPosition` 引用 |
| `state_digest.gap_flags` | enum[] | Y | STATE | F | 否 | 缺失即必须显式列出，禁止静默 |
| `state_digest.validation_confidence` | enum | Y | BDV | F | 否 | `HIGH`/`MEDIUM`/`LOW`；LOW 时 Reasoning 不得输出写动作 |
| `forecast_ref` | object | Y | FE | F | 否 | **架构主契约字段** |
| `forecast_ref.forecast_id` | string | Y | FE | F | 否 | 预测任务 ID |
| `forecast_ref.horizon` | string | Y | FE | F | 否 | 如 `2h` / `to_peak_window` |
| `forecast_ref.confidence` | number | Y | FE | F | 否 | [0,1]；阈值 Proposed ≥0.6 方可触发写动作 |
| `forecast_ref.summary` | object | Y | FE | F | 否 | 关键走势/预算寿命/稳定性/爆发概率摘要 |
| `forecast_ref.based_on_validated_ids` | string[] | Y | FE | F | 否 | 仅允许 `ValidatedMetricSet` 引用 |
| `knowledge_refs` | object[] | N | KE | F | 否 | 命中的 Rule/Strategy/Genome/Experience 版本锁定 |
| `genome_ref` | string | N | KE | F | 否 | Parameter Genome `id@version` |
| `working_context_id` | string | N | ME | F | 否 | `WorkingContext` 引用 |

### 2.4 假设与动作（决策内容）

| 字段 | 类型 | 必填 | 来源 | 可变性 | 版本 | 说明 |
|---|---|---|---|---|---|---|
| `hypothesis` | object | Y | RE | F | 否 | **架构主契约字段**；观察→假设 |
| `hypothesis.observation` | object | Y | RE | F | 否 | 现象、指标、时间窗、对比基线；对齐 CausalRecord.observation |
| `hypothesis.cause_claim` | string | Y | RE | F | 否 | 原因判断（自然语言或结构化码） |
| `hypothesis.confidence` | number | Y | RE | F | 否 | [0,1] |
| `hypothesis.supporting_signals` | object[] | N | RE | F | 否 | 支撑信号 |
| `hypothesis.rival_hypotheses` | string[] | N | RE | F | 否 | 备择假设 |
| `hypothesis.knowledge_basis` | string[] | N | RE | F | 否 | 命中知识对象 ID |
| `proposed_actions` | object[] | Y | RE→CBA | F | 否 | **架构主契约字段**；见 §2.5 |
| `expected_response_window` | object | Y | RE/FE | F | 否 | 调整响应窗口（§8.6） |
| `expected_response_window.min_minutes` | int | Y | RE | F | 否 | Proposed 先验见 Genome §6.4 |
| `expected_response_window.max_minutes` | int | Y | RE | F | 否 | |
| `expected_response_window.metric_hint` | string[] | Y | RE | F | 否 | 预期响应指标 |
| `expected_effect` | object | N | RE/FE | F | 否 | 预测指标方向与幅度；供 Observed 对照 |
| `no_action_reason` | string | N | RE | F | 否 | 当且仅当动作类为 `NO_ACTION` 时必填 |

### 2.5 `proposed_actions[]` 元素（对齐 JD AbstractActionRequest）

| 字段 | 类型 | 必填 | 来源 | 可变性 | 说明 |
|---|---|---|---|---|---|
| `action_id` | string | Y | RE | F | 包内唯一，前缀 `ACT-` |
| `action_type` | enum | Y | RE | F | `WA-BID-01`…`WA-CLS-01`（NoAction）等；平台语义动作，非 API 名 |
| `action_class` | enum | Y | RE | F | `KEYWORD_BID` / `AUDIENCE_PREMIUM` / `BUDGET` / `ROI_TARGET` / `PLAN_CONTROL` / `CREATE_PLAN` / `NO_ACTION` |
| `target` | object | Y | RE | F | `campaign_id` / `plan_id` / `unit_id` / `keyword_id` / `audience_id` 等 |
| `change` | object | Y* | RE | F | 字段、from、to、relative_pct；`NO_ACTION` 时省略 |
| `priority` | int | N | RE | F | 同包内执行序（默认 1） |
| `rationale_ref` | string | Y | RE | F | 指向 hypothesis / evidence |
| `risk_per_action` | object | N | RKE | F | 动作级风险覆盖（可被包级 `risk` 吸收） |
| `shadow_preview` | object | N | RE | F | 仅 `shadow_decision`：若执行预期参数轨迹 |

\* `NO_ACTION` 除外。

### 2.6 门禁与审批（衔接 Risk / Trust / Self-review）

| 字段 | 类型 | 必填 | 来源 | 可变性 | 版本 | 说明 |
|---|---|---|---|---|---|---|
| `risk` | object | Y@Draft 末 | RKE | F | 否 | **架构主契约 `risk_grade` 展开** |
| `risk.risk_level` | enum | Y | RKE | F | 否 | `R0`…`R4` |
| `risk.hard_block` | string[] | Y | RKE | F | 否 | 非空则禁止 APPROVE |
| `risk.constraints` | object | Y | RKE | F | 否 | 幅度/频率/探索预算/`min_response_window` 等 |
| `risk.reason_codes` | string[] | Y | RKE | F | 否 | |
| `risk.baseline_version` | string | Y | RKE | F | 否 | 风险基线版本 |
| `trust` | object | Y | TE | F | 否 | **架构主契约 trust_required / trust_actual** |
| `trust.trust_required` | int | Y | TE/SRA | F | 否 | 0–5；动作所需最低档 |
| `trust.trust_actual` | int | Y | TE | F | 否 | 决策时实际 Trust Level |
| `trust.trust_score_snapshot` | number | N | TE | F | 否 | 决策时 TS（0–100） |
| `trust.version` | string | N | TE | F | 否 | Trust 版本 |
| `review` | object | Y@Self-reviewed | SRA | A | 否 | **架构主契约 `review_result` 展开** |
| `review.review_result` | enum | Y | SRA | A | 否 | `APPROVE` / `REVISE` / `HOLD` / `REJECT` / `ESCALATE_HUMAN` / `NO_ACTION_APPROVE` |
| `review.approved_by` | enum | Y | SRA | A | 否 | `AGENT` / `HUMAN` |
| `review.predicate_trace` | object[] | Y | SRA | A | 否 | `CHK_*` 谓词 pass/fail/unknown |
| `review.reason_codes` | string[] | Y | SRA | A | 否 | |
| `review.revise_round` | int | N | SRA | A | 否 | 修订轮次；上限 Proposed `N_revise=2` |
| `review.human_ticket_id` | string | N | SRA | A | 否 | ESCALATE 时 |
| `review.review_event_id` | string | Y | SRA | A | 否 | TRACE ReviewEvent 引用 |
| `executor` | enum/string | Y@Executed | CBA/JDA | F | 否 | **架构主契约字段**；Domain Agent ID（如 `JDA-01`） |
| `adapter_runtime_mode` | enum | N | ADAPT | F | 否 | `FIXTURE_ONLY` / `SIMULATION` / … 本轮仅前两者 |

### 2.7 执行、结果与反思（回填槽）

| 字段 | 类型 | 必填 | 来源 | 可变性 | 版本 | 说明 |
|---|---|---|---|---|---|---|
| `action_receipts` | object[] | Y@Executed | ADAPT/JDA | A | 否 | 与 `proposed_actions` 一一对应；`NO_ACTION` 可写合成 Receipt |
| `action_receipts[].receipt_id` | string | Y | ADAPT | A | 否 | |
| `action_receipts[].action_id` | string | Y | ADAPT | A | 否 | 对应包内动作 |
| `action_receipts[].status` | enum | Y | ADAPT | A | 否 | `ACCEPTED` / `REJECTED_BY_GATE` / `REJECTED_BY_PLATFORM` / `TIMEOUT` / `UNKNOWN` / `SIMULATED` / `NOT_APPLICABLE_NO_ACTION` |
| `action_receipts[].platform_ack_ref` | string | N | ADAPT | A | 否 | 本轮 Fixture 模拟 |
| `action_receipts[].idempotency_key` | string | Y | ADAPT | A | 否 | |
| `action_receipts[].submitted_at` | timestamp | Y | ADAPT | A | 否 | |
| `outcome_ref` | object | Y@Observed | JDA/ME | R | 否 | **架构主契约字段**；执行后回填 |
| `outcome_ref.receipt_ids` | string[] | Y | JDA | R | 否 | |
| `outcome_ref.observed_at` | timestamp | Y | JDA | R | 否 | 响应窗口到期或提前触发 |
| `outcome_ref.metrics_delta` | object | N | BDV/STATE | R | 否 | 校验后指标对比（禁止用未校验平台口径） |
| `outcome_ref.met_prediction` | enum | N | JDA/RFE | R | 否 | `fully` / `partially` / `no` / `not_applicable` |
| `outcome_ref.side_effects` | string[] | N | JDA | R | 否 | |
| `outcome_ref.validation_report_ref` | string | Y | BDV | R | 否 | 结果必须过 BDV |
| `causal_ids` | string[] | N | ME | R | 否 | 生成的 CausalRecord ID 列表 |
| `reflection_ref` | object | N | RFE | R | 否 | **架构主契约字段**；复盘后回填 |
| `reflection_ref.session_id` | string | Y | RFE | R | 否 | ReflectionSession |
| `reflection_ref.finding_ids` | string[] | N | RFE | R | 否 | |
| `reflection_ref.outcome_label` | enum | N | RFE | R | 否 | `success` / `failure` / `neutral` / `pending` |
| `corrections` | object[] | N | RFE/人工 | A | 否 | 只追加，不覆盖历史 |
| `tags` | string[] | N | 任意 | A | 否 | 如 `failure_pattern_candidate` / `shadow` / `activity_window` |

### 2.8 字段来源汇总（架构 §6 主契约对照）

| 架构字段 | 本文落点 |
|---|---|
| decision_id | `decision_id` |
| objective_snapshot | `objective_snapshot` |
| state_digest | `state_digest` |
| forecast_ref | `forecast_ref` |
| hypothesis | `hypothesis` |
| proposed_actions[] | `proposed_actions[]` |
| risk_grade | `risk.risk_level` |
| trust_required / trust_actual | `trust.trust_required` / `trust.trust_actual` |
| review_result | `review.review_result` |
| executor | `executor` |
| outcome_ref | `outcome_ref` |
| reflection_ref | `reflection_ref` |

### 2.9 版本与可变性策略（汇总）

| 阶段 | 允许写入 | 禁止 |
|---|---|---|
| Draft | 全部输入字段；`status` 流转 | 伪造 validation 为 PASS |
| Self-reviewed 追加 | `review.*`、`risk.*` 只读锁定后写入审批结果 | 篡改已锁定 hypothesis/actions/objective |
| Executed | `action_receipts[]` 追加、`executor` | 改动作参数；改目标权重 |
| Observed | `outcome_ref`、`causal_ids` | 用未校验指标填写 metrics_delta |
| Reflected | `reflection_ref`、`corrections[]`、`tags` | 直接改写 observation/action/result |
| Archived / Superseded | 仅状态与 `superseded_by` / `closed_at` | 物理删除；无审计替换 |

**Supersede 规则：**  
1. 仅在 `Revise` 重提且语义等价修正时，可选择同 `decision_id` + `revision+1`（保留 lineage）。  
2. 若假设或动作对象发生实质变化，必须新 `decision_id`，旧包 `status=Superseded`，`superseded_by` 指向新包。  
3. 已 `Executed` 的包**不得** Supersede 为“从未发生”；只能 Reflected→Archived，并在新包中引用。

---

## 3. 状态机

### 3.1 状态定义

| 状态 | 含义 | 进入条件 | 允许的主责写入者 |
|---|---|---|---|
| `Draft` | 决策包已形成，门禁未完成 | CBA/RE 完成字段组装，Risk/Trust 预检可已填 | CBA / RE |
| `Self-reviewed` | 审批终态已写入 | `review.review_result` 非空；Risk/Trust 锁定 | SRA |
| `Executed` | 已进入执行通道 | `review_result=APPROVE` 或 `NO_ACTION_APPROVE`；ActionReceipt 已产生或 NO_ACTION 合成回执 | JDA / ADAPT |
| `Observed` | 结果已回填 | 响应窗口到期或事件触发；`outcome_ref` 完整 | JDA / ME / BDV |
| `Reflected` | 复盘已挂接 | ReflectionSession 覆盖本 decision | RFE |
| `Archived` | 终态封存 | Reflected 完成，或 REJECT/HOLD 超时，或失败包归档 | CBA / ME |
| `Superseded` | 被新决策包取代 | `superseded_by` 非空 | CBA |

### 3.2 状态迁移图

```text
                    ┌──────────────────────────────────────────┐
                    │                 Draft                     │
                    │  (RE 形成包；Risk/Trust 预检)              │
                    └───────────────────┬──────────────────────┘
                                        │ SRA 完成终审
                 ┌──────────────────────┼──────────────────────┐
                 │                      │                      │
                 ▼                      ▼                      ▼
          review=APPROVE /       review=REVISE           review=HOLD /
          NO_ACTION_APPROVE      (revision+1 回 Draft)   REJECT / ESCALATE
                 │                      │                      │
                 │                      │              ┌───────┴────────┐
                 │                      │              │                │
                 │                      │         人类 APPROVE     超时/否决
                 │                      │              │                │
                 ▼                      ▼              ▼                ▼
             Executed ◄───────── (重提后再次审批)   Executed        Archived
                 │                                     │           (Reject Pattern)
                 │ 响应窗口到期 / 结果就绪
                 ▼
             Observed
                 │ Reflection 触发
                 ▼
             Reflected
                 │
         ┌───────┴───────┐
         ▼               ▼
     Archived      Superseded ──► 新 Decision Packet
```

### 3.3 迁移规则表

| 从 → 到 | 条件 | 审计 |
|---|---|---|
| Draft → Self-reviewed | `review.review_result ∈ {APPROVE, NO_ACTION_APPROVE, REVISE, HOLD, REJECT, ESCALATE_HUMAN}` 已写入 | `review.review_event_id` |
| Self-reviewed → Draft | `REVISE` 且 `revise_round < N_revise`（Proposed=2） | `parent_decision_id` 或 `revision+1` |
| Self-reviewed → Archived | `REJECT`；或 `HOLD` 超时 `T_hold_max`（Proposed，待 GA2-T07）；或 `ESCALATE` 后 `HUMAN_REJECT` | reject reason_codes；失败样本标签 |
| Self-reviewed → Executed | `APPROVE` 且非 Shadow 写路径；或 `NO_ACTION_APPROVE`；或 `HUMAN_APPROVE/HUMAN_MODIFY` | ActionReceipt / NO_ACTION 合成回执 |
| Executed → Observed | `expected_response_window` 到期或指标事件提前触发；`outcome_ref` 必填 | BDV validation_report |
| Observed → Reflected | RFE 周期任务或事件任务覆盖本 decision | ReflectionSession/Finding |
| Observed → Archived | 可选：超长未复盘包强制归档（仍可后补 Reflected 追加 finding） | 归档原因 |
| Reflected → Archived | 默认终态 | closed_at |
| 任意非终态 → Superseded | 新包创建且语义取代 | superseded_by |
| Executed → Superseded | **禁止**“无痕取代”；只能经 Reflected/Archived 后，由新包引用旧包 | DPK-I7 |

### 3.4 与 Self-review 审批状态机的关系

| Decision Packet `status` | Self-review `review_result` | 说明 |
|---|---|---|
| Draft | 空 / 进行中 | 对应 SRA 的 Submitted/RiskGate/TrustGate/ReviewEval 过程态 |
| Self-reviewed | APPROVE / NO_ACTION_APPROVE | 可进入 Executed |
| Self-reviewed | REVISE | 回到 Draft（或 revision+1） |
| Self-reviewed | HOLD | 挂起，状态可保持 Self-reviewed 或新增子态（本文用 tags + decided_at 记录，Proposed） |
| Self-reviewed → Archived | REJECT / ESCALATE→HUMAN_REJECT | 不执行 |
| Self-reviewed → Executed | ESCALATE→HUMAN_APPROVE/MODIFY | 人工放行后执行 |
| Executed 及之后 | 审批结果不再变更（只读） | T8 样本锁定 |

> **命名消歧：** JD Adapter `DecisionPackage.status` 枚举（DRAFT/PENDING_REVIEW/APPROVE/…）实际混用了包生命周期与审批结果。**本文以主线为准拆成两个字段：`status`（生命周期）+ `review.review_result`（审批）。** JD Adapter 后续应映射为 `review_result`，见 §5。

---

## 4. 与 Causal Memory O-H-A-R-R 的映射

### 4.1 映射表

| O-H-A-R-R | CausalRecord 字段 | Decision Packet 来源字段 | 说明 |
|---|---|---|---|
| **O**bservation | `observation` | `hypothesis.observation` + `state_digest` + `forecast_ref.summary` | 观察必须锚定 Trusted State，不得用 Raw |
| **H**ypothesis | `hypothesis` | `hypothesis.cause_claim/confidence/supporting_signals/rival_hypotheses` | 含置信度与备择 |
| **A**ction | `action` | `proposed_actions[]` + `action_receipts[]` + `executor` | `NO_ACTION` 时 `action` 可写 `type=NO_ACTION` 且参数空 |
| **R**esult（预期） | `expected_effect` | `expected_effect` + `expected_response_window` | 工程扩展段，理论 O-H-A-R-R 中的“预期” |
| **R**esult（实际） | `result` | `outcome_ref` | 必须 BDV 后指标 |
| **R**eflection | `reflection` | `reflection_ref` + Reflected 阶段补充文本（由 RFE/LE） | Packet 只存引用与标签；叙述在 Reflection/Causal |

> 理论写作 O-H-A-R-R（两 R 分别对应 Result 与 Reflection）；工程上 `expected_effect` 作为独立段，与 Memory_Knowledge_Boundary §5 一致。

### 4.2 写入时序

```text
Draft/Self-reviewed/Executed
    → ME 可预写 CausalRecord 骨架（O+H+expected，action 状态=pending）
Observed
    → ME 回填 A 回执 + R(result)；evidence_refs 含 receipt_id / outcome_ref
Reflected
    → ME/RFE 回填 reflection；knowledge_note 初判（非正式晋升）
    → packet.causal_ids ← [CR-...]
```

### 4.3 一致性约束

1. 一条 Decision Packet 默认对应 Episode 内**一条**主 CausalRecord（`seq` 连续）；复杂多动作包可一动作一 CR，`packet.causal_ids` 多值。  
2. `NO_ACTION` 仍写 CR：`action.type=NO_ACTION`，`result` 记录“维持基线是否符合预测”，用于稳定性质检与 T2 样本。  
3. REJECT 包：写 CR 骨架 + `result` 为空动作拒绝说明；Learning 可生成 Reject Pattern。  
4. Shadow 包：写入独立观测池或 `visibility=internal` + `tags=["shadow"]`，**默认不进入企业规则蒸馏主池**（Proposed，见 JD-Q10 同类污染风险）。

---

## 5. 与 Trust / Risk / Self-review 字段的衔接

### 5.1 衔接矩阵

| 详设对象 | 字段进入 Packet 的方式 | 消费时机 |
|---|---|---|
| RiskAssessment | 深拷贝为 `risk.*`（含 baseline_version） | Draft 末；SRA 与 ADAPT G-03 |
| Trust Score/Level | `trust.trust_required/actual` + 可选 score 快照 | Draft；SRA；ADAPT G-02 |
| ReviewEvent | `review.review_event_id` + predicate_trace 摘要 | Self-reviewed 进入时 |
| AbstractActionRequest | 由 `proposed_actions[]` 生成；回指 `decision_package_id=decision_id` | Executed / ADAPT 写路径 |
| ActionReceipt | 写入 `action_receipts[]`；Receipt.audit.decision_id=本包 | Executed |
| Trust 更新样本 | 整包作为 T2/T8 样本 ID | 周期 Reflection 后 TE |

### 5.2 门禁顺序在 Packet 上的体现

```text
1. RE 填充 hypothesis/proposed_actions
2. RKE 写入 risk（含 hard_block）
3. TE 写入 trust_required/actual
4. SRA 写入 review（若 REVISE → 回 Draft）
5. CBA 下发 JDA：必须 status≥Self-reviewed 且 review_result 允许执行
6. ADAPT 二次硬闸 G-01..G-09（引用 decision_id，不信任仅内存对象）
```

### 5.3 `NO_ACTION` 专用路径

| 步骤 | 行为 |
|---|---|
| RE | `proposed_actions=[{action_type:"WA-CLS-01", action_class:"NO_ACTION"}]`；填写 `no_action_reason` |
| SRA | 谓词含 `CHK_STAB`；结果 `NO_ACTION_APPROVE`（或等价 APPROVE + action_class=NO_ACTION） |
| JDA/ADAPT | **不调用**平台写接口；生成 `NOT_APPLICABLE_NO_ACTION` 合成 Receipt |
| ME | 仍写 CausalRecord |
| RFE | 评估“不调整是否正确”，计入稳定性与 T8 |

---

## 6. 冲突与对齐（相对主线）

| 冲突点 | 主线/相关详设 | 裁决 |
|---|---|---|
| Packet 状态枚举 | 架构无展开；JD 用审批枚举当 status；任务要求生命周期六态 | **采用生命周期 `status` + 独立 `review.review_result`** |
| JD DecisionPackage 缺 forecast/state_digest/outcome 完整链 | JD §4.8 较薄 | **以本文扩展为准**；JD 后续应引用本 Schema |
| risk_grade vs risk_level | 架构用 grade，Risk 详设用 R0–R4 level | 统一 `risk.risk_level`，grade 作展示别名 |
| Shadow 是否也算 Decision Packet | M5 只说 shadow mode 设计稿 | **是同一对象 + `packet_kind=shadow_decision`**，不另造类型 |
| `NO_ACTION` 是否必须 SRA | Risk 详设称不触发执行门禁 | **仍须 SRA 走 `NO_ACTION_APPROVE`**，保证审计与 T8 样本完整；无平台写故无 ADAPT 写门禁 |
| 一包多动作的 Receipt 对齐 | JD 未强制 | `action_receipts` 与 `proposed_actions` 按 `action_id` 对齐，允许部分失败标记 |

---

## 7. 只读影子模式变体（`shadow_decision`）

### 7.1 定位

在 **GA-DEC-004「Shadow / 只读优先」** 红线下，系统仍完整走“状态→预测→推理→风险→信任→自审→（模拟）执行→观察→反思”，但**绝不改变平台状态**。Shadow Decision Packet 是 GA-3 验证前的可观测钩子。

### 7.2 与 standard 差异表

| 维度 | standard | shadow_decision |
|---|---|---|
| `packet_kind` | `standard` | `shadow_decision` |
| `execution_mode` | `LIVE`（本轮禁止） | `SHADOW_READ_ONLY`（本轮唯一允许） |
| Trust 门槛 | 按动作类 L0–L5 | 可在 L0 运行（只提供建议）；建议仍写 `trust_required` 作反事实 |
| SRA | 终审后可执行 | **仍强制跑 SRA**，用于校准审批策略（反事实 APPROVE 率） |
| ADAPT 写 | 按 G-01..G-09 | **写路径硬失败**；最多生成 `SIMULATED` Receipt |
| Memory 池 | 主因果池 | `tags=["shadow"]`；Learning 默认隔离或降权（Proposed） |
| Trust 计分 | 计入 T2/T8 | **默认不计入** Trust（无真实结果）；仅进 shadow 校准集（Proposed） |
| 对用户/经营可见性 | 执行结果可感知 | 仅审计与报告；人类可浏览“若执行会怎样” |
| NO_ACTION | 合法 | 同样合法，且更应鼓励 |

### 7.3 Shadow 包附加字段

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `shadow.config_id` | string | Y | 影子运行配置引用 |
| `shadow.counterfactual_receipt` | object | N | 模拟回执（status 固定 `SIMULATED`） |
| `shadow.compare_to_live_decision_id` | string | N | 与人类/其他系统真实决策对照时填写 |
| `shadow.learning_pool` | enum | Y | `isolated` / `downweighted_main`（默认 `isolated`，Proposed） |

### 7.4 Shadow 不变式

1. DPK-I5：`execution_mode=SHADOW_READ_ONLY` ⇒ ADAPT.write 必须返回 `REJECTED_BY_GATE` 或不装配。  
2. 不得把 Shadow 包表述为“平台已执行”。  
3. Shadow 包仍满足 DPK-I1 的成包与审计要求（否则影子无效）。

---

## 8. 端到端样例

> 样例为设计 Fixture，对应 JD §2.4 `FX-01` / `FX-02`。数值均为 **Proposed / 示意**，非企业真值。  
> 本轮 `execution_mode` 均为 `SHADOW_READ_ONLY`；为展示完整生命周期，标准包标注“若未来 LIVE 的等价路径”。

### 8.1 样例 A：种草计划上午获量下滑 → 提前干预（对应 FX-01）

**场景摘要**

- 商品：中高客单品牌款；计划 `plan_mode=SEEDING`；生命周期 `growth`。  
- 现象：上午 09:00–11:00 展现与点击同步显著低于近 7 日同时段基线。  
- 团队目标权重模板：`T-MHB-SEED`。  
- 库存 OK；无活动冲突；Trust Level=2；无硬红线。

**决策意图：** 假设“关键词竞争增强导致展现能力下降”，提议核心词出价 +12%（在 R2/L2 幅度内），预期 2–6h 展现与点击回升。

#### A.1 关键 Packet 片段（JSON，节选）

```json
{
  "decision_id": "DP-JD-20260911-0001",
  "schema_version": "0.1.0",
  "revision": 1,
  "status": "Reflected",
  "packet_kind": "standard",
  "execution_mode": "SHADOW_READ_ONLY",
  "domain": "JD_AD",
  "tenant_id": "TEN-DEMO",
  "shop_id": "SHOP-DEMO-01",
  "episode_id": "EP-DEMO-0007",
  "created_at": "2026-09-11T11:10:00+08:00",
  "decided_at": "2026-09-11T11:12:30+08:00",
  "executed_at": "2026-09-11T11:12:40+08:00",
  "closed_at": null,

  "objective_snapshot": {
    "template_id": "T-MHB-SEED",
    "weights": {
      "ctr": 0.31, "clicks": 0.23, "add_cart": 0.17,
      "impressions": 0.13, "cpc": 0.10, "gmv_roi": 0.06
    },
    "lifecycle_bias": "lifecycle_grow",
    "explanation": "中高客单×种草×成长放量：触达与点击优先，ROI 权重低",
    "valid_until": "2026-09-12T00:00:00+08:00"
  },

  "state_digest": {
    "state_id": "STATE-20260911-1100",
    "as_of": "2026-09-11T11:00:00+08:00",
    "hash": "sha256:8f3c…a1",
    "plan_mode": "SEEDING",
    "lifecycle_phase": "growth",
    "inventory_risk": "OK",
    "budget_ref": "BUD-PLAN-8821",
    "gap_flags": [],
    "validation_confidence": "HIGH"
  },

  "forecast_ref": {
    "forecast_id": "FC-20260911-1030-01",
    "horizon": "to_18:00",
    "confidence": 0.72,
    "summary": {
      "impression_trend": "down_vs_baseline",
      "ctr_trend": "down",
      "budget_lifetime": "adequate",
      "risk_note": "无爆发窗口冲突"
    },
    "based_on_validated_ids": ["VM-20260911-0900", "VM-20260911-1100"]
  },

  "genome_ref": "JD-MHB-SEED-GROW@0.1.0",

  "hypothesis": {
    "observation": {
      "window": {"start": "2026-09-11T09:00:00+08:00", "end": "2026-09-11T11:00:00+08:00"},
      "metric": "impressions|clicks|ctr",
      "delta": "impressions -38%, clicks -35%, ctr -5% vs 7d same-slot",
      "baseline_ref": "BASE-7D-SLOT",
      "peer_comparison": "同店种草计划簇中位数亦下滑但更缓",
      "state_id": "STATE-20260911-1100"
    },
    "cause_claim": "核心关键词竞争增强，展现能力下降",
    "confidence": 0.68,
    "supporting_signals": ["类目竞价压力上升", "核心词排名份额下降"],
    "rival_hypotheses": ["素材疲劳", "人群包过窄", "平台延迟"],
    "knowledge_basis": ["KO-experience-012@v2"]
  },

  "proposed_actions": [
    {
      "action_id": "ACT-001",
      "action_type": "WA-BID-01",
      "action_class": "KEYWORD_BID",
      "target": {"plan_id": "PLAN-8821", "keyword_id": "KW-core-001"},
      "change": {"field": "bid", "from_value": 4.20, "to_value": 4.70, "relative_pct": 0.12},
      "priority": 1,
      "rationale_ref": "hypothesis#cause_claim"
    }
  ],

  "expected_response_window": {
    "min_minutes": 120,
    "max_minutes": 360,
    "metric_hint": ["impressions", "clicks"]
  },
  "expected_effect": {
    "direction": "recover",
    "metric_targets": {"impressions": ">= baseline * 0.85", "ctr": ">= baseline * 0.95"}
  },

  "risk": {
    "risk_level": "R2",
    "hard_block": [],
    "constraints": {
      "max_bid_delta_pct": 0.15,
      "max_budget_delta_pct": 0.10,
      "max_daily_adjust_count": 4,
      "min_response_window_minutes": 120,
      "allow_new_plan": false,
      "review_mode": "STANDARD"
    },
    "reason_codes": ["SEEDING_PLAN", "INTRADAY_DROP", "LIFECYCLE_GROWTH"],
    "baseline_version": "RB-2026W37-01"
  },

  "trust": {
    "trust_required": 2,
    "trust_actual": 2,
    "trust_score_snapshot": 66.0,
    "version": "TR-2026W36"
  },

  "review": {
    "review_result": "APPROVE",
    "approved_by": "AGENT",
    "predicate_trace": [
      {"id": "CHK_MODEL", "result": "pass"},
      {"id": "CHK_RISK", "result": "pass"},
      {"id": "CHK_INV", "result": "pass"},
      {"id": "CHK_BUD", "result": "pass"},
      {"id": "CHK_LC", "result": "pass"},
      {"id": "CHK_GOAL", "result": "pass"},
      {"id": "CHK_CONF", "result": "pass"},
      {"id": "CHK_WINDOW", "result": "pass"},
      {"id": "CHK_AMP", "result": "pass", "detail": "12% <= 15%"},
      {"id": "CHK_TRUST", "result": "pass"}
    ],
    "reason_codes": [],
    "revise_round": 0,
    "review_event_id": "REV-20260911-0001"
  },

  "executor": "JDA-01",
  "adapter_runtime_mode": "FIXTURE_ONLY",

  "action_receipts": [
    {
      "receipt_id": "RCPT-SIM-0001",
      "action_id": "ACT-001",
      "status": "SIMULATED",
      "platform_ack_ref": "FX-01",
      "idempotency_key": "DP-JD-20260911-0001:ACT-001",
      "submitted_at": "2026-09-11T11:12:40+08:00",
      "audit": {"decision_id": "DP-JD-20260911-0001", "causal_memory_pending": true}
    }
  ],

  "outcome_ref": {
    "receipt_ids": ["RCPT-SIM-0001"],
    "observed_at": "2026-09-11T15:00:00+08:00",
    "metrics_delta": {
      "impressions": "+22% vs 11:00",
      "clicks": "+18%",
      "ctr": "flat_to_slightly_up"
    },
    "met_prediction": "partially",
    "side_effects": ["cpc 上行约 6%"],
    "validation_report_ref": "VR-20260911-1500"
  },

  "causal_ids": ["CR-20260911-0001"],

  "reflection_ref": {
    "session_id": "RFS-2026W37",
    "finding_ids": ["RFI-0003"],
    "outcome_label": "success"
  },

  "corrections": [],
  "tags": ["shadow", "seeding", "intraday_intervention", "FX-01"]
}
```

#### A.2 生命周期时间线

| 时间 | status | 事件 |
|---|---|---|
| 11:10 | Draft | RE 成包；FE/RKE/TE 预检 |
| 11:12 | Self-reviewed | SRA APPROVE（T2/L2，幅度 12%≤15%） |
| 11:12 | Executed | SHADOW：SIMULATED Receipt，平台无写 |
| 15:00 | Observed | 响应窗内展现回升，部分符合预期；BDV 后指标 |
| 周反思后 | Reflected | 记为 success；候选经验“种草上午展现点击双降时优先查词竞争/出价” |

#### A.3 O-H-A-R-R 对照

| 段 | 样例内容 |
|---|---|
| O | 上午展现 -38%、点击 -35% |
| H | 关键词竞争增强 |
| A | 核心词出价 +12%（shadow 模拟） |
| R预期 | 2–6h 展现/点击回升 |
| R实际 | 3.8h 后展现 +22%，部分符合 |
| R反思 | 种草获量下滑优先恢复竞争力，而非先降 ROI 考核 |

---

### 8.2 样例 B：收割计划稳定性优先 → 输出 NO_ACTION（对应 FX-02）

**场景摘要**

- 商品：中高客单；计划 `plan_mode=HARVEST`，`system_managed=true`；生命周期 `mature`。  
- 现象：当日 ROI 在基线带内波动，预测小幅上修空间 < 噪声阈值。  
- 目标模板：`T-MHB-HARVEST`；`prefer_stability=true`；Trust=3；Risk=R0–R1。

**决策意图：** 显式输出 `NO_ACTION`，避免破坏系统学习与稳定性。

#### B.1 关键 Packet 片段（JSON，节选）

```json
{
  "decision_id": "DP-JD-20260911-0002",
  "schema_version": "0.1.0",
  "revision": 1,
  "status": "Reflected",
  "packet_kind": "standard",
  "execution_mode": "SHADOW_READ_ONLY",
  "domain": "JD_AD",
  "shop_id": "SHOP-DEMO-01",
  "episode_id": "EP-DEMO-0008",

  "objective_snapshot": {
    "template_id": "T-MHB-HARVEST",
    "weights": {
      "gmv_roi": 0.31, "add_cart": 0.23, "ctr": 0.17,
      "clicks": 0.13, "cpc": 0.10, "impressions": 0.06
    },
    "explanation": "中高客单×收割×成熟：成交与稳定性优先"
  },

  "state_digest": {
    "state_id": "STATE-20260911-1400",
    "plan_mode": "HARVEST",
    "lifecycle_phase": "mature",
    "inventory_risk": "OK",
    "gap_flags": [],
    "validation_confidence": "HIGH"
  },

  "forecast_ref": {
    "forecast_id": "FC-20260911-1330-02",
    "horizon": "to_day_end",
    "confidence": 0.80,
    "summary": {
      "roi_band": "within_baseline",
      "improvement_if_adjust": "below_noise_threshold",
      "stability_score": "high"
    },
    "based_on_validated_ids": ["VM-20260911-1400"]
  },

  "genome_ref": "JD-MHB-HARVEST-MATURE@0.1.0",

  "hypothesis": {
    "observation": {
      "metric": "trusted_roi",
      "delta": "within p40–p60 of 14d band; no material deterioration",
      "baseline_ref": "BASE-14D"
    },
    "cause_claim": "系统托管学习中；当前波动属正常噪声，无显著恶化证据",
    "confidence": 0.77,
    "rival_hypotheses": ["人群衰弱（证据不足）"]
  },

  "proposed_actions": [
    {
      "action_id": "ACT-001",
      "action_type": "WA-CLS-01",
      "action_class": "NO_ACTION",
      "target": {"plan_id": "PLAN-9012"},
      "priority": 1,
      "rationale_ref": "stability_first"
    }
  ],

  "no_action_reason": "CHK_STAB：成熟收割+prefer_stability，预测改进小于噪声阈值；避免打断系统学习（架构 P5 / Risk §7.2(4)）",

  "expected_response_window": {
    "min_minutes": 0,
    "max_minutes": 1440,
    "metric_hint": ["trusted_roi", "spend"]
  },

  "risk": {
    "risk_level": "R1",
    "hard_block": [],
    "constraints": {
      "max_bid_delta_pct": 0.10,
      "max_daily_adjust_count": 1,
      "min_response_window_minutes": 1440,
      "allow_new_plan": false,
      "review_mode": "LITE"
    },
    "reason_codes": ["HARVEST_STABLE"],
    "baseline_version": "RB-2026W37-01"
  },

  "trust": {
    "trust_required": 0,
    "trust_actual": 3,
    "trust_score_snapshot": 74.5
  },

  "review": {
    "review_result": "NO_ACTION_APPROVE",
    "approved_by": "AGENT",
    "predicate_trace": [
      {"id": "CHK_STAB", "result": "pass", "detail": "stability preferred"},
      {"id": "CHK_CONF", "result": "pass"},
      {"id": "CHK_RISK", "result": "pass"},
      {"id": "CHK_TRUST", "result": "pass"}
    ],
    "review_event_id": "REV-20260911-0002"
  },

  "executor": "JDA-01",

  "action_receipts": [
    {
      "receipt_id": "RCPT-NOACT-0002",
      "action_id": "ACT-001",
      "status": "NOT_APPLICABLE_NO_ACTION",
      "idempotency_key": "DP-JD-20260911-0002:ACT-001",
      "submitted_at": "2026-09-11T14:01:00+08:00",
      "audit": {"decision_id": "DP-JD-20260911-0002", "causal_memory_pending": true}
    }
  ],

  "outcome_ref": {
    "receipt_ids": ["RCPT-NOACT-0002"],
    "observed_at": "2026-09-11T23:30:00+08:00",
    "metrics_delta": {"trusted_roi": "day-end within baseline band"},
    "met_prediction": "fully",
    "validation_report_ref": "VR-20260911-2330"
  },

  "causal_ids": ["CR-20260911-0002"],

  "reflection_ref": {
    "session_id": "RFS-2026W37",
    "finding_ids": ["RFI-0004"],
    "outcome_label": "success"
  },

  "tags": ["shadow", "harvest", "no_action", "FX-02"]
}
```

#### B.2 为何仍要成包

1. **审计：** 证明系统“有意识地选择不动”，而不是漏检。  
2. **信任：** 正确的 NO_ACTION 支撑 T3 风险控制与 T8 审批准确性。  
3. **学习：** 稳定性样本进入 RFE，校准噪声阈值与 `prefer_stability`。  
4. **对齐：** 架构 P5 与 JD `WA-CLS-01` 一等公民。

#### B.3 与样例 A 的对照

| 维度 | A 种草干预 | B 收割 NO_ACTION |
|---|---|---|
| plan_mode | SEEDING | HARVEST |
| 动作类 | KEYWORD_BID | NO_ACTION |
| Risk | R2，幅度上限 15% | R1，更紧频率 |
| review | APPROVE | NO_ACTION_APPROVE |
| Receipt | SIMULATED（shadow） | NOT_APPLICABLE_NO_ACTION |
| 是否触达平台写 | 否（shadow） | 否 |
| 学习价值 | 干预有效性 | 稳定性/噪声边界 |

---

## 9. JSON Schema 草案

> Draft 2020-12；用于结构校验与样例序列化。枚举与必填若与本文表格冲突，以表格为准并修订本节。

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://garp.local/schemas/decision_packet/0.1.0",
  "title": "GARP Decision Packet",
  "type": "object",
  "required": [
    "decision_id",
    "schema_version",
    "revision",
    "status",
    "packet_kind",
    "execution_mode",
    "tenant_id",
    "shop_id",
    "domain",
    "episode_id",
    "created_at",
    "updated_at",
    "objective_snapshot",
    "state_digest",
    "forecast_ref",
    "hypothesis",
    "proposed_actions",
    "expected_response_window",
    "risk",
    "trust"
  ],
  "properties": {
    "decision_id": {"type": "string", "minLength": 1},
    "schema_version": {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$"},
    "revision": {"type": "integer", "minimum": 1},
    "status": {
      "type": "string",
      "enum": ["Draft", "Self-reviewed", "Executed", "Observed", "Reflected", "Archived", "Superseded"]
    },
    "packet_kind": {"type": "string", "enum": ["standard", "shadow_decision"]},
    "execution_mode": {"type": "string", "enum": ["LIVE", "SHADOW_READ_ONLY"]},
    "created_at": {"type": "string", "format": "date-time"},
    "updated_at": {"type": "string", "format": "date-time"},
    "decided_at": {"type": ["string", "null"], "format": "date-time"},
    "executed_at": {"type": ["string", "null"], "format": "date-time"},
    "closed_at": {"type": ["string", "null"], "format": "date-time"},
    "tenant_id": {"type": "string"},
    "shop_id": {"type": "string"},
    "domain": {"type": "string", "enum": ["JD_AD", "DOUYIN_OPS"]},
    "episode_id": {"type": "string"},
    "parent_decision_id": {"type": ["string", "null"]},
    "superseded_by": {"type": ["string", "null"]},

    "objective_snapshot": {
      "type": "object",
      "required": ["template_id", "weights"],
      "properties": {
        "template_id": {"type": "string"},
        "weights": {
          "type": "object",
          "additionalProperties": {"type": "number", "minimum": 0, "maximum": 1}
        },
        "lifecycle_bias": {"type": "string"},
        "explanation": {"type": "string"},
        "valid_until": {"type": ["string", "null"], "format": "date-time"}
      }
    },

    "state_digest": {
      "type": "object",
      "required": ["state_id", "as_of", "hash", "plan_mode", "lifecycle_phase", "gap_flags", "validation_confidence"],
      "properties": {
        "state_id": {"type": "string"},
        "as_of": {"type": "string", "format": "date-time"},
        "hash": {"type": "string"},
        "plan_mode": {"type": "string", "enum": ["SEEDING", "HARVEST", "MIXED", "UNKNOWN"]},
        "lifecycle_phase": {"type": "string", "enum": ["explore", "growth", "mature", "burst", "decline"]},
        "inventory_risk": {"type": ["string", "null"], "enum": ["OK", "TIGHT", "CRITICAL", "OVERSTOCK", null]},
        "budget_ref": {"type": ["string", "null"]},
        "gap_flags": {"type": "array", "items": {"type": "string"}},
        "validation_confidence": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]}
      }
    },

    "forecast_ref": {
      "type": "object",
      "required": ["forecast_id", "horizon", "confidence", "summary", "based_on_validated_ids"],
      "properties": {
        "forecast_id": {"type": "string"},
        "horizon": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "summary": {"type": "object"},
        "based_on_validated_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1}
      }
    },

    "genome_ref": {"type": ["string", "null"]},
    "knowledge_refs": {"type": "array", "items": {"type": "object"}},
    "working_context_id": {"type": ["string", "null"]},

    "hypothesis": {
      "type": "object",
      "required": ["observation", "cause_claim", "confidence"],
      "properties": {
        "observation": {"type": "object"},
        "cause_claim": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "supporting_signals": {"type": "array", "items": {"type": "object"}},
        "rival_hypotheses": {"type": "array", "items": {"type": "string"}},
        "knowledge_basis": {"type": "array", "items": {"type": "string"}}
      }
    },

    "proposed_actions": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["action_id", "action_type", "action_class", "target", "rationale_ref"],
        "properties": {
          "action_id": {"type": "string"},
          "action_type": {"type": "string"},
          "action_class": {
            "type": "string",
            "enum": ["KEYWORD_BID", "AUDIENCE_PREMIUM", "BUDGET", "ROI_TARGET", "PLAN_CONTROL", "CREATE_PLAN", "NO_ACTION"]
          },
          "target": {"type": "object"},
          "change": {"type": "object"},
          "priority": {"type": "integer", "minimum": 1},
          "rationale_ref": {"type": "string"},
          "risk_per_action": {"type": "object"},
          "shadow_preview": {"type": "object"}
        },
        "allOf": [
          {
            "if": {"properties": {"action_class": {"const": "NO_ACTION"}}},
            "then": {},
            "else": {"required": ["change"]}
          }
        ]
      }
    },

    "expected_response_window": {
      "type": "object",
      "required": ["min_minutes", "max_minutes", "metric_hint"],
      "properties": {
        "min_minutes": {"type": "integer", "minimum": 0},
        "max_minutes": {"type": "integer", "minimum": 0},
        "metric_hint": {"type": "array", "items": {"type": "string"}, "minItems": 1}
      }
    },
    "expected_effect": {"type": "object"},
    "no_action_reason": {"type": "string"},

    "risk": {
      "type": "object",
      "required": ["risk_level", "hard_block", "constraints", "reason_codes", "baseline_version"],
      "properties": {
        "risk_level": {"type": "string", "enum": ["R0", "R1", "R2", "R3", "R4"]},
        "hard_block": {"type": "array", "items": {"type": "string"}},
        "constraints": {"type": "object"},
        "reason_codes": {"type": "array", "items": {"type": "string"}},
        "baseline_version": {"type": "string"}
      }
    },

    "trust": {
      "type": "object",
      "required": ["trust_required", "trust_actual"],
      "properties": {
        "trust_required": {"type": "integer", "minimum": 0, "maximum": 5},
        "trust_actual": {"type": "integer", "minimum": 0, "maximum": 5},
        "trust_score_snapshot": {"type": ["number", "null"], "minimum": 0, "maximum": 100},
        "version": {"type": "string"}
      }
    },

    "review": {
      "type": "object",
      "required": ["review_result", "approved_by", "predicate_trace", "reason_codes", "review_event_id"],
      "properties": {
        "review_result": {
          "type": "string",
          "enum": ["APPROVE", "NO_ACTION_APPROVE", "REVISE", "HOLD", "REJECT", "ESCALATE_HUMAN"]
        },
        "approved_by": {"type": "string", "enum": ["AGENT", "HUMAN"]},
        "predicate_trace": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["id", "result"],
            "properties": {
              "id": {"type": "string"},
              "result": {"type": "string", "enum": ["pass", "fail", "unknown"]},
              "detail": {"type": "string"}
            }
          }
        },
        "reason_codes": {"type": "array", "items": {"type": "string"}},
        "revise_round": {"type": "integer", "minimum": 0},
        "human_ticket_id": {"type": ["string", "null"]},
        "review_event_id": {"type": "string"}
      }
    },

    "executor": {"type": "string"},
    "adapter_runtime_mode": {
      "type": ["string", "null"],
      "enum": ["FIXTURE_ONLY", "SIMULATION", "SANDBOX_LIVE", "LIVE", null]
    },

    "action_receipts": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["receipt_id", "action_id", "status", "idempotency_key", "submitted_at"],
        "properties": {
          "receipt_id": {"type": "string"},
          "action_id": {"type": "string"},
          "status": {
            "type": "string",
            "enum": [
              "ACCEPTED", "REJECTED_BY_GATE", "REJECTED_BY_PLATFORM",
              "TIMEOUT", "UNKNOWN", "SIMULATED", "NOT_APPLICABLE_NO_ACTION"
            ]
          },
          "platform_ack_ref": {"type": ["string", "null"]},
          "idempotency_key": {"type": "string"},
          "submitted_at": {"type": "string", "format": "date-time"},
          "audit": {"type": "object"}
        }
      }
    },

    "outcome_ref": {
      "type": "object",
      "required": ["receipt_ids", "observed_at", "validation_report_ref"],
      "properties": {
        "receipt_ids": {"type": "array", "items": {"type": "string"}},
        "observed_at": {"type": "string", "format": "date-time"},
        "metrics_delta": {"type": "object"},
        "met_prediction": {"type": ["string", "null"], "enum": ["fully", "partially", "no", "not_applicable", null]},
        "side_effects": {"type": "array", "items": {"type": "string"}},
        "validation_report_ref": {"type": "string"}
      }
    },

    "causal_ids": {"type": "array", "items": {"type": "string"}},

    "reflection_ref": {
      "type": "object",
      "required": ["session_id"],
      "properties": {
        "session_id": {"type": "string"},
        "finding_ids": {"type": "array", "items": {"type": "string"}},
        "outcome_label": {"type": ["string", "null"], "enum": ["success", "failure", "neutral", "pending", null]}
      }
    },

    "corrections": {"type": "array", "items": {"type": "object"}},
    "tags": {"type": "array", "items": {"type": "string"}},

    "shadow": {
      "type": "object",
      "required": ["config_id", "learning_pool"],
      "properties": {
        "config_id": {"type": "string"},
        "counterfactual_receipt": {"type": "object"},
        "compare_to_live_decision_id": {"type": ["string", "null"]},
        "learning_pool": {"type": "string", "enum": ["isolated", "downweighted_main"]}
      }
    }
  },
  "allOf": [
    {
      "if": {
        "properties": {
          "status": {"enum": ["Self-reviewed", "Executed", "Observed", "Reflected", "Archived"]}
        }
      },
      "then": {"required": ["review", "executor"]}
    },
    {
      "if": {
        "properties": {"status": {"enum": ["Observed", "Reflected", "Archived"]}}
      },
      "then": {"required": ["action_receipts", "outcome_ref"]}
    },
    {
      "if": {
        "properties": {"packet_kind": {"const": "shadow_decision"}}
      },
      "then": {
        "required": ["shadow"],
        "properties": {"execution_mode": {"const": "SHADOW_READ_ONLY"}}
      }
    },
    {
      "if": {
        "properties": {"execution_mode": {"const": "SHADOW_READ_ONLY"}}
      },
      "then": {
        "properties": {
          "packet_kind": {"enum": ["shadow_decision", "standard"]}
        }
      }
    }
  ],
  "additionalProperties": false
}
```

### 9.1 校验伪流程（非实现代码）

```text
validate(packet):
  jsonschema.validate(packet, DecisionPacket@0.1.0)
  assert packet.status allowed transitions from previous revision
  if packet.hypothesis.state_digest.validation_confidence == LOW:
      forbid any action_class != NO_ACTION for REVIEW approve path
  if packet.execution_mode == SHADOW_READ_ONLY:
      assert no ActionReceipt.status == ACCEPTED
  if any proposed_actions.action_class != NO_ACTION:
      assert no_action_reason is empty
  else:
      assert no_action_reason non-empty
  assert review.review_result present when status >= Self-reviewed
```

---

## 10. 理论追踪与待决问题

### 10.1 理论 / 架构追踪

| 内容 | 锚点 | 本文落点 | 状态 |
|---|---|---|---|
| 决策包最小契约 | 架构 §6 | §2 字段表 | Mapped |
| 成长原子 / 回路 A→B 物理连接 | 架构 §4/§6；初答 §3.3 | §1、§4 | Mapped |
| O-H-A-R-R 因果记忆 | GA-1 §9.2；MKB §5 | §4 | Mapped |
| 预测先于动作 | P2；FE | `forecast_ref` 必填 | Mapped |
| 状态先于相信 | P3；BDV | `state_digest` + validated 引用 | Mapped |
| 稳定性优先 / NO_ACTION | P5；§8.5 | §5.3、样例 B | Mapped |
| 失败即学习 | P6；§9.4 | DPK-I6、REJECT→CR | Mapped |
| Trust 限制动作半径 | P7；§6.7/11.3 | `trust.*`、门禁顺序 | Mapped |
| Risk 硬于 Trust | Risk §2 | `risk.hard_block` 先于 APPROVE | Mapped |
| Self-review 终审 | §11.2 | `review.*` | Mapped |
| 调整响应窗口 | §8.6 | `expected_response_window` | Mapped（数值 Proposed） |
| 动态目标函数 | §7.2/8.2 | `objective_snapshot` | Mapped |
| Shadow/只读红线 | GA-DEC-004 | §7 | Mapped |
| JD Adapter 写门禁 | JD G-01..G-09 | §2.6/§5.2 | Mapped |
| 参数基因引用 | GA2-T07 | `genome_ref` | Partial（目录另文） |
| GA-INNOV-008 | Causal Memory | §4 | Mapped |
| GA-INNOV-002/003/007 | 预测/状态/信任 | §2.3/2.6 | Mapped |

### 10.2 待决问题

| ID | 问题 | 建议（Draft） | 阻塞 | 归属 |
|---|---|---|---|---|
| DPK-Q01 | `NO_ACTION_APPROVE` 是否独立枚举，还是复用 `APPROVE`+action_class | 独立枚举，便于 T8 与统计；若评审嫌冗余可合并 | 否 | SRA 联调 |
| DPK-Q02 | 一包多动作部分失败时的整包状态语义 | 引入 `execution_completeness`；本文暂用 tags + receipt 级状态 | 否 | T05/JD |
| DPK-Q03 | Shadow 样本是否进入 Trust | 默认否；进校准集 | 否 | TE / GA2-T11 |
| DPK-Q04 | Shadow 样本是否进入 Learning 主池 | 默认 `isolated`；高置信反事实可 `downweighted_main` | 否 | LE / GA2-T11 |
| DPK-Q05 | `revision+1` 与新 `decision_id` 的触发边界 | 仅参数级修正用 revision；假设/对象变化用新 ID | 否 | 治理 |
| DPK-Q06 | HOLD 的包级状态是否需要显式子态 | 暂用 `Self-reviewed`+review_result=HOLD；后续可加 `status_detail` | 否 | T05 |
| DPK-Q07 | Schema 是否允许 `validation_confidence=LOW` 下的 NO_ACTION | 允许（只读决策）；禁止写动作 | 否 | BDV/RE |
| DPK-Q08 | 与 JD `DecisionPackage.status` 的双向映射何时冻结 | JD 详设 v0.2 向本文对齐 | 是（接口） | JD Adapter |
| DPK-Q09 | 响应窗口到期自动 Observed 的调度归属 | ME/JDA 定时任务；细则 GA2-T11 | 否 | 运行时 |
| DPK-Q10 | 多租户下 decision_id 全局唯一算法 | `DP-{domain}-{date}-{tenanthash}-{seq}` | 否 | 存储后置 |
| DPK-Q11 | `NO_ACTION` 频率上限是否单独风控 | 建议纳入 RFE 校准，防“永不调整”躺平 | 否 | RKE/RFE |
| DPK-Q12 | 真实 LIVE 路径启用时的字段差异 | 仅 `execution_mode` 与 Receipt 状态；需新 GA-DEC | 是（授权） | 负责人 |

---

## 11. 与上游文档的一致性声明

1. 未修改 `GA-1_Theory_v1.0.md` 与 `PROJECT_SPEC.md`。  
2. 未接入真实广告 API；样例为 Fixture 语义。  
3. 冲突处以 `Architecture_Overview_v0.2.md`（GA-DEC-004）为准，并在 §6 标注。  
4. 全部阈值/默认值为 **Proposed**，禁止表述为已验证真值。  
5. 本文为 GA2-T10 交付物；Shadow 运行细则与 GA2-T11 衔接。

---

## 12. 变更记录

| 日期 | 版本 | 变更 | 依据 |
|---|---|---|---|
| 2026-09-11 | v0.1 | 首次建立：成长原子定位、字段 Schema、状态机、O-H-A-R-R 映射、门禁衔接、shadow 变体、双端到端样例、JSON Schema、追踪与待决 | GA-DEC-004；Architecture_Overview_v0.2 §6；MKB/Risk/JD/Genome 详设 |

---

**Document Status:** Draft  
**Next Stage:** GA2-T09 评审后升 Under Review；与 GA2-T11 Shadow Mode 联调字段  
**Owner Review:** 待 Project Owner / Research Architect  
**Explicit Non-claim:** 本文档不代表已对接京东或抖音官方 API；所有样例为设计 Fixture。
