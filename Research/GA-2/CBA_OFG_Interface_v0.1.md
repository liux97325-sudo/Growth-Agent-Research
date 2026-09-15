# GA-2：CBA 与 Objective Function Generator 接口详设

**文档编号：** GA-2-CBA-OFG-001  
**版本：** v0.1  
**状态：** Draft  
**阶段：** GA-2 Engineering Design  
**输入基线：** `Research/GA-1/GA-1_Theory_v1.0.md`（GA-1.0 / v1.0，Confirmed）§7–8、§12  
**主线架构：** `Research/GA-2/Architecture_Overview_v0.2.md`（Confirmed，GA-DEC-004）  
**关联详设：**  
- `Reasoning_Engine_Interface_v0.1.md`（OFG → RE 的 Objective Snapshot 消费契约）  
- `Parameter_Genome_Templates_v0.1.md`（序关系模板、权重衰减、生命周期偏置）  
- `Decision_Packet_Schema_v0.1.md`（objective_snapshot 字段权威）  
- `Risk_Trust_SelfReview_v0.1.md`（CHK_GOAL 谓词；Trust 动作半径）  
- `Gate_Integration_Playbook_v0.2.md`（双字段可执行判定；CBA 下发路径）  
- `Module_Skeleton_Design_v0.1.md`（garp_core.cba / garp_core.objective 职责表）  
**授权依据：** GA-DEC-004（主线冻结）+ 完善审计「CBA/OFG 缺接口级详设」  
**作者角色：** Research Engineer 子代理  
**约束：** 仅接口契约与编排骨架；不接真实 API；不改 GA-1；所有权重数值、阈值、时间窗一律 **Proposed**；CBA 不写 `review_result`；OFG 不产出动作。

---

## 0. 范围声明

### 0.1 本轮要做

1. 定义 CBA 在四回路中的**接口级**职责、输入输出契约与引擎调用顺序。  
2. 定义 OFG 的独立契约：输入上下文、输出 ObjectiveSnapshot、权重生成规则、与 Reasoning 的边界。  
3. 给出五类场景的目标函数权重生成规则（低客单 / 中高客单 / 种草 / 收割 / 生命周期），从 GA-1 序关系派生，数值全部 **Proposed**。  
4. 定义 CBA 决策任务编排状态机（Decision Task Orchestration State Machine）。  
5. 对齐 Decision Packet `objective_snapshot` 字段与写权。  
6. 明确 CBA/OFG 与 Trust Level、Risk 硬约束、Self-review 的权限关系。  
7. 给出理论追踪与待决问题。

### 0.2 本轮明确不做

- 真实平台 API、凭证、可执行投放脚本；  
- 实现 CBA/OFG 业务代码或性能基准；  
- 替代 SRA 终审、Risk 分档、Trust 升降权；  
- 修改 `GA-1_Theory_v1.0.md` / `Architecture_Overview_v0.2.md` / `Decision_Packet_Schema_v0.1.md`；  
- 抖音域 CBA 编排细化（占位）。

### 0.3 术语约定

| 术语 | 含义 |
|---|---|
| **CBA** | Chief Business Agent；架构唯一最高协调者，负责决策任务编排、资源分配与生命周期推进 |
| **OFG** | Objective Function Generator；动态目标函数生成器，输出有序权重向量 |
| **ObjectiveSnapshot** | OFG 一次生成的可序列化目标快照（template_id + weights + bias + explanation） |
| **DecisionTask** | CBA 编排的一次回路 A 工作单元（可对应 0–N 个 Decision Packet） |
| **CBAContext** | CBA 编排决策任务时组装的上下文包 |
| **Proposed** | 工程草案值，须经历史标定与 GA-3 验证后方可升格 |

---

## 1. CBA 职责、输入输出与引擎调用顺序

### 1.1 一句话定位

> **CBA 是 Growth OS 的唯一最高协调者：消费企业经营目标与 Knowledge 摘要，编排回路 A 的完整决策流水线（OFG → FE → RE → Gate → Domain），组装并推进 Decision Packet 生命周期，但不直接调用平台写接口、不写 `review_result`、不改写目标权重。**

对齐 `Architecture_Overview_v0.2.md` §5：

| 输入 | 输出 | 不做什么 |
|---|---|---|
| 企业经营目标/预算/风险偏好；Trust Level；Knowledge 摘要；Domain Agent 状态；Trusted Business State；RuntimeEnvelope | DecisionTask 编排指令；Decision Packet Draft 组装与生命周期推进；资源分配（shop/plan scope）；executor 指派 | 直接调平台写接口；写 `review_result`；改写 OFG weights；伪造 validated 数据 |

### 1.2 CBA 输入契约（CBAContext）

```text
CBAContext {
  context_id*           : string          // 前缀 CBA-CTX-
  tenant_id*            : ref
  shop_ids*             : ref[]
  enterprise_goals*     : object          // §1.2.1
  budget_position*      : object          // BudgetPosition 引用或摘要
  risk_appetite*        : enum            // Conservative | Balanced | Aggressive_Exploration
  trust_snapshot*       : object          // TE 只读预览：{ trust_actual, trust_version, allowed_action_classes[] }
  knowledge_summary*    : object          // KE 摘要：活跃 Rule/Strategy/Genome 版本索引
  domain_status*        : object[]        // 各 Domain Agent 健康度/在途任务数
  runtime_envelope*     : RuntimeEnvelope // SHADOW / LIVE / FIXTURE 标签透传
  trigger*              : enum {
    PERIODIC_INTRADAY,          // 日内周期扫描
    PERIODIC_DAILY,             // 日终/晨间规划
    EVENT_CAMPAIGN_PREP,        // 活动预热触发
    EVENT_INVENTORY_ALERT,      // 库存预警
    HUMAN_DIRECTIVE,            // 人类下达经营指令
    SRA_REVISE_RETURN,          // REVISE 回流
    LEARNING_FEEDBACK           // 回路 C 知识更新触发重规划
  }
  as_of*                : timestamp
}
```

