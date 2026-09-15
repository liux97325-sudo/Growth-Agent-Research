# GA-2：Reasoning Engine 接口与场景推理骨架

**文档编号：** GA-2-RE-001  
**任务编号：** GA2-T23  
**版本：** v0.1  
**状态：** Draft  
**阶段：** GA-2 Engineering Design  
**输入基线：** `Research/GA-1/GA-1_Theory_v1.0.md`（GA-1.0 / v1.0，Confirmed）  
**主线架构：** `Research/GA-2/Architecture_Overview_v0.2.md`（Confirmed，GA-DEC-004）  
**关联详设：**  
- `Forecast_Engine_Interface_v0.1.md`（ForecastBundle / forecast_ref / 降级阶梯）  
- `Decision_Packet_Schema_v0.1.md`（Decision Packet 字段与硬不变式）  
- `Gate_Integration_Playbook_v0.2.md`（双字段可执行判定；RE 为 L2 候选产出层）  
- `Risk_Trust_SelfReview_v0.1.md`（Risk/Trust 预览约束；SRA 谓词）  
- `Parameter_Genome_Templates_v0.1.md`（OFG 输出契约；adjustment_policy；prefer_stability）  
- `Shadow_Mode_Design_v0.1.md`（Shadow 下 RE 完整候选含 NO_ACTION）  

**授权依据：** `GA-DEC-004`（主线冻结 + 启动 GA2-T23）  
**作者角色：** Research Engineer 子代理  
**约束：** 仅接口契约与推理骨架；不接真实 API；不实现推理引擎代码；所有置信度阈值、幅度、窗口与噪声门限一律 **Proposed**；不得绕过 Risk/Trust/Self-review/Adapter 门禁。

---

## 0. 范围声明

### 0.1 本轮要做

1. 定义 Reasoning Engine（RE）在四回路中的位置、职责边界与设计原则。  
2. 定义 RE 输入契约：Trusted Business State、ForecastBundle、Knowledge refs、Objective Snapshot、Risk/Trust 预览。  
3. 定义 RE 输出契约：候选动作 + hypothesis + expected_response_window，或合法 `NO_ACTION`。  
4. 建立五类场景推理骨架（Scenario Skeleton）：种草获量下滑、预算寿命、收割稳定性、活动期、库存紧张。  
5. 明确 RE 与 Objective Function Generator（OFG）的调用与引用关系。  
6. 给出 RE 输出字段 → Decision Packet 字段映射表。  
7. 定义低置信 / 缺预测 / 预拒绝时的降级与 `NO_ACTION`/`HOLD` 行为。  
8. 给出理论追踪与待决问题。

### 0.2 本轮明确不做

- 真实平台数据拉取、写操作、API 凭证与可执行投放脚本；  
- 实现具体推理算法（规则引擎 / LLM / 混合）的代码或性能基准；  
- 替代 Risk Engine 分档、Trust Engine 门控或 Self-review 终审；  
- 修改 `GA-1_Theory_v1.0.md` / `PROJECT_SPEC.md` / `Architecture_Overview_v0.2.md`；  
- 抖音域场景骨架扩展（仅占位）。

### 0.3 术语约定

| 术语 | 含义 |
|---|---|
| **ReasoningBundle** | RE 一次推理产出的候选决策草稿集合（可含 0–N 个非写动作候选 + 0–1 个推荐主候选，或 NO_ACTION） |
| **ReasoningCandidate** | Bundle 内单个候选：含 hypothesis、proposed_actions、expected_response_window 等 |
| **Scenario Skeleton** | 按经营场景预设的推理路径模板（观察面 → 假设簇 → 动作候选类 → 稳定性检查），不是固定剧本 |
| **Risk/Trust 预览** | RKE/TE 在 Draft 末写入 Decision Packet 前的只读约束快照；RE 消费但不改写 |
| **Proposed** | 工程草案值，须经历史标定与 GA-3 验证后方可升格 |

---

## 1. Reasoning Engine 定位

### 1.1 一句话

> **RE 是经营状态与未来预测到可审计决策草稿的映射器：只消费 Trusted State、ForecastBundle、Objective Snapshot 与 Knowledge，产出候选动作或显式 NO_ACTION，不拍板、不执行、不绕过门禁。**

### 1.2 在架构中的位置

对齐 `Architecture_Overview_v0.2.md` §5 组件边界表：

| 输入 | 输出 | 不做什么 |
|---|---|---|
| Trusted State（STATE）、ForecastBundle（FE）、Objective Snapshot（OFG）、Knowledge refs（KE）、Risk/Trust 预览 | 候选动作 + 假设 + 预期窗口 + `NO_ACTION`；组装 Decision Packet Draft | 绕过门禁；写 `review_result`；调用平台写接口；伪造 validated 数据 |

### 1.3 在四条主回路中的位置

```text
回路 A（日内/单计划）—— RE 是“决策草稿”核心节点：

  Adapter(RO) → BDV → STATE → FE → RE → [Decision Packet Draft]
                                            ↓
                                    Risk → Trust → SRA → CBA → JDA → Adapter(G-01..G-09)

  RE 必须在 FE 之后、Risk 之前；任何组件不得要求 RE 产出“已批准可执行”动作。

回路 B（经验蒸馏）：RE 不写 Memory；但 hypothesis / expected_effect / no_action_reason
  经 Decision Packet 进入 CausalRecord，供 RFE 校准“假设是否正确、NO_ACTION 是否正确”。

回路 C（知识演化）：RE 消费 KE 的 Rule/Strategy/Genome/Experience 版本锁定引用；
  新场景无知识模板时，RE 应显式标记 knowledge_basis 为空，并倾向 HOLD / ESCALATE（ESC-06）。

回路 D（信任与自治）：RE 根据 trust_actual 预览收敛候选动作半径（低 Trust 不提 CREATE_PLAN）；
  但 RE 不提升 Trust、不放宽 Risk、不替代 SRA。
```

### 1.4 设计原则（自理论与主线派生）

| ID | 原则 | 理论/架构锚点 | 工程含义 |
|---|---|---|---|
| RE-P1 | 预测先于动作 | GA-1 §6.2；架构 P2；FE-P1 | 无有效 ForecastBundle 时不得产出非 `NO_ACTION` 写动作候选 |
| RE-P2 | 只信校验后状态 | GA-1 §6.3, §8.1；架构 P3；DPK-I3 | 输入必须引用 Trusted State / ValidatedMetricSet，禁止 Raw |
| RE-P3 | 目标函数动态消费 | GA-1 §7.2–7.4, §8.2；架构 P4 | 以 OFG 输出的 Objective Snapshot 为偏好方向，不自造全局 ROI |
| RE-P4 | 稳定性可战胜贪婪 | GA-1 §8.5；架构 P5；DPK-I2 | `NO_ACTION` 一等公民：合法、可审批、可学习、必须成包 |
| RE-P5 | 假设必须可反驳 | GA-1 §6.4, §8.4 | 每个写动作候选必须携带 observation → cause_claim + confidence + rival_hypotheses |
| RE-P6 | 响应窗口内不重调 | GA-1 §8.6 | 候选必须声明 expected_response_window；未过窗不产生同向二次调整候选 |
| RE-P7 | 门禁前置感知、后置不越权 | 架构 §5；Gate §2.3 | RE 可读 Risk/Trust 预览以收敛候选；RE 不写 review_result、不执行、不绕过 Adapter |
| RE-P8 | 双时间尺度 | GA-1 §8.3 | 同时支持日内干预骨架与长周期（7/14/30d）骨架 |
| RE-P9 | 场景可插拔 | 架构 P8 | 骨架是模板不是硬编码；域 Agent / 商品类目可注册新骨架 |
| RE-P10 | 降级可解释 | 架构 P6；FE-P7 | 低置信 / 缺预测 / 状态 gap 时显式降级到 HOLD / NO_ACTION，不伪精确 |

---

## 2. 输入契约

### 2.1 输入总览

```text
ReasoningRequest {
  request_id*           : string          // 前缀 RE-REQ-
  triggered_by*         : enum {
    CBA_DECISION_LOOP,        // 回路 A 常规
    FE_FOLLOWUP,              // FE 补充预测后重推理
    SRA_REVISE,               // REVISE 修订重提
    HUMAN_MODIFY,             // 人类修改后重推理
    PERIODIC_REFRESH          // 周期刷新
  }
  state_ref*            : ref             // TrustedBusinessState.state_id
  forecast_bundle_ref*  : ref             // ForecastBundle.bundle_id（或 inline，见 §2.3）
  objective_snapshot*   : object          // OFG 输出（§2.5）
  knowledge_refs*       : object[]        // KE 版本锁定引用（§2.4）
  risk_trust_preview*   : object          // 只读预览（§2.6）
  scope*                : {
    shop_id*            : ref
    plan_ids?           : ref[]
    campaign_ids?       : ref[]
    skus?               : ref[]
  }
  decision_intent?      : enum            // CBA 可指定意图：INTRADAY_INTERVENTION | STABILITY_CHECK | BUDGET_LIFE | CAMPAIGN_PREP | INVENTORY_GUARD | AUTO
  prior_decision_id?    : ref             // REVISE / HUMAN_MODIFY 时的上游包
  scenario_hint?        : enum            // 可选骨架提示，见 §4
  runtime_envelope      : RuntimeEnvelope // 透传 SHADOW/LIVE 标签
  as_of*                : timestamp
}
```

### 2.2 Trusted Business State（STATE）

RE **不直接调用 Adapter**。唯一状态源是 STATE 组装的 `TrustedBusinessState`（对齐 FE §2.2 与 JD Adapter `BusinessState`）。

| BusinessState 字段 | RE 用途 | 缺失时行为 |
|---|---|---|
| `state_id` / `as_of` | 决策时间锚；写入 `state_digest` | 必填，缺失则请求非法 |
| `trusted_metrics_by_plan` | 观察面（observation）与基线对比 | 该 plan 不进入写动作候选；倾向 NO_ACTION / HOLD |
| `plan_mode` / `lifecycle_phase` | 场景骨架路由与动作白名单 | `UNKNOWN` 时倾向 ADVISE / HOLD，不提强写动作 |
| `inventory_by_sku` / `inventory_risk` | 库存紧张骨架；CHK_INV 预判 | 缺库存源时禁扩量/新建候选（Risk R3+ 语义） |
| `budget`（BudgetPosition） | 预算寿命骨架 | 缺预算数据时禁 BUDGET / CREATE 候选 |
| `active_events[]` | 活动期骨架 | 无活动时按常态骨架 |
| `confidence` / `validation_confidence` | RE 整体候选上限 | `LOW` 时禁止写动作候选（见 §7） |
| `ready_for_forecast` / `gap_flags[]` | 与 FE 降级联动 | FE BLOCKED 时 RE 仅 NO_ACTION / HOLD |
| `working_context_id` | 近窗调整历史（response window） | 缺失时使用更保守冷却先验（Proposed） |

> **硬约束：** RE 消费的指标必须能回指 `ValidatedMetricSet` / `validated_id`。Raw 指标不得进入 hypothesis.observation（DPK-I3）。

### 2.3 ForecastBundle（FE）

对齐 `Forecast_Engine_Interface_v0.1.md` §4/§5：

```text
RE 消费：
  ForecastBundle {
    bundle_id, state_id, as_of,
    status: OK | DEGRADED | BLOCKED,
    objects: ForecastObject[],          // 完整对象，不只 summary
    summary: { ... },                   // FE §4.2
    overall_confidence,
    degraded_targets[], gap_flags[],
    based_on_validated_ids[]
  }
```