#### 1.2.1 `enterprise_goals` 子对象

```text
enterprise_goals {
  primary_intent        : enum            // GROWTH | EFFICIENCY | CLEARANCE | BRAND_AWARENESS | BALANCED
  period                : { start, end }
  hard_constraints[]    : object          // 企业级硬约束（总预算上限、禁投类目等）
  soft_preferences      : map<string,number>  // 可选：对 OFG bias 的软提示（不直接覆盖 weights）
  campaign_calendar_ref : ref             // 活动日历引用
}
```

### 1.3 CBA 输出契约（CBAOrchestrationResult）

```text
CBAOrchestrationResult {
  result_id*            : string          // 前缀 CBA-RES-
  context_id*           : ref
  decision_tasks*       : DecisionTask[]  // 本轮编排产出的任务
  skipped_scopes[]      : object          // 未进入决策的 scope 及原因（gap / cooldown / trust）
  resource_allocation*  : object          // 各 Domain Agent 分配的动作包数/预算探索额度
  envelope*             : RuntimeEnvelope
  created_at*           : timestamp
}

DecisionTask {
  task_id*              : string          // 前缀 CBA-TASK-
  scope*                : { shop_id, plan_ids?, campaign_ids?, skus? }
  decision_intent*      : enum            // INTRADAY_INTERVENTION | STABILITY_CHECK | BUDGET_LIFE
                                           // | CAMPAIGN_PREP | INVENTORY_GUARD | AUTO
  objective_snapshot_ref : ref | inline   // OFG 产出（见 §3）
  state_ref*            : ref             // TrustedBusinessState
  forecast_bundle_ref   : ref             // FE 产出；BLOCKED 时仍成 NO_ACTION 任务
  knowledge_refs*       : object[]
  risk_trust_preview*   : object          // §6
  status*               : enum            // 见 §4 状态机
  packet_ids[]          : ref             // 关联 Decision Packet
  executor_hint?        : enum            // JDA-01 | DYA-01（由 CBA 指派，SRA 后正式 executor）
  created_at*           : timestamp
}
```

### 1.4 引擎调用顺序（回路 A 权威时序）

```text
CBA.enter(CBAContext)
  │
  ├─ S0  Scope Partition
  │     按 shop / plan_mode / lifecycle / inventory_risk 将经营范围切分为若干 Decision Scope
  │     过滤：cooldown 中、Trust 不足、gap_flags 严重 → skipped_scopes
  │
  ├─ S1  Objective Generation（每个 Scope）
  │     OFG.generate(ObjectiveGenRequest) → ObjectiveSnapshot
  │     【硬规则】OFG 必须先于 RE；RE 不回调 OFG 改权重（RE §5.2）
  │
  ├─ S2  State Assembly（并行于 S1，或由 STATE 预组装）
  │     STATE 组装 TrustedBusinessState（BDV 已完成校验）
  │     validation_confidence=LOW 的 Scope → 仅 NO_ACTION 任务
  │
  ├─ S3  Forecast
  │     FE.predict(ForecastRequest{ state_ref, horizon }) → ForecastBundle
  │     FE BLOCKED → DecisionTask 标记 forecast_degraded，后续 RE 仅出 NO_ACTION
  │
  ├─ S4  Risk/Trust Preview
  │     RKE/TE 只读预览 → RiskTrustPreview（供 RE 收敛候选，非终审）
  │
  ├─ S5  Reasoning
  │     RE.reason(ReasoningRequest{ objective_snapshot, state_ref, forecast_bundle_ref,
  │                                 knowledge_refs, risk_trust_preview, scope, decision_intent })
  │     → ReasoningBundle（含 PRIMARY + ALTERNATIVE + NO_ACTION）
  │
  ├─ S6  Packet Assembly（CBA 主责）
  │     组装 Decision Packet Draft：
  │       decision_id, schema_version, packet_kind, execution_mode,
  │       objective_snapshot（OFG 原样快照，F 冻结）,
  │       state_digest, forecast_ref, knowledge_refs, genome_ref,
  │       hypothesis, proposed_actions, expected_*（来自 RE）
  │     CBA 不写 risk.* / trust.* / review.*（由后续门禁组件写入）
  │
  ├─ S7  Gate Pipeline
  │     RKE.evaluate → risk.*
  │     TE.gate_action → trust.*
  │     SRA.review → review.*（唯一写 review_result）
  │     REVISE → 回 S5（revise_round+1 ≤ N_revise，Proposed=2）
  │     HOLD → 挂起队列
  │     REJECT → Archived + Failure Pattern
  │     ESCALATE_HUMAN → 人类审批队列
  │
  ├─ S8  Dispatch（仅 APPROVE / NO_ACTION_APPROVE）
  │     CBA 校验双字段可执行（GIP v0.2 §1.1）：
  │       lifecycle_status ∈ {Self-reviewed, Executed}
  │       ∧ review_result ∈ {APPROVE, NO_ACTION_APPROVE}
  │       ∧ execution_mode ≠ SHADOW_READ_ONLY
  │       ∧ risk.hard_block == []
  │     通过 → 下发 Domain Agent（executor）
  │     NO_ACTION → 合成 Receipt 路径，不调平台写
  │
  └─ S9  Lifecycle Advance
        CBA 推进 lifecycle_status：Executed → Observed → Reflected → Archived
        回填 outcome_ref / reflection_ref；写 Audit
```

**时序硬约束：**