| FE 产物 | RE 用途 |
|---|---|
| `FC-CURVE-*` 曲线与分位带 | 日内/长周期观察与 expected_effect 方向幅度 |
| `FC-ETA-BUDGET` | 预算寿命骨架主输入 |
| `FC-STAB-PLAN`（stability_score / noise_threshold） | 收割稳定性骨架；`improvement_if_adjust=below_noise` → NO_ACTION 强信号 |
| `FC-BURST-CAMPAIGN`（burst_prob / peak_window） | 活动期骨架主输入 |
| `FC-RISK-INVENTORY` | 库存紧张骨架；放量前硬约束 |
| `summary.overall_confidence` | CHK_CONF 预判；低于阈值触发 §7 |

**FE 状态 × RE 行为（对齐 FE §7）：**

| FE status | RE 允许产出 |
|---|---|
| `OK` | 完整候选集（含写动作或 NO_ACTION） |
| `DEGRADED`（轻） | 写动作可保留，但 hypothesis.supporting_signals 必须标注「基于降级预测」 |
| `DEGRADED`（重，关键对象跳过） | 相关场景倾向 HOLD / NO_ACTION；缺失对象相关写动作不产出 |
| `BLOCKED` | 仅 `NO_ACTION` 候选（DPK-I2 仍须成包） |

### 2.4 Knowledge refs（KE）

| 知识对象 | RE 用途 | 引用方式 |
|---|---|---|
| Rule / Strategy | 动作类型白名单、幅度先验、场景路径 | `knowledge_refs[]`，锁定 `id@version` |
| Parameter Genome | 调整策略、prefer_stability、期望窗口、目标模板引用 | `genome_ref` |
| Experience / Case | 同类场景成功/失败先验；支撑 hypothesis.knowledge_basis | `knowledge_basis[]` |
| Failure Pattern | 规避已知失败路径 | supporting_signals / rival_hypotheses |

> 新场景无匹配知识时：`knowledge_basis=[]`，RE 不得假装“有模板”；SRA 可走 ESC-06。

### 2.5 Objective Snapshot（OFG）

对齐 `Parameter_Genome_Templates_v0.1.md` §5.5 与 Decision Packet `objective_snapshot`：

```text
ObjectiveSnapshot {
  template_id*      : string            // 如 T-MHB-SEED / T-MHB-HARVEST
  weights*          : map<string,number> // 六指标，Σ=1
  lifecycle_bias?   : string
  explanation?      : string
  valid_until?      : timestamp
}
```

RE **只读**该快照并写入 Decision Packet；不得在推理中途改权重（DPK-I7）。

### 2.6 Risk / Trust 预览

RE 可在组装 Draft 前读取**只读预览**（由 RKE/TE 或 CBA 编排提供），用于收敛候选、降低必然被 REJECT 的动作：

```text
RiskTrustPreview {
  risk_level_hint     : R0..R4 | UNKNOWN
  hard_block_flags    : string[]        // 非空则 RE 不应产出对应写动作
  max_bid_delta_pct   : number          // Proposed 来自 Risk constraints
  max_budget_delta_pct: number
  max_daily_adjust_count : number
  min_response_window_minutes : number
  allow_new_plan      : bool
  trust_actual        : int 0..5
  trust_required_map  : map<action_class, int>
  baseline_version    : string
  trust_version       : string
}
```

**边界：** 预览仅供 RE 收敛候选；**最终** `risk.*` / `trust.*` 由 RKE/TE 写入 Decision Packet，`review_result` 仅 SRA 写入（Gate §4.3）。预览与正式评估不一致时，以正式评估为准。

---

## 3. 输出契约

### 3.1 ReasoningBundle 总览

```text
ReasoningBundle {
  bundle_id*            : string          // 前缀 RE-
  request_id*           : ref
  state_id*             : ref
  forecast_bundle_id*   : ref
  objective_snapshot_ref : ref / inline
  status*               : enum { OK, DEGRADED, BLOCKED, NO_ACTION_ONLY }
  primary_candidate_id? : ref             // 推荐主候选；NO_ACTION 时指向 NO_ACTION 候选
  candidates*           : ReasoningCandidate[]
  no_action_candidate?  : ReasoningCandidate   // 当 status 含 NO_ACTION 语义时必填
  scenario_skeleton_id  : string          // 命中的骨架，如 SC-SEED-INTRADAY-DROP
  knowledge_basis_used  : string[]
  confidence_self*      : number          // RE 自评 [0,1]（非 FE confidence）
  degrade_reasons*      : string[]
  created_at*           : timestamp
  runtime_envelope      : RuntimeEnvelope
}
```

> **硬规则：**  
> 1. `candidates` 中非 `NO_ACTION` 的写动作候选，最终进入 Decision Packet 时必须走完整门禁。  
> 2. RE **从不**输出 `review_result`、`lifecycle_status=Self-reviewed`、`executor` 执行确认。  
> 3. `status=BLOCKED` 时仅允许 `no_action_candidate`（或 HOLD 语义候选，见 §7）。

### 3.2 ReasoningCandidate 结构

```text
ReasoningCandidate {
  candidate_id*         : string          // 前缀 REC-
  candidate_role*       : enum { PRIMARY, ALTERNATIVE, NO_ACTION, HOLD_SUGGEST }
  action_class*         : enum {
    KEYWORD_BID, AUDIENCE_PREMIUM, BUDGET, ROI_TARGET,
    PLAN_CONTROL, CREATE_PLAN, NO_ACTION
  }
  hypothesis*           : object          // §3.3
  proposed_actions*     : object[]        // §3.4；NO_ACTION 时单元素 WA-CLS-01
  expected_response_window* : object      // §3.5
  expected_effect?      : object          // §3.6
  no_action_reason?     : string          // 当且仅当 action_class=NO_ACTION
  hold_reason?          : string          // HOLD_SUGGEST 时
  objective_alignment   : object          // 与 weights 的对齐说明
  risk_awareness        : object          // RE 基于预览的自评，非最终 risk.*
  knowledge_basis       : string[]
  rival_hypotheses      : string[]
  scenario_skeleton_id  : string
}
```

### 3.3 hypothesis（观察 → 假设）

对齐 Decision Packet `hypothesis`（Schema §2.4）：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `observation` | object | Y | 窗口、指标、delta、baseline_ref、state_id；必须可回指 Trusted State |
| `cause_claim` | string | Y | 原因判断（自然语言或结构化码） |
| `confidence` | number [0,1] | Y | 假设置信；低于阈值触发 §7 |
| `supporting_signals` | object[] | N | 支撑信号；DEGRADED 预测必须标注 |
| `rival_hypotheses` | string[] | N | 备择假设（可反驳性） |
| `knowledge_basis` | string[] | N | 命中知识对象 ID@version |

### 3.4 proposed_actions[] 元素

对齐 Decision Packet §2.5 / JD `AbstractActionRequest` 语义（非 API 名）：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `action_id` | string | Y | 包内唯一，`ACT-` 前缀 |
| `action_type` | enum | Y | `WA-BID-01` 等平台语义动作 |
| `action_class` | enum | Y | 见 §3.1 |
| `target` | object | Y | plan_id / keyword_id / audience_id 等 |
| `change` | object | Y* | field / from / to / relative_pct；`NO_ACTION` 除外 |
| `priority` | int | N | 同候选内执行序 |
| `rationale_ref` | string | Y | 指向 hypothesis 段 |
| `within_risk_preview` | bool | Y | 是否落在 Risk 预览幅度/频率内（自评，非最终门禁） |

**幅度自评（Proposed，与 Risk §7.2 对齐）：**

| Risk 预览档 | 建议出价幅度上限 | 建议预算幅度上限 |
|---|---|---|
| R0–R1, L≥2 | 10%–20% | 10%–20% |
| R2 | 5%–10% | 5%–10% |
| R3 | 0%–5% 或不产出写动作 | 极小或不产出 |
| R4 / hard_block 非空 | **不产出写动作** | **不产出** |

> RE 超预览幅度产出的候选可保留为 ALTERNATIVE，但应标记 `within_risk_preview=false`，预期被 SRA REVISE/REJECT。

### 3.5 expected_response_window（调整响应窗口）

对齐 GA-1 §8.6 与 Decision Packet `expected_response_window`：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `min_minutes` | int | Y | 先验下界；Genome `response_window_hours` 可参考 |
| `max_minutes` | int | Y | 先验上界 |
| `metric_hint` | string[] | Y | 预期响应指标 |

**Proposed 先验（非真值）：**

| 动作类 | min_minutes | max_minutes | metric_hint 常见 |
|---|---:|---:|---|
| KEYWORD_BID（种草） | 120 | 360 | impressions, clicks |
| AUDIENCE_PREMIUM | 120 | 480 | clicks, ctr |
| BUDGET | 180 | 720 | spend, clicks, gmv |
| ROI_TARGET | 240 | 1440 | roi, spend, gmv |
| PLAN_CONTROL | 30 | 180 | spend, status |
| CREATE_PLAN | 240 | 2880 | impressions, clicks, add_cart |
| NO_ACTION | 0 | 1440 | trusted_roi, spend（观察是否仍稳） |

> 同对象同向调整在 `max_minutes` 内不得再次进入 PRIMARY 候选（RE-P6）；G-08 由 Adapter 最终硬检。

### 3.6 expected_effect（预期效果）

| 字段 | 类型 | 说明 |
|---|---|---|
| `direction` | enum | `recover` / `accelerate` / `stabilize` / `reduce_waste` / `hold` |
| `metric_targets` | map | 如 `{impressions: ">= baseline * 0.85"}` |
| `side_effect_notes` | string[] | 如 CPC 上行 |

### 3.7 NO_ACTION 候选（一等公民）

```text
NO_ACTION Candidate {
  candidate_role: NO_ACTION,
  action_class: NO_ACTION,
  proposed_actions: [{ action_type: WA-CLS-01, action_class: NO_ACTION, target, rationale_ref }],
  no_action_reason*: string,     // 必填
  expected_response_window: { min_minutes: 0, max_minutes: 观察窗, metric_hint },
  expected_effect: { direction: "hold", ... },
  hypothesis: 观察“为何不必动”（噪声/稳定/学习中/数据不足）
}
```

**合法 NO_ACTION 触发条件（任一，Proposed）：**

| 条件来源 | 条件 |
|---|---|
| FE | `improvement_if_adjust=below_noise`；`within_band_prob ≥ 0.8`；`stability_class=HIGH` |
| FE | `status=BLOCKED` 或 `overall_confidence < 0.5` |
| STATE | `validation_confidence=LOW`；关键 gap_flags |
| Genome / Objective | `prefer_stability=true` 且无显著恶化证据 |
| Risk 预览 | hard_block / R4；或写动作将违规 |
| 场景 | 收割成熟计划无恶化；响应窗口未到 |

> NO_ACTION **仍必须成包**并走 SRA（`NO_ACTION_APPROVE`），写 CausalRecord，计入稳定性与 T2/T8 样本（DPK-I2；Decision Packet §5.3）。

### 3.8 HOLD_SUGGEST 候选

当 RE 认为“现在不应写动作，且不是稳定的 NO_ACTION，而是信息不足/窗口未到”：

- `candidate_role=HOLD_SUGGEST`；`hold_reason` 必填；  
- 不进入执行路径；CBA/SRA 可映射为 `review_result=HOLD`；  
- 与 NO_ACTION 区分：NO_ACTION 是“有意识维持”；HOLD 是“暂缓、待条件满足再审”。

---

## 4. 场景推理骨架（Scenario Skeleton）

### 4.1 骨架模型

```text
ScenarioSkeleton {
  skeleton_id*          : string          // SC-*
  name*                 : string
  applies_when*         : object          // plan_mode / lifecycle / event / inventory 条件
  observation_panels*   : enum[]          // 优先读取哪些预测/状态面板
  hypothesis_cluster*   : object[]        // 候选原因及鉴别信号
  action_candidates*    : object[]        // 允许的动作类与幅度倾向
  stability_gate*       : object          // NO_ACTION / HOLD 门槛
  objective_hint?       : ref             // 常配合的目标模板
  risk_trust_floor?     : object          // 最低 Trust / 典型 Risk 档
  theory_anchor?        : string
}
```