| ID | 约束 | 依据 |
|---|---|---|
| CBA-T1 | OFG 严格先于 RE；RE 不改 weights | RE §5.2；DPK-I7 |
| CBA-T2 | FE 必须在 RE 之前；无有效 ForecastBundle 不得产出写动作候选 | RE-P1；FE FR-I* |
| CBA-T3 | Risk/Trust 正式评估在 RE 之后、SRA 之前；预览仅 Draft 收敛用 | RE §2.6；Gate §5.2 |
| CBA-T4 | `review_result` 仅 SRA 可写；CBA 只推进 `lifecycle_status` | GIP C5；DPK §2.6 |
| CBA-T5 | CBA 下发 Domain 前必须重校双字段可执行公式 | GIP §1.1 |
| CBA-T6 | REVISE 回路必须重新引用最新 state/forecast（或显式声明沿用且仍新鲜） | RE §6.4 |
| CBA-T7 | NO_ACTION 仍必须成包并走完整门禁 | DPK-I2 |

### 1.5 CBA 不做的事情（负向清单）

| 禁止项 | 依据 |
|---|---|
| 直接调用平台写接口 | 架构 §5；CBA 通过 Domain Agent + Adapter |
| 写 `review_result` / 改审批结果 | GIP C5；仅 SRA |
| 改写 ObjectiveSnapshot.weights | DPK-I7；OFG 产出后冻结 |
| 消费 Raw 指标做决策 | DPK-I3；必须 Trusted State |
| 绕过 Risk/Trust/Self-review 直接下发 | 架构 P7；Gate §2 |
| 无证据提升 Trust Level | 架构 TE 边界 |
| 对 Executed 包做无痕 Supersede | DPK-I7；DPK §2.9 |

---

## 2. OFG 职责（契约独立于 Reasoning）

### 2.1 一句话定位

> **OFG 是独立的目标函数生成服务：根据商品维度、推广目的、生命周期、库存、活动与企业目标，从理论序关系模板派生有序权重向量，输出可解释的 ObjectiveSnapshot。OFG 不产出动作、不消费 Forecast、不参与门禁、不固定全局 ROI。**

> **架构注记：** 在 `Module_Skeleton_Design_v0.1.md` 中 OFG 被放在 `garp_core.objective` 包，与 `garp_core.reasoning` 同属 core 层。**这不意味着 OFG 是 Reasoning 的子模块。** OFG 契约完全独立：CBA 直接调用 OFG，产物以只读快照形式注入 RE 的 ReasoningRequest。RE 消费但不回调、不改写。

### 2.2 与 Reasoning 的职责切分

| 维度 | OFG | RE |
|---|---|---|
| **输入** | 商品价格带、plan_purpose、lifecycle、inventory_state、activity_event、enterprise_goal、risk_level | Trusted State + ForecastBundle + Objective Snapshot + Knowledge + Risk/Trust 预览 |
| **输出** | ObjectiveSnapshot（template_id、weights、bias、explanation、valid_until） | ReasoningBundle（hypothesis、actions、window 或 NO_ACTION） |
| **做什么** | 从序关系模板派生权重；叠加生命周期/活动偏置；重归一化；生成解释 | 以 weights 为偏好方向生成候选动作或 NO_ACTION |
| **不做什么** | 产出动作；固定全局 ROI；调用 FE/RE；参与门禁 | 改写 weights；自造与理论序冲突的目标；调用 OFG 改权重 |
| **调用者** | CBA（编排器） | CBA（编排器） |
| **可变性** | 输出后在 Packet 中 F 冻结 | 产出候选，经门禁后 F 冻结 |

### 2.3 OFG 输入契约（ObjectiveGenRequest）

```text
ObjectiveGenRequest {
  request_id*           : string          // 前缀 OFG-REQ-
  scope*                : {
    shop_id*            : ref
    plan_ids?           : ref[]
    skus?               : ref[]
  }
  category*             : object          // 对齐 Genome category
    .price_band*        : enum            // Low_Frequency_Fast_Moving | Mid_High_Brand | Unclassified
    .plan_purpose*      : enum            // Seed | Harvest
    .life_cycle_stage*  : enum            // Explore | Grow | Mature | Campaign | Decline_Clearance
  inventory_state*      : enum            // OK | TIGHT | CRITICAL | OVERSTOCK
  activity_event?       : object          // { event_id, phase: PRE|LIVE|PEAK|POST, peak_window? }
  enterprise_goal*      : object          // CBAContext.enterprise_goals 引用
  risk_level_hint*      : enum            // R0..R4 | UNKNOWN（Risk 预览）
  genome_ref?           : ref             // 若 CBA 已锁定 Parameter Genome，OFG 读取其 objective_profile
  trust_actual*         : int 0..5        // 仅影响 explanation 与 valid_until，不影响 weights 结构
  as_of*                : timestamp
}
```

### 2.4 OFG 输出契约（ObjectiveSnapshot）

对齐 `Decision_Packet_Schema_v0.1.md` §2.3 与 `Reasoning_Engine_Interface_v0.1.md` §2.5：

```text
ObjectiveSnapshot {
  template_id*          : string          // 如 T-MHB-SEED / T-LFM-HARVEST
  weights*              : map<string,number>  // 六指标，Σ=1.0（±0.01 舍入容差）
  lifecycle_bias?       : string          // 如 lifecycle_grow / campaign_overlay
  applied_overlays[]    : object[]        // 偏置叠加记录：{ type, direction, magnitude }
  explanation*          : string          // 人类可读；供 SRA CHK_GOAL
  derivation_trace*     : object          // §2.5 可解释性追踪
  valid_until*          : timestamp       // 过期后 RE 标记降级，不静默沿用
  generated_at*         : timestamp
  ofg_version*          : string          // OFG 实现版本（用于审计复现）
}
```

### 2.5 derivation_trace（可解释性追踪）

```text
derivation_trace {
  base_template_id*     : string          // 理论序关系模板 ID
  order_relation*       : string[]        // 使用的序关系（六指标有序列表）
  decay_r*              : number          // 衰减系数（Proposed，默认 0.75）
  bias_chain*           : object[]        // 按序应用的偏置：
    // [{ layer: "lifecycle", name: "explore", multipliers: {ctr:1.2, clicks:1.15, gmv_roi:0.6} },
    //  { layer: "campaign", name: "campaign_go", multipliers: {impressions:1.3, clicks:1.2, gmv_roi:0.7} },
    //  { layer: "inventory", name: "tight", multipliers: {gmv_roi:1.1, impressions:0.9} }]
  renormalized*         : bool            // 是否已重归一化
  theory_anchors*       : string[]        // GA-1 §7.2 / §7.3 / §7.4 / §8.2
}
```