> 骨架是**推理路径模板**，不是 if-else 剧本。RE 可同时命中多骨架，按 `applies_when` 优先级与 Objective 对齐度选择 PRIMARY。

### 4.2 SC-SEED-INTRADAY-DROP：种草获量下滑

| 属性 | 内容 |
|---|---|
| **applies_when** | `plan_mode=SEEDING`；日内曲线显著低于同时段基线 |
| **theory** | GA-1 §6.2 预测驱动；§7.3 种草更高频调整；§7.2 中高客单点击/触达优先 |
| **observation_panels** | FC-CURVE-IMPRESSION / CLICK / CTR 相关；state 日内分时；竞品/类目信号（可得则用） |
| **hypothesis_cluster** | ① 关键词竞争增强（排名份额↓、类目竞价↑）② 素材疲劳（CTR 单调衰减）③ 人群包过窄 ④ 平台延迟/数据异常（BDV gap） |
| **action_candidates** | PRIMARY 常为 KEYWORD_BID 或 AUDIENCE_PREMIUM，幅度在 Risk 预览内（R2 常见 5%–10%）；ALTERNATIVE 可并列 |
| **stability_gate** | 若仅轻微偏离噪声带或 FE DEGRADED 关键曲线缺失 → HOLD / NO_ACTION |
| **expected_window** | 种草出价：Proposed 2–6h；metric: impressions, clicks |
| **objective_hint** | `T-MHB-SEED` / `T-LFM-SEED` |

**推理伪路径（非实现代码）：**

```text
1. 读 summary.impression_trend / click_trend 与完整曲线分位带
2. 对比 baseline_ref（近 7 日同时段）
3. 若 |delta| < noise_threshold → NO_ACTION（稳定）
4. 若 FE BLOCKED 或 confidence 过低 → HOLD_SUGGEST 或 NO_ACTION
5. 按 hypothesis_cluster 鉴别信号排序 cause_claim
6. 生成 1 个 PRIMARY + 0–2 个 ALTERNATIVE 动作候选（幅度 ≤ Risk 预览）
7. 写 expected_response_window 与 expected_effect
8. 若 risk_preview.hard_block 非空或 trust 不足对应动作类 → 改 NO_ACTION/HOLD 并写原因
```

### 4.3 SC-BUDGET-LIFETIME：预算寿命

| 属性 | 内容 |
|---|---|
| **applies_when** | `FC-ETA-BUDGET.projected_exhaust_at` 早于目标经营时段；或 `budget_lifetime ∈ {tight, critical, exhausted_soon}` |
| **theory** | GA-1 §6.2 预算耗尽时间；§8.3 双时间尺度；§11.1 预算红线 |
| **observation_panels** | FC-ETA-BUDGET；FC-CURVE-SPEND；BudgetPosition |
| **hypothesis_cluster** | ① 燃烧过快（竞价/流量结构）② 预算设置过低 ③ 晚高峰抢量预期 ④ 异常消耗 |
| **action_candidates** | 预算仍安全但晚间需抢量 → 小步 BUDGET；已触红线风险 → **不**产出加预算写动作，改 NO_ACTION/HOLD 或 PLAN_CONTROL（降速） |
| **stability_gate** | 预算红线 / Risk R3–R4 / hard_block → 禁止加预算候选 |
| **expected_window** | BUDGET：Proposed 3–12h；metric: spend, exhaust_at, gmv |
| **objective_hint** | 依 plan_mode；活动期可临时 Campaign Overlay |

### 4.4 SC-HARVEST-STABILITY：收割稳定性

| 属性 | 内容 |
|---|---|
| **applies_when** | `plan_mode=HARVEST`；常 `lifecycle=mature`；`prefer_stability=true` 或 system_managed |
| **theory** | GA-1 §7.3 收割强调稳定；§8.5 稳定性优先；§8.4 噪声 vs 趋势 |
| **observation_panels** | FC-STAB-PLAN；FC-CURVE-ROI（within_band_prob）；trusted_roi 基线带 |
| **hypothesis_cluster** | ① 正常噪声（主）② 真实恶化（需证据）③ 系统学习中，不应打断 |
| **action_candidates** | **默认 PRIMARY = NO_ACTION**；仅当“显著恶化证据”充分时才产出极小步 ROI_TARGET/BUDGET/BID 候选 |
| **stability_gate** | `stability_class=HIGH` 且 `improvement_if_adjust=below_noise` → 强制 NO_ACTION；无显著恶化 → NO_ACTION |
| **expected_window** | NO_ACTION 观察窗 Proposed 至日终或 24h |
| **objective_hint** | `T-MHB-HARVEST` / `T-LFM-HARVEST`；weights 含较高 gmv_roi 与稳定性偏好 |

### 4.5 SC-CAMPAIGN-WINDOW：活动期

| 属性 | 内容 |
|---|---|
| **applies_when** | `active_events[]` 非空；`event_phase ∈ {PRE, LIVE, PEAK_WINDOW}`；或 `burst_prob` 高 |
| **theory** | GA-1 §7.4 活动爆发期动态提高种草/收割；§6.2 活动爆发周期；§11.1 动态放宽 ROI 保障获量 |
| **observation_panels** | FC-BURST-CAMPAIGN；活动日历；预算寿命；库存（放量前强制看） |
| **hypothesis_cluster** | ① 峰值窗口前需蓄水/抢量 ② 窗口内获量不足 ③ 峰值后回落风险（post_burst_falloff_risk） |
| **action_candidates** | PRE：可提 BUDGET/KEYWORD_BID 蓄水；PEAK：在 Risk 放宽窗口内提获量动作；POST：倾向收敛/NO_ACTION，防浪费 |
| **stability_gate** | 无活动却强放量 → 降级；库存紧张叠加活动 → 禁止扩量写动作 |
| **expected_window** | 对齐 expected_peak_window；短窗 Proposed 15–120min（PEAK） |
| **objective_hint** | Campaign Overlay / lifecycle_bias=`campaign_go`；允许短期 ↓ gmv_roi 权重 |

### 4.6 SC-INVENTORY-TIGHT：库存紧张

| 属性 | 内容 |
|---|---|
| **applies_when** | `inventory_risk ∈ {TIGHT, CRITICAL}` 或 `FC-RISK-INVENTORY` 投影断货临近 |
| **theory** | GA-1 §6.3 库存感知；§11.1 库存紧张限制加预算/暂停扩量、禁止新建 |
| **observation_panels** | FC-RISK-INVENTORY；GMV/销量曲线；BudgetPosition |
| **hypothesis_cluster** | ① 去化过快需降速 ② 断货将毁计划稳定性 ③ 清仓期需反向加快收割（Decline_Clearance） |
| **action_candidates** | TIGHT：禁 CREATE_PLAN；限 BUDGET 扩量；可 PLAN_CONTROL 降速或维持；CRITICAL：默认 NO_ACTION/HOLD 或明确止损类候选（若 Trust/Risk 允许） |
| **stability_gate** | 库存 CRITICAL + 扩量写动作 → RE **不产出**该类 PRIMARY；写入 degrade_reasons |
| **expected_window** | 按动作；库存投影 horizon 3–14d |
| **objective_hint** | 成熟/清仓偏 gmv_roi；探索期仍禁扩种草新建 |

### 4.7 骨架速查表

| skeleton_id | 主触发 | 默认倾向 | 禁写动作（预览下） |
|---|---|---|---|
| SC-SEED-INTRADAY-DROP | 种草日内获量↓ | 小步 BID/PRM | hard_block 时全部写动作 |
| SC-BUDGET-LIFETIME | 预算将尽/过快 | 依红线：加预算或降速/NA | 触红线时禁加预算 |
| SC-HARVEST-STABILITY | 收割成熟稳定 | **NO_ACTION** | 无显著恶化时禁“刷存在感”微调 |
| SC-CAMPAIGN-WINDOW | 活动 PRE/PEAK | 窗口内获量 | POST/库存紧时禁扩量 |
| SC-INVENTORY-TIGHT | 库存 TIGHT/CRITICAL | 降速/维持/NA | 禁新建与大幅扩量 |

---

## 5. 与 Objective Function Generator 的关系

### 5.1 职责切分

| 维度 | OFG | RE |
|---|---|---|
| 输入 | 商品价格带、plan_purpose、lifecycle、库存、活动、企业目标、Risk 档 | Trusted State + ForecastBundle + Objective Snapshot + Knowledge + Risk/Trust 预览 |
| 输出 | `ObjectiveSnapshot`（weights、template_id、bias、explanation） | ReasoningBundle（hypothesis、actions、window 或 NO_ACTION） |
| 不做什么 | 产出动作；固定全局 ROI | 改写 weights；自造与理论序冲突的目标 |

### 5.2 调用时序（回路 A）

```text
CBA（或编排器）
  → OFG.generate(context) → ObjectiveSnapshot
  → RE.reason(ReasoningRequest{ objective_snapshot, state, forecast_bundle, ... })
  → RE 产出 ReasoningBundle
  → CBA 组装 Decision Packet Draft（objective_snapshot 原样快照）
  → RKE / TE / SRA
```

- OFG **先于** RE；RE 不回调 OFG 改权重。  
- 若 CBA 未提供合法 Objective Snapshot，RE 应拒绝产出写动作候选（`status=DEGRADED`，`degrade_reasons` 含 `MISSING_OBJECTIVE`），仅 NO_ACTION/HOLD。  
- `valid_until` 已过期的目标快照：RE 标记降级，不静默沿用。

### 5.3 RE 如何消费 weights

| 用途 | 方式 |
|---|---|
| 动作方向对齐 | 例如种草 weights 偏 ctr/clicks → 获量类动作优先；收割偏 gmv_roi → 稳定与成交优先 |
| expected_effect 指标选择 | metric_targets 优先覆盖高权重指标 |
| PRIMARY vs ALTERNATIVE 排序 | 与高权重指标改善方向一致者优先 |
| NO_ACTION 判定辅助 | 预测改进主要落在低权重指标且低于噪声 → 更倾向 NO_ACTION |
| objective_alignment 字段 | 生成人类可读对齐说明，供 SRA CHK_GOAL |

> RE **不得**为了短期高权重指标突破 Risk 硬约束或库存/预算红线（Risk 硬于目标偏好；Gate §4.3）。

---

## 6. Decision Packet 字段映射

### 6.1 映射总表（RE 输出 → Packet）

| RE 输出 | Decision Packet 字段 | 来源组件 | 可变性 |
|---|---|---|---|
| —（编排） | `decision_id` / `schema_version` / `status=Draft` | CBA | F / W |
| ObjectiveSnapshot 原样 | `objective_snapshot` | OFG | F |
| state 摘要 | `state_digest.*` | STATE/CBA | F |
| ForecastBundle | `forecast_ref.*` | FE | F |
| knowledge 引用 | `knowledge_refs` / `genome_ref` | KE | F |
| **hypothesis** | `hypothesis.*` | RE | F |
| **proposed_actions** | `proposed_actions[]` | RE→CBA | F |
| **expected_response_window** | `expected_response_window.*` | RE | F |
| **expected_effect** | `expected_effect` | RE/FE | F |
| **no_action_reason** | `no_action_reason` | RE | F |
| —（门禁后写） | `risk.*` | RKE | F |
| —（门禁后写） | `trust.*` | TE | F |
| —（终审） | `review.*` / `review_result` | **仅 SRA** | A |
| —（执行） | `executor` / `action_receipts` | CBA/JDA/ADAPT | F / A |
| —（观察/反思） | `outcome_ref` / `reflection_ref` | JDA/ME/RFE | R |

### 6.2 装配顺序（Gate §5.2）