### 2.6 OFG 硬约束

| ID | 约束 | 依据 |
|---|---|---|
| OFG-I1 | weights 六指标 Σ=1.0；指标集合固定为 `{gmv_roi, add_cart, ctr, cpc, clicks, impressions}` | Genome §5.1 |
| OFG-I2 | 序关系必须从 GA-1 §7.2/§7.3 理论模板派生；企业自定义序需 `status=Evolved` + 质量分门槛 | Genome §5.5；架构 P4 |
| OFG-I3 | `price_band=Low_Frequency_Fast_Moving ∧ plan_purpose=Harvest` 时，`gmv_roi` 必须为第一优先 | Genome §3.5 规则 2 |
| OFG-I4 | `price_band=Mid_High_Brand ∧ plan_purpose=Seed` 时，`ctr` 必须为第一优先 | Genome §3.5 规则 3 |
| OFG-I5 | OFG 不产出动作、不调用 FE/RE、不参与门禁 | 架构 §5 |
| OFG-I6 | 输出后 weights 在 Decision Packet 中 F 冻结；已 Executed 不可原地覆盖 | DPK-I7 |
| OFG-I7 | `valid_until` 必填；默认 Proposed=24h（日内）或绑定活动窗口结束 | RE §5.2 |
| OFG-I8 | explanation 必须人类可读，引用 template_id 与 bias 原因 | Genome §5.5 |

---

## 3. 目标函数权重生成规则

> **本节全部数值为 Proposed 工程预标定，不是 GA-1 理论结论。有效性待 GA-3 验证。**

### 3.1 指标词典（固定六指标）

| 指标代码 | 含义 | 理论用语 |
|---|---|---|
| `gmv_roi` | 成交 ROI | 成交 ROI |
| `add_cart` | 加购 | 加购总数/加购数 |
| `ctr` | 点击率 | 点击率 |
| `cpc` | 点击单价 | 点击单价 |
| `clicks` | 点击数 | 点击数/点击 |
| `impressions` | 展现 | 展现量/展现数 |

### 3.2 基础序关系模板（从 GA-1 派生）

#### T-LFM-HARVEST：低客单 × 收割（GA-1 §7.2 低客单原文序，Confirmed 语义）

```text
gmv_roi > add_cart > ctr > cpc > clicks > impressions
```

#### T-MHB-SEED：中高客单 × 种草（GA-1 §7.2 中高客单原文序，Confirmed 语义）

```text
ctr > clicks > add_cart > impressions > cpc > gmv_roi
```

#### T-LFM-SEED：低客单 × 种草（理论未给专序；Proposed 工程草案）

在 T-LFM-HARVEST 上将触达类上提，仍保留成交导向：

```text
add_cart > ctr > clicks > impressions > gmv_roi > cpc
```

#### T-MHB-HARVEST：中高客单 × 收割（理论未给专序；Proposed 工程草案）

偏成交，但因客单高，稳定性与点击质量仍重要：

```text
gmv_roi > add_cart > ctr > clicks > cpc > impressions
```

### 3.3 序关系 → 权重映射（ordinal decay）

将序关系映射为可计算权重（Σ=1.0）。采用**等比递减**：

```text
w_i = r^(rank_i - 1) / Σ_k r^(k - 1)
```

默认 `r = 0.75`（**Proposed**）。示意权重：

| 模板 | r1 | r2 | r3 | r4 | r5 | r6 |
|---|---:|---:|---:|---:|---:|---:|
| T-LFM-HARVEST | 0.31 | 0.23 | 0.17 | 0.13 | 0.10 | 0.06 |
| T-MHB-SEED | 0.31 | 0.23 | 0.17 | 0.13 | 0.10 | 0.06 |
| T-LFM-SEED | 0.31 | 0.23 | 0.17 | 0.13 | 0.10 | 0.06 |
| T-MHB-HARVEST | 0.31 | 0.23 | 0.17 | 0.13 | 0.10 | 0.06 |

> **Pending：** `r` 值、是否采用非均匀衰减、是否允许企业覆盖，待历史优秀计划标定与敏感性分析（Genome GQ3）。

### 3.4 生命周期偏置（Lifecycle Bias）

在基础模板上对权重做**乘性偏置**后重归一化：

| 阶段 | 偏置方向（乘性系数，Proposed） | 理论锚点 |
|---|---|---|
| **Explore** | ↑ `ctr`×1.2, `clicks`×1.15, `impressions`×1.1；↓ `gmv_roi`×0.6 | GA-1 §7.4 种草权重高；获取人群与数据 |
| **Grow** | ↑ `clicks`×1.15, `add_cart`×1.1；轻微 ↓ `cpc` 敏感度×0.95 | GA-1 §7.4 扩大有效流量 |
| **Mature** | ↑ `gmv_roi`×1.2, `add_cart`×1.1；↓ `impressions`×0.9 | GA-1 §7.4 提高成交效率；§8.5 稳定性优先 |
| **Campaign** | 整体 ↑ 获量类：`impressions`×1.3, `clicks`×1.2, `ctr`×1.1；↓ `gmv_roi`×0.7 | GA-1 §7.4 动态提高；§11.1 动态放宽 ROI 保障获量 |
| **Decline_Clearance** | ↑↑ `gmv_roi`×1.3, `add_cart`×1.2；↓ 新客探索类 `impressions`×0.8 | GA-1 §7.4 快速转化与清库存 |

`Campaign Overlay` 可临时替换/覆盖 `objective_profile`，有效期绑定活动窗口，结束后回落到主基因。