```text
1. RE 填充 hypothesis / proposed_actions / expected_* / no_action_reason
2. RKE 写入 risk（含 hard_block）
3. TE 写入 trust_required / trust_actual
4. SRA 写入 review（REVISE → 回 RE 重推理；不缓存旧 Risk/Trust）
5. CBA 下发时校验双字段可执行（Gate §1.1）
6. ADAPT G-01..G-09 最终硬闸
```

### 6.3 NO_ACTION 专用路径

| 步骤 | 行为 |
|---|---|
| RE | `proposed_actions=[{WA-CLS-01, NO_ACTION}]`；填 `no_action_reason`；完整 hypothesis |
| SRA | 谓词含 `CHK_STAB`；结果 `NO_ACTION_APPROVE` |
| JDA/ADAPT | 不调用平台写；合成 `NOT_APPLICABLE_NO_ACTION` 回执 |
| ME | 仍写 CausalRecord |
| RFE | 评估“不调整是否正确”，计入稳定性与 T8 |

### 6.4 REVISE 回路

```text
SRA review_result=REVISE
  → RE 以 prior_decision_id + revise_round+1 重推理
  → 必须重新拉取/引用最新 state 与 forecast（或显式声明沿用的 forecast_id 仍有效）
  → 重新走 Risk → Trust → SRA（Gate §4.3 第 5 条）
  → revise_round ≤ N_revise（Proposed=2），超出 → ESCALATE_HUMAN（ESC-04）
```

---

## 7. 低置信 / 缺预测 / 预拒绝行为

### 7.1 降级阶梯（RE 侧，对齐 FE §7）

```text
Level 0: 正常
  → 完整候选集；PRIMARY 写动作或 NO_ACTION

Level 1: 轻度降级（DEGRADED）
  → 写动作可保留，但 supporting_signals 标注降级来源
  → confidence_self 下调；建议 SRA 收紧 CHK_CONF

Level 2: 重度降级
  → 跳过依赖缺失预测对象的写动作候选
  → PRIMARY 可为 HOLD_SUGGEST 或 NO_ACTION
  → degrade_reasons 显式列出

Level 3: 阻断（BLOCKED）
  → 仅 NO_ACTION（或 HOLD_SUGGEST，不进入执行）
  → Decision Packet 仍须成包（DPK-I2）
```

### 7.2 触发条件与行为表

| 触发条件 | 级别 | RE 行为 | 对门禁的影响 |
|---|---|---|---|
| FE `status=BLOCKED` / STATE `ready_for_forecast=false` | L3 | 仅 NO_ACTION | SRA 仅可 `NO_ACTION_APPROVE` |
| FE `overall_confidence < 0.6`（Proposed，写动作门槛） | L2–L3 | 非 NO_ACTION 写动作不产出或降 ALTERNATIVE | CHK_CONF 倾向 HOLD |
| FE `overall_confidence < 0.5`（Proposed，整体不可靠） | L3 | 强制 NO_ACTION 路径 | 同上 |
| STATE `validation_confidence=LOW` | L3 | 禁写动作（Packet Schema 明文） | 仅 NO_ACTION/HOLD |
| 关键曲线对象缺失（impression/click） | L2 | 种草日内骨架 HOLD/NA | CHK_CONF/CHK_MODEL |
| FC-ETA-BUDGET 缺失 | L2 | 禁 BUDGET/CREATE PRIMARY | CHK_BUD |
| FC-RISK-INVENTORY 缺失 | L2 | 禁扩量/新建 PRIMARY | CHK_INV；Risk R3+ |
| risk_preview.hard_block 非空 | L2–L3 | 不产出对应写动作；改 NA/HOLD | SRA 必 REJECT 若强行 APPROVE |
| trust_actual < 动作所需档 | L2 | 收敛到信任半径内动作或 ADVISE/NA | CHK_TRUST / G-02 |
| 无 Knowledge 匹配且场景高风险 | L2 | 标记 knowledge_basis=[]；倾向 HOLD | ESC-06 |
| hypothesis.confidence < Proposed 0.55 | L1–L2 | 降 ALTERNATIVE 或 HOLD | CHK_CONF |
| 同对象未过 min_response_window | L2 | 不产出同向 PRIMARY | CHK_WINDOW / G-08 |
| OFG 快照缺失或过期 | L2 | 禁写动作；MISSING_OBJECTIVE | CHK_GOAL |

### 7.3 预拒绝（Pre-reject）语义

> **预拒绝 = RE 在成包前避免产出“必然失败”的候选，不是替 SRA/Adapter 做终审。**

| 预拒绝类型 | RE 行为 | 是否仍成包 |
|---|---|---|
| 必然 hard_block | 不产出该写动作 PRIMARY | 若无其他候选 → NO_ACTION 包 |
| 必然 Trust 不足 | 收敛到允许动作类，或 ADVISE/NA | 同上 |
| 必然违反 response window | 不产出同向动作 | NO_ACTION/HOLD |
| 预测整体不可信 | 仅 NO_ACTION | **是**（NO_ACTION 包） |
| Shadow 环境 | 候选完整，execution_mode 由 CBA 标 SHADOW_READ_ONLY | 是；写路径由 G-01-S 硬拒绝 |

**不变量：**

1. RE 预拒绝**不能**跳过 Decision Packet 生命周期。  
2. RE 预拒绝**不能**写 `review_result=REJECT`（仅 SRA 可写）。  
3. 被预拒绝的意图应写入 `degrade_reasons` / `no_action_reason` / `hold_reason`，供 RFE 分析“是否误杀”。

---

## 8. 理论追踪