### 3.5 五类场景权重生成规则汇总

#### 规则 R-LFM-H：低客单收割

```text
输入：price_band=Low_Frequency_Fast_Moving, plan_purpose=Harvest
基础模板：T-LFM-HARVEST
序：gmv_roi > add_cart > ctr > cpc > clicks > impressions
生命周期偏置：
  Explore → 罕见；若出现则警告并降级为 T-LFM-SEED
  Grow    → 轻微 ↑ add_cart
  Mature  → 强化 gmv_roi；prefer_stability=true
  Campaign → 临时 Overlay ↑ 获量，允许 ↓ gmv_roi
  Decline → ↑↑ gmv_roi，禁扩种草
```

#### 规则 R-MHB-S：中高客单种草

```text
输入：price_band=Mid_High_Brand, plan_purpose=Seed
基础模板：T-MHB-SEED
序：ctr > clicks > add_cart > impressions > cpc > gmv_roi
生命周期偏置：
  Explore → 强化 ctr/clicks/impressions；gmv_roi 权重极低
  Grow    → 主力阶段；标准 T-MHB-SEED + lifecycle_grow
  Mature  → 种草权重下降；可与收割计划并存
  Campaign → Overlay 大幅 ↑ 获量类
  Decline → 种草权重极低；倾向停建
```

#### 规则 R-LFM-S：低客单种草（Proposed）

```text
输入：price_band=Low_Frequency_Fast_Moving, plan_purpose=Seed
基础模板：T-LFM-SEED（Proposed）
序：add_cart > ctr > clicks > impressions > gmv_roi > cpc
说明：低客单种草仍带成交导向（add_cart 居首），触达类次之
```

#### 规则 R-MHB-H：中高客单收割（Proposed）

```text
输入：price_band=Mid_High_Brand, plan_purpose=Harvest
基础模板：T-MHB-HARVEST（Proposed）
序：gmv_roi > add_cart > ctr > clicks > cpc > impressions
说明：偏成交但保留点击质量；Mature 阶段 prefer_stability=true
```

#### 规则 R-UNC：未分类/冷启动

```text
输入：price_band=Unclassified
基础模板：企业默认混合模板 T-MIXED-DEFAULT（Proposed）
序：add_cart > gmv_roi > ctr > clicks > impressions > cpc（折中）
说明：观察期后重新分类；不单独占用 20 主槽位
```

### 3.6 库存与活动叠加规则

| 条件 | 叠加行为 |
|---|---|
| `inventory_state=TIGHT` | ↑ `gmv_roi`×1.1；↓ `impressions`×0.9；同时 Risk 升档，限制扩量 |
| `inventory_state=CRITICAL` | 强制偏成交/清库存；禁新建与扩种草（Risk R4 语义） |
| `activity_event.phase=PRE` | Overlay：↑ `add_cart`×1.15, `impressions`×1.1（蓄水） |
| `activity_event.phase=PEAK` | Overlay：↑ 获量类；允许 ↓ `gmv_roi`×0.7 |
| `activity_event.phase=POST` | Overlay 撤销；回落主基因 + 收紧 Risk |
| `risk_level_hint=R4` | OFG 仍正常生成 weights；但 RE 侧将因 hard_block 收敛为 NO_ACTION |

### 3.7 OFG 生成算法骨架（非实现代码）

```text
1. 读 category → 选定 base_template_id
2. 读取模板 order_relation（六指标有序列表）
3. 计算基础权重：w_i = r^(rank-1) / Σ r^(k-1)
4. 按序叠加 bias_chain：
     lifecycle_bias → inventory_bias → campaign_overlay
   每层：w_i' = w_i * multiplier_i
5. 重归一化：w_i'' = w_i' / Σ w_i'
6. 校验 OFG-I3 / OFG-I4（第一优先约束）
7. 生成 explanation + derivation_trace
8. 设置 valid_until（日内=当日 24:00；活动=窗口结束；默认=as_of+24h）
9. 返回 ObjectiveSnapshot
```

---

## 4. CBA 决策任务编排状态机

### 4.1 DecisionTask 状态定义

| 状态 | 含义 | 进入条件 | 主责写入者 |
|---|---|---|---|
| `CREATED` | 任务已创建，OFG/FE 尚未完成 | CBA Scope Partition 完成 | CBA |
| `OBJECTIVE_READY` | OFG 已产出 ObjectiveSnapshot | OFG.generate 返回 | OFG/CBA |
| `FORECAST_READY` | FE 已产出 ForecastBundle（或 BLOCKED 标记） | FE.predict 返回 | FE/CBA |
| `REASONING` | RE 正在推理 | CBA 发起 RE.reason | RE |
| `PACKET_DRAFT` | Decision Packet Draft 已组装 | CBA 组装完成 | CBA |
| `GATING` | 进入门禁流水线（Risk→Trust→SRA） | Draft 完成，提交 Gate | RKE/TE/SRA |
| `REVISE_LOOP` | SRA 返回 REVISE，等待重推理 | review_result=REVISE | CBA→RE |
| `HOLD_QUEUE` | SRA 返回 HOLD，挂起等待 | review_result=HOLD | CBA |
| `ESCALATED` | SRA 返回 ESCALATE_HUMAN | review_result=ESCALATE_HUMAN | CBA/人类 |
| `APPROVED` | SRA APPROVE 或 NO_ACTION_APPROVE | review_result 写入 | SRA |
| `DISPATCHED` | 已下发 Domain Agent | CBA 校验可执行公式后 | CBA/JDA |
| `OBSERVED` | 结果已回填 | 响应窗口到期 + outcome_ref 完整 | JDA/ME |
| `COMPLETED` | 任务闭环 | Reflected 完成 | CBA |
| `CANCELLED` | 任务取消/失败归档 | REJECT / 超时 / 人类否决 | CBA |

### 4.2 状态迁移图

```text
                         ┌─────────────┐
                         │   CREATED   │
                         └──────┬──────┘
                                │ OFG.generate
                                ▼
                      ┌───────────────────┐
                      │ OBJECTIVE_READY   │
                      └─────────┬─────────┘
                                │ FE.predict（可并行）
                                ▼
                      ┌───────────────────┐
                      │  FORECAST_READY   │
                      └─────────┬─────────┘
                                │ RE.reason
                                ▼
                      ┌───────────────────┐
                      │    REASONING      │
                      └─────────┬─────────┘
                                │ CBA 组装 Draft
                                ▼
                      ┌───────────────────┐
                      │   PACKET_DRAFT    │
                      └─────────┬─────────┘
                                │ 提交 Gate
                                ▼
                      ┌───────────────────┐
                      │     GATING        │
                      └─────────┬─────────┘
            ┌───────────┬───────┼───────┬───────────┐
            ▼           ▼       ▼       ▼           ▼
     ┌──────────┐ ┌──────────┐ ┌────┐ ┌──────┐ ┌────────┐
     │REVISE_   │ │HOLD_     │ │ESCA│ │APPROVED│ │CANCELLED│
     │LOOP      │ │QUEUE     │ │LATED│ │      │ │(REJECT) │
     └────┬─────┘ └────┬─────┘ └──┬─┘ └──┬───┘ └────────┘
          │            │          │       │
          │ ≤N_revise  │ 解锁     │ HUMAN │
          │ 回 RE      │ 重审     │ 批准  │
          ▼            ▼          ▼       ▼
     ┌──────────┐              ┌───────────────┐
     │REASONING │              │  DISPATCHED   │
     └──────────┘              └───────┬───────┘
                                       │ 响应窗口
                                       ▼
                               ┌───────────────┐
                               │   OBSERVED    │
                               └───────┬───────┘
                                       │ Reflection
                                       ▼
                               ┌───────────────┐
                               │   COMPLETED   │
                               └───────────────┘
```

### 4.3 迁移规则表

| 从 → 到 | 条件 | 审计 |
|---|---|---|
| CREATED → OBJECTIVE_READY | OFG.generate 成功 | ofg_version + derivation_trace |
| OBJECTIVE_READY → FORECAST_READY | FE.predict 返回（含 BLOCKED） | forecast_bundle_id |
| FORECAST_READY → REASONING | CBA 发起 RE.reason | request_id |
| REASONING → PACKET_DRAFT | ReasoningBundle 产出，CBA 组装完成 | decision_id |
| PACKET_DRAFT → GATING | Draft 提交 Risk/Trust/SRA | gate 入口日志 |
| GATING → REVISE_LOOP | review_result=REVISE 且 revise_round < N_revise | parent_decision_id |
| REVISE_LOOP → REASONING | CBA 发起重推理（新 state/forecast 引用） | revise_round+1 |
| REVISE_LOOP → ESCALATED | revise_round ≥ N_revise（Proposed=2） | ESC-04 |
| GATING → HOLD_QUEUE | review_result=HOLD | hold_reason |
| HOLD_QUEUE → GATING | 解锁条件满足（窗口到期/数据补齐） | 解锁事件 |
| HOLD_QUEUE → CANCELLED | 超时 T_hold_max（Proposed，待标定） | 超时原因 |
| GATING → ESCALATED | review_result=ESCALATE_HUMAN | human_ticket_id |
| ESCALATED → APPROVED | HUMAN_APPROVE / HUMAN_MODIFY | approved_by=HUMAN |
| ESCALATED → REVISE_LOOP | HUMAN_REVISE | |
| ESCALATED → CANCELLED | HUMAN_REJECT | |
| GATING → APPROVED | review_result=APPROVE / NO_ACTION_APPROVE | review_event_id |
| GATING → CANCELLED | review_result=REJECT | Failure Pattern 标签 |
| APPROVED → DISPATCHED | CBA 校验 GIP §1.1 四条件通过 | executor + receipt |
| DISPATCHED → OBSERVED | 响应窗口到期 + outcome_ref 完整 | validation_report |
| OBSERVED → COMPLETED | ReflectionSession 覆盖 | reflection_ref |

### 4.4 并行与批量规则

| 规则 | 说明 |
|---|---|
| Scope 并行 | 不同 shop / 不同 plan_mode 的 DecisionTask 可并行进入 S1–S5 |
| 同对象串行 | 同一 plan_id 的写动作任务串行，遵守 response window（RE-P6） |
| 批量上限 | 单轮 CBA 编排产出的 DecisionTask 数上限 Proposed=20；超出分批 |
| 优先级 | decision_intent 优先级：INVENTORY_GUARD > CAMPAIGN_PREP > BUDGET_LIFE > INTRADAY_INTERVENTION > STABILITY_CHECK > AUTO |

---

## 5. 与 Decision Packet objective_snapshot 对齐

### 5.1 字段映射

| ObjectiveSnapshot 字段 | Decision Packet 路径 | 来源 | 可变性 | 说明 |
|---|---|---|---|---|
| `template_id` | `objective_snapshot.template_id` | OFG | F | 如 `T-MHB-SEED` |
| `weights` | `objective_snapshot.weights` | OFG | F | 六指标，Σ=1 |
| `lifecycle_bias` | `objective_snapshot.lifecycle_bias` | OFG | F | 如 `lifecycle_grow` |
| `explanation` | `objective_snapshot.explanation` | OFG | F | 供 SRA CHK_GOAL |
| `valid_until` | `objective_snapshot.valid_until` | OFG | F | 过期降级 |
| `derivation_trace` | （建议扩展字段） | OFG | F | 当前 DPK Schema 未显式列出；建议 v0.2 增补或放入 `tags`/`metadata` |
| `applied_overlays` | （建议扩展字段） | OFG | F | 同上 |