| 理论主张 | GA-1 锚点 | 本文落点 | 覆盖 |
|---|---|---|---|
| Prediction-driven Decision | §6.2, GA-INNOV-002 | §1.4 RE-P1；§2.3 FE 为一等输入；§4 骨架以预测面板驱动 | Mapped |
| Business State Awareness | §6.3, GA-INNOV-003 | §2.2 强制 Trusted State；Raw 禁入 hypothesis | Mapped |
| 动态目标函数 | §7.2–7.4, §8.2 | §2.5；§5 OFG 关系；objective_alignment | Mapped |
| 双时间尺度决策 | §8.3 | §1.4 RE-P8；骨架覆盖日内与长周期 | Mapped |
| 决策可信度验证 | §8.4 | §3.3 confidence；§7 降级阶梯 | Mapped |
| 稳定性优先原则 | §8.5 | §3.7 NO_ACTION 一等公民；SC-HARVEST-STABILITY | Mapped |
| 调整响应窗口 | §8.6 | §3.5；RE-P6；§7.2 window 预拒绝 | Mapped |
| 种草 vs 收割差异 | §7.3 | SC-SEED-INTRADAY-DROP / SC-HARVEST-STABILITY | Mapped |
| 生命周期策略 | §7.4 | 骨架 applies_when；objective_hint；Campaign Overlay | Mapped |
| 库存与风险感知 | §6.3, §11.1 | SC-INVENTORY-TIGHT；Risk 预览收敛 | Mapped |
| Trust-based 权限成长 | §6.7 | §2.6 trust 预览；候选动作半径收敛 | Mapped |
| Experience / Failure 学习 | §6.4, §9 | hypothesis 可反驳；knowledge_basis；NO_ACTION 入 Causal | Mapped |
| Shadow / 只读红线 | GA-DEC-004 | §7.3 Shadow 预拒绝；不绕过门禁 | Mapped |
| 预测对象清单 | §6.2 | 消费 FE Catalog；§2.3 | Mapped（FE 主责） |

**明确不声称：** 本文全部置信度阈值、幅度、窗口、噪声门限均为 Proposed 工程预标定，不是 GA-1 理论结论；有效性待 GA-3 验证。本文不实现任何推理算法或真实广告操作。

---

## 9. 待决问题

| ID | 问题 | 建议（Draft） | 阻塞 | 归属 |
|---|---|---|---|---|
| RE-Q01 | RE 内核形态（规则引擎 / LLM / 混合）是否本文锁定？ | **不锁定**；接口契约优先；实现选型后置 | 否 | 实现阶段 |
| RE-Q02 | 多骨架同时命中时 PRIMARY 选择函数如何形式化？ | 先规则：applies_when 特异性 > objective 对齐度 > risk 安全边际 | 否 | 联调 |
| RE-Q03 | Risk/Trust 预览的刷新时机（每包 vs 缓存）？ | 每包强制读取正式评估结果；预览仅 Draft 收敛用 | 否 | Gate 联调 |
| RE-Q04 | hypothesis.confidence 与 FE overall_confidence 如何合成进 CHK_CONF？ | SRA 使用 min(RE, FE) 与区间宽度联合判定（Proposed） | 否 | SRA 标定 |
| RE-Q05 | HOLD_SUGGEST 与 SRA HOLD 的权威边界？ | RE 只建议；`review_result=HOLD` 仅 SRA 写 | 否 | 已定原则 |
| RE-Q06 | REVISE 时是否必须新 forecast_id？ | 若原 bundle 仍新鲜（Proposed <30min）可沿用；否则强制刷新 | 否 | 运行时 |
| RE-Q07 | 骨架目录是否按京东域单独版本化？ | 先核心五骨架；域扩展由 JDA 注册，不改核心契约 | 否 | P8 |
| RE-Q08 | NO_ACTION 的 expected_effect 如何度量“维持正确”？ | 日终 trusted_roi/主指标仍落在基线带；RFE 标定 | 否 | RFE |
| RE-Q09 | RE confidence_self 的校准样本从哪来？ | Shadow 包 + 后验 outcome；默认不计入 Trust | 否 | GA2-T11 |
| RE-Q10 | 一包多动作时 RE 如何保证动作间无冲突？ | 同候选内 priority + 互斥规则（如清仓与扩种草互斥）；冲突则拆包或去低优先 | 否 | 联调 |
| RE-Q11 | 抖音场景骨架何时扩展？ | 占位；JD 验证后再设计 | 否 | 后置 |
| RE-Q12 | 与 FE `data_requests` 的联动是否需要 RE 发起？ | 否；RE 只降级；补数由 STATE/CBA 编排 | 否 | 已对齐 FE |

---

## 10. 与后续任务的接口

| 下游 | 本文供给 |
|---|---|
| Decision Packet（GA2-T10） | RE 字段映射（§6）；NO_ACTION 成包语义 |
| Gate Integration（GA2-T19） | RE 层职责；REVISE 回路；预拒绝不越权 |
| Risk/Trust/SRA（GA2-T05） | 预览消费边界；hypothesis 置信输入；HOLD 建议语义 |
| Forecast Engine（GA2-T13） | 消费 ForecastBundle；DEGRADED/BLOCKED 行为 |
| OFG / Genome（GA2-T07） | Objective Snapshot 消费；prefer_stability；response window 先验 |
| Shadow Mode（GA2-T11） | Shadow 下完整候选；confidence_self 校准样本格式 |
| GA-3 验证 | 骨架命中率、NO_ACTION 正确率、REVISE 循环效率指标定义 |

---

## 11. 变更记录

| 日期 | 版本 | 变更 | 依据 |
|---|---|---|---|
| 2026-09-11 | v0.1 | 首次建立 RE 接口：定位与非目标、输入/输出契约、五类场景骨架、OFG 关系、Decision Packet 映射、低置信/缺预测/预拒绝、理论追踪与待决 | GA2-T23；Architecture v0.2；GA-1 §6.2/§7/§8；Forecast_Engine_Interface；Decision_Packet_Schema；Gate_Integration_Playbook v0.2；Risk_Trust_SelfReview |

---

**Document Status:** Draft  
**Next Review:** 项目负责人 / Research Architect  
**Explicit Non-claim:** 本文不代表已实现任何推理引擎或接入真实数据源；所有阈值、幅度、窗口与置信度门槛均为 Proposed；RE 不产生平台副作用、不写 `review_result`、不绕过任何门禁；`NO_ACTION` 为合法一等公民输出且必须成包。