> **对齐注记：** 当前 `Decision_Packet_Schema_v0.1.md` §2.3 的 `objective_snapshot` 含 5 个字段（template_id / weights / lifecycle_bias / explanation / valid_until）。`derivation_trace` 与 `applied_overlays` 为本文新增提案，供 DPK v0.2 评审时增补。在增补前，可将 derivation_trace 序列化写入 `explanation` 或 `tags`。

### 5.2 写权与时序

```text
1. OFG.generate() → ObjectiveSnapshot（内存对象）
2. CBA 组装 Decision Packet Draft 时，将 ObjectiveSnapshot 原样拷贝入 packet.objective_snapshot
3. 此后 objective_snapshot 全部字段 F 冻结（DPK-I7）
4. RE 只读消费；SRA 只读校验（CHK_GOAL）
5. 已 Executed 的包不得原地覆盖 objective_snapshot；修正须新 decision_id
```

### 5.3 与 RE 的消费契约（引用 RE §5.3）

| RE 用途 | 消费方式 |
|---|---|
| 动作方向对齐 | 种草 weights 偏 ctr/clicks → 获量类动作优先；收割偏 gmv_roi → 稳定与成交优先 |
| expected_effect 指标选择 | metric_targets 优先覆盖高权重指标 |
| PRIMARY vs ALTERNATIVE 排序 | 与高权重指标改善方向一致者优先 |
| NO_ACTION 判定辅助 | 预测改进主要落在低权重指标且低于噪声 → 更倾向 NO_ACTION |
| objective_alignment 字段 | 生成人类可读对齐说明，供 SRA CHK_GOAL |

### 5.4 缺失/过期行为

| 条件 | OFG 行为 | RE 行为 | SRA 行为 |
|---|---|---|---|
| OFG 未被调用 | — | `status=DEGRADED`，`degrade_reasons` 含 `MISSING_OBJECTIVE`；仅 NO_ACTION/HOLD | CHK_GOAL fail → REVISE 或 HOLD |
| ObjectiveSnapshot 过期（valid_until < now） | — | 标记降级；不静默沿用 | CHK_GOAL fail → HOLD |
| weights 非法（Σ≠1 或缺指标） | OFG 内部校验失败，返回错误 | 不消费 | — |
| Unclassified 商品 | 使用 T-MIXED-DEFAULT | 正常消费 | CHK_MODEL 可放宽 |

---

## 6. 与 Trust / 权限的关系

### 6.1 CBA 与 Trust

| 维度 | 规则 |
|---|---|
| **读** | CBA 在 S0 Scope Partition 时读取 Trust 预览，过滤 `trust_actual < trust_required` 的 scope |
| **不写** | CBA 不修改 Trust Score / Level；升降权仅由 TE 基于历史表现执行 |
| **executor 指派** | CBA 指派 Domain Agent 时参考 Trust Level；高风险动作指派给 Trust 更高的 Agent（若有多个） |
| **资源分配** | 探索预算分配受 Trust Level 约束（L4+ 才可分配新建计划额度） |

### 6.2 OFG 与 Trust / Risk

| 维度 | 规则 |
|---|---|
| **Risk 影响** | OFG 接收 `risk_level_hint`，但 **Risk 硬于目标偏好**：hard_block 非空时 OFG 正常生成 weights，由 RE/SRA 收敛动作 |
| **Trust 影响** | OFG 接收 `trust_actual`，仅影响 explanation 与 valid_until（低 Trust 时缩短有效期），**不影响 weights 结构** |
| **不参与门禁** | OFG 不调用 Risk/Trust/SRA；不产出 hard_block |

### 6.3 与 SRA CHK_GOAL 谓词的衔接

```text
CHK_GOAL 通过条件（Draft）：
  - objective_snapshot.template_id 与 scope.category 一致
  - weights 第一优先指标与 plan_purpose 匹配（OFG-I3/I4）
  - proposed_actions 的 expected_effect.metric_targets 覆盖高权重指标
  - 动作方向与 lifecycle_bias 不冲突
  - objective_snapshot 未过期

失败倾向：REVISE（可修正）或 ESCALATE_HUMAN（目标根本冲突）
```

### 6.4 权限矩阵（CBA/OFG 相关动作类 × Trust Level）

对齐 `Risk_Trust_SelfReview_v0.1.md` §5.2，CBA 编排时的过滤规则：

| 动作类 | 最低 Trust | CBA 编排行为 |
|---|---|---|
| 只读感知/分析/建议 | L0 | 正常编排 |
| 低风险微调 | L1 | L0 时 skip，写入 skipped_scopes |
| 关键词出价 / 人群溢价 | L2 | L<2 时 skip |
| 计划内预算调整 | L3 | L<3 时 skip |
| 账户级预算重分配 | L4 | L<4 时 skip |
| 新建种草计划 | L4 | L<4 时 skip；且受探索预算约束 |
| 新建收割计划 | L4–5 | 受限 |
| 批量/跨计划策略切换 | L5 | L<5 时 skip |
| 触碰 Risk 硬红线 | — | 任何 Level 均 skip（hard_block） |

---

## 7. 理论追踪

| 理论主张 | GA-1 锚点 | 本文落点 | 覆盖 |
|---|---|---|---|
| 动态目标函数（禁固定 ROI） | §8.2；架构 P4 | §2 OFG 独立契约；§3 五类场景权重生成 | Mapped |
| 低客单 vs 中高客单序关系 | §7.2 | §3.2 T-LFM-HARVEST / T-MHB-SEED | Mapped |
| 种草 vs 收割差异 | §7.3 | §3.2 T-LFM-SEED / T-MHB-HARVEST；§3.5 R-* 规则 | Mapped |
| 生命周期五阶段权重变化 | §7.4 | §3.4 生命周期偏置表 | Mapped |
| Chief Business Agent 协调 | §12 | §1 CBA 职责与调用顺序 | Mapped |
| 企业 AI OS 分层 | §12 | §1.1 CBA 作为唯一最高协调者 | Mapped |
| 稳定性优先 / NO_ACTION | §8.5 | §1.4 CBA-T7；§4 状态机 APPROVED 含 NO_ACTION_APPROVE | Mapped |
| 调整响应窗口 | §8.6 | §4.4 同对象串行规则 | Mapped |
| 数据真实性校验 | §8.1 | §1.2 强制 Trusted State | Mapped |
| 决策可信度验证 | §8.4 | §1.4 S2 validation_confidence=LOW → 仅 NO_ACTION | Mapped |
| 双时间尺度 | §8.3 | §1.2 trigger 含 PERIODIC_INTRADAY / PERIODIC_DAILY | Mapped |
| Trust-based 权限成长 | §6.7 | §6 权限矩阵 | Mapped |
| 动态风险基线 | §11.1 | §3.6 库存/活动叠加；§6.2 Risk 硬于目标 | Mapped |
| Self-review 检查项 | §11.2 | §6.3 CHK_GOAL 衔接 | Mapped |
| Shadow / 只读红线 | GA-DEC-004 | §1.4 S8 execution_mode 校验 | Mapped |

**明确不声称：** 本文全部权重数值、衰减系数、偏置乘性系数、批量上限、时间窗均为 Proposed 工程预标定，不是 GA-1 理论结论；有效性待 GA-3 验证。本文不实现任何 CBA/OFG 算法或真实广告操作。

---

## 8. 待决问题

| ID | 问题 | 建议（Draft） | 阻塞 | 归属 |
|---|---|---|---|---|
| CO-Q01 | OFG 是否需要支持多目标 Pareto 而非单一权重向量？ | 第一轮坚持单一有序权重；Pareto 后置 | 否 | GA-3 后评估 |
| CO-Q02 | CBA Scope Partition 的粒度（shop/plan/sku）如何动态选择？ | 默认 plan 级；库存/活动事件可升至 sku 级 | 否 | 联调 |
| CO-Q03 | `derivation_trace` 是否进入 DPK Schema 正式字段？ | 建议 DPK v0.2 增补；当前可序列化入 explanation | 否 | DPK 评审 |
| CO-Q04 | 衰减系数 `r` 是否允许按企业/类目差异化？ | 先全局 0.75；标定后可按槽位覆盖 | 否 | GA2-T07 标定 |
| CO-Q05 | Campaign Overlay 的有效期粒度（小时/天）？ | 绑定 activity_event.peak_window；默认 PRE 起至 POST 止 | 否 | 活动日历 |
| CO-Q06 | CBA 单轮批量上限 20 是否合理？ | 先 Proposed=20；Shadow 试运行观测后再调 | 否 | Shadow Trial |
| CO-Q07 | REVISE 回路是否必须新 forecast_id？ | 若原 bundle 仍新鲜（Proposed <30min）可沿用；否则强制刷新（对齐 RE-Q06） | 否 | 运行时 |
| CO-Q08 | 未分类商品的 T-MIXED-DEFAULT 序关系是否采纳 §3.5 R-UNC？ | 评审确认后进默认模板，保持 Proposed | 否 | OFG 评审 |
| CO-Q09 | CBA 与 Runtime Orchestrator（Module Skeleton）的边界？ | CBA 负责业务编排；Runtime 负责装配/熔断/自检；不重叠 | 否 | 已对齐 Skeleton |
| CO-Q10 | 多租户场景下 OFG 模板是否支持租户级覆盖？ | 否；仅写 `enterprise/` 目录；defaults 变更走版本评审（对齐 GQ8） | 否 | 治理 |
| CO-Q11 | CBA 在 FE BLOCKED 时是否仍调用 OFG？ | 是；NO_ACTION 任务仍需 objective_snapshot 成包 | 否 | 已定原则 |
| CO-Q12 | 抖音域 CBA 编排何时扩展？ | 占位；JD 验证后再设计 | 否 | 后置 |

---

## 9. 与后续任务的接口

| 下游 | 本文供给 |
|---|---|
| Decision Packet（GA2-T10） | objective_snapshot 字段映射（§5）；derivation_trace 增补提案 |
| Gate Integration（GA2-T19） | CBA 下发前双字段校验（§1.4 S8）；CHK_GOAL 输入 |
| Risk/Trust/SRA（GA2-T05） | CBA 编排时的 Trust 过滤规则（§6）；OFG 与 Risk 的边界 |
| Reasoning Engine（GA2-T23） | OFG → RE 调用时序（§1.4）；ObjectiveSnapshot 消费契约（§5.3） |
| Parameter Genome（GA2-T07） | 权重生成规则（§3）；序关系模板与衰减系数 |
| Module Skeleton（GA2-T28） | garp_core.cba / garp_core.objective 接口签名输入 |
| Shadow Mode（GA2-T11） | CBA 在 Shadow 下的编排完整性要求 |
| GA-3 验证 | 权重有效性、NO_ACTION 正确率、CBA 编排效率指标定义 |

---

## 10. 变更记录

| 日期 | 版本 | 变更 | 依据 |
|---|---|---|---|
| 2026-09-14 | v0.1 | 首次建立 CBA/OFG 接口详设：CBA 职责与调用顺序、OFG 独立契约、五类场景权重生成规则、决策任务编排状态机、objective_snapshot 对齐、Trust/权限关系、理论追踪与待决 | 完善审计；Architecture v0.2 §5；GA-1 §7–8/§12；Genome §5；RE §5；DPK §2.3；Risk §5–6 |

---

**Document Status:** Draft  
**Next Review:** 项目负责人 / Research Architect  
**Explicit Non-claim:** 本文不代表已实现任何 CBA/OFG 逻辑或接入真实数据源；所有权重数值、衰减系数、偏置系数、批量上限与时间窗均为 Proposed；CBA 不写 `review_result`、不调平台写接口；OFG 不产出动作、不固定全局 ROI；`NO_ACTION` 为合法一等公民输出且必须成包。
