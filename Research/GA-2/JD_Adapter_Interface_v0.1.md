# GA-2：京东广告 Agent 与平台接入层接口规范

**文档编号：** GA-2-IFACE-JD-001  
**任务编号：** GA2-T06  
**版本：** v0.1  
**状态：** Draft（历史，已被 `JD_Adapter_Interface_v0.2.md` 承接；勿作现行权威引用）  
**阶段：** GA-2 Engineering Design  
**输入基线：** `Research/GA-1/GA-1_Theory_v1.0.md`（GA-1.0 / v1.0，Confirmed）  
**关联架构：** `Architecture_Overview_v0.1.md`（GA-2-ARCH-001；历史，已被 v0.2 承接）  
**授权依据：** `GA-DEC-003`（Accepted，2026-09-11）  
**作者角色：** Research Engineer / MiMo Desktop（Local Research Operations Assistant）  
**约束：** 本文档仅为**抽象接口契约与字段映射设计**；**不对接真实京东/抖音官方 API**；**不含真实凭证、可执行广告操作脚本或账户配置**。与理论冲突时以理论基线为准并修订本文。

---

## 0. 安全边界与范围声明（强制阅读）

### 0.1 本轮明确不做

| 项 | 说明 |
|---|---|
| 真实 API 联调 | 不访问、不模拟调用京准通 / 京东宙斯 / 抖音巨量引擎等任何真实端点 |
| 凭证与密钥 | 不创建、不示例化、不落盘任何 AppKey / Token / Secret / Cookie |
| 可执行投放脚本 | 不编写可对真实广告账户执行调价、改预算、新建计划的脚本 |
| 端点与协议终局 | 不锁定真实 URL、签名算法、OAuth 流程、SDK 版本 |
| 账户结构映射终局 | 不声称已按某商户真实账户完成字段对齐 |
| 抖音侧详设 | 仅预留对称扩展点；抖音 Adapter 契约另文（后续任务） |

### 0.2 本轮明确要做

1. 定义 **JD Advertising Agent ↔ Platform Adapter ↔ Business Data Validation ↔ Business State Assembler** 的分层职责与调用边界。  
2. 定义**只读能力清单**与**写操作能力清单**（抽象动作 + 前置门禁）。  
3. 定义核心数据对象的**字段契约**（平台无关核心字段 + 平台可映射扩展字段）。  
4. 定义**经营数据真实性校验规则**在接口层的落点。  
5. 定义**种草计划 vs 收割计划**在接口能力、字段与门禁上的行为差异。  
6. 给出**理论追踪**与**待决问题**。

### 0.3 术语使用约定

- 「平台原始值」：Adapter 直接从平台侧读取、**未经校验**的数据。  
- 「可信经营值」：经 Business Data Validation 后、允许进入预测/推理链路的数据。  
- 「抽象动作」：接口契约中的语义动作（如 `AdjustBid`），**不等价于**某一具体平台 API 名称。  
- 术语表遵循 `Research/GA-1/Glossary.md`；本文不新增理论术语，仅新增工程接口 ID。

---

## 1. 分层职责与调用边界

对齐 `Architecture_Overview_v0.1.md` §3–4 与 L3/L4。

```text
┌─────────────────────────────────────────────────────────────┐
│  L2 能力引擎（Forecast / Reasoning / Risk / Trust / OFG…）   │
│  —— 只消费可信经营状态，只输出决策包，不直接触碰平台           │
└───────────────────────────▲─────────────────────────────────┘
                            │ BusinessState / DecisionPackage
┌───────────────────────────┴─────────────────────────────────┐
│  JD Advertising Agent（L3 场景执行）                          │
│  职责：计划类型语义、种草/收割行为模式、动作编排、三阶段记录触发 │
│  不做：真实 HTTP、凭证管理、原始字段清洗                        │
└───────────────────────────▲─────────────────────────────────┘
                            │ AbstractAction / ResourceQuery
┌───────────────────────────┴─────────────────────────────────┐
│  Business State Assembler（L4）                               │
│  职责：跨源组装经营状态；标注置信度；拒绝未校验指标进入决策视图   │
└───────────────────────────▲─────────────────────────────────┘
                            │ ValidatedMetric / TrustedOrderFact
┌───────────────────────────┴─────────────────────────────────┐
│  Business Data Validation（L4）                               │
│  职责：待付款/退款/跨计划归因/自然与推广耦合等校验；输出偏差标记  │
└───────────────────────────▲─────────────────────────────────┘
                            │ RawPlatformPayload（不可直信）
┌───────────────────────────┴─────────────────────────────────┐
│  Platform Adapter（L4）                                       │
│  职责：认证/限流/重试（设计位）、资源读取、动作提交、字段映射     │
│  能力：把平台方言翻成统一契约；把统一动作翻成平台方言             │
│  不做：经营语义判断、目标函数、风险裁决                          │
└───────────────────────────▲─────────────────────────────────┘
                            │ （本轮：Mock / Fixture only）
┌───────────────────────────┴─────────────────────────────────┐
│  平台侧（京东广告体系等）—— 本轮不接入真实系统                    │
└─────────────────────────────────────────────────────────────┘
```

### 1.1 JD Advertising Agent

| 项 | 约定 |
|---|---|
| 定位 | 京东场景经营动作的编排者与计划类型语义持有者 |
| 输入 | 上游：CBA 下发的已审批 Decision Package；侧向：State Assembler 的 BusinessState |
| 输出 | 抽象动作序列 → Platform Adapter；动作前后上下文 → Memory / Trace（经架构既定通道） |
| 计划类型语义 | 持有 `plan_mode ∈ {SEEDING, HARVEST, MIXED/UNKNOWN}`，驱动门禁与调用策略差异（见 §6） |
| 禁止 | 直接信任平台 GMV/ROI；绕过 Self-review/Risk/Trust；绕过 Adapter 发写操作 |

### 1.2 Platform Adapter

| 项 | 约定 |
|---|---|
| 定位 | 平台 I/O 边界；唯一允许“说平台方言”的组件 |
| 读路径 | `ResourceQuery` → 平台读接口（设计位）→ `RawPlatformPayload` + 元数据 |
| 写路径 | `AbstractAction` → 前置门禁校验（信任级、幂等、字段合法性）→ 平台写接口（设计位）→ `ActionReceipt` |
| 字段映射 | 维护 `FieldMappingTable`：统一契约字段 ↔ 平台侧字段名（本轮仅占位与规则，不填真实 API 字段） |
| 非职责 | 不做 ROI 是否达标、库存是否够、种草是否该提价等经营判断 |
| 本轮实现形态 | `JingzhuntongAdapter` 为接口占位类型；数据源为 Fixture/Mock；`LiveTransport` 默认禁用 |

### 1.3 Business Data Validation（BDV）

| 项 | 约定 |
|---|---|
| 定位 | 平台原始数据 → 可信经营事实的强制转换层 |
| 理论锚点 | GA-1 §6.3 / §8.1；GA-INNOV-003；「数据不可直信」 |
| 输入 | RawPlatformPayload、店铺订单事实（订单状态/退款）、自然流量侧读数（若有）、历史归因表 |
| 输出 | `ValidatedMetricSet`、`OrderFactAdjustment`、`ValidationReport`（含偏差原因码） |
| 硬规则 | **未通过或未标记校验的指标，不得进入 State Assembler 的 `trusted_*` 视图** |

### 1.4 Business State Assembler（STATE）

| 项 | 约定 |
|---|---|
| 定位 | 单次决策窗口的统一经营状态容器组装者 |
| 组装源 | BDV 通过的指标、计划/单元结构、库存与仓配、预算与余额、活动事件、审核合规、生命周期、类目竞争（可得则组装） |
| 输出 | `BusinessState`（带 `confidence` 与 `gap_flags`） |
| 硬规则 | 库存与预算为**决策变量输入**，不是附属展示字段；缺失时必须打 `gap_flag`，禁止静默当正常 |

### 1.5 层间调用方向（硬约束）

```text
允许：
  JDA → STATE/BDV/ADAPT（查询与动作下发）
  STATE → BDV → ADAPT（只读组装链）
  ADAPT → 平台（本轮仅 Mock）

禁止：
  L2 引擎 → ADAPT（绕过场景 Agent 与校验）
  ADAPT → 直接写 Memory/KE（绕过 Trace/ME 既定路径）
  任何组件 → 伪造 ValidationReport 为 PASS
```

---

## 2. 只读能力清单（抽象资源）

只读能力不改变平台状态；默认可在 Trust Level 0 使用。所有读接口统一返回：`fetched_at`、`source`、`raw_ref`（原始载荷引用）、`validation_state`（`UNVALIDATED` / `VALIDATING` / `VALIDATED` / `REJECTED`）。

### 2.1 资源总览

| 能力 ID | 抽象资源 | 说明 | 主要消费者 | 理论锚点 |
|---|---|---|---|---|
| RO-CAM-01 | Campaign / Plan 列表与状态 | 计划层级、启停、审核状态 | JDA, STATE | §7.3 |
| RO-CAM-02 | AdUnit / Creative 摘要 | 单元与素材存在性、审核 | JDA | §7.1 |
| RO-MET-01 | MetricSnapshot（日内） | 花费/展现/点击/加购/成交/ROI 等平台口径 | BDV→FE/RE | §6.2, §8.3 |
| RO-MET-02 | MetricSnapshot（日/多日） | 7/15/30 天序列 | FE, LE | §8.3 长周期 |
| RO-MET-03 | IntradayCurve | 分时花费/展现/点击/加购/成交曲线 | FE | §5.1（交接）/§8.3 |
| RO-ORD-01 | OrderFact（店铺侧） | 订单状态、实付、退款、是否推广归因标记 | BDV | §8.1 |
| RO-INV-01 | InventoryPosition | 可售/锁定/在途/入仓 lead time | STATE, RKE | §4.4（交接）/§6.3 |
| RO-BUD-01 | BudgetPosition | 计划日预算、已耗、剩余、账户余额 | STATE, FE | §5.3（交接）/§6.3 |
| RO-ACT-01 | BusinessEvent | 活动节奏、爆发窗口、促销价释放状态 | STATE, FE | §5.2（交接） |
| RO-CMP-01 | ComplianceStatus | 审核、违规、限流提示 | RKE, SRA | §6.3, §11.2 |
| RO-CAT-01 | CategoryCompetition（可选） | 类目竞价压力等（若平台可得） | FE（弱信号） | §6.3 |
| RO-ACC-01 | AccountQuota | 账户余额、信用/充值状态（抽象） | RKE | 预算连续性 |

> 说明：RO-ORD-01、RO-INV-01、RO-ACT-01 可能来自非广告域（订单/仓储/活动日历）。接口层将其建模为 **Adapter 可插拔 Provider**，而非假定广告 API 一次返回全部。

### 2.2 查询接口（抽象签名）

```text
ResourceQuery {
  query_id: string
  resource: enum {
    CAMPAIGN_LIST, PLAN_DETAIL, METRIC_SNAPSHOT,
    INTRADAY_CURVE, ORDER_FACTS, INVENTORY,
    BUDGET, BUSINESS_EVENT, COMPLIANCE, ACCOUNT
  }
  scope: {
    shop_id: ref
    campaign_ids?: ref[]
    plan_ids?: ref[]
    skus?: ref[]
    time_range: { start, end, granularity: MINUTE|HOUR|DAY }
  }
  fields?: string[]          // 字段子集，降低无效拉取
  dry_run: true              // 只读恒为 true
}

PlatformAdapter.read(query) -> {
  payload_ref: string
  raw: PlatformPayload | FixturePayload
  fetched_at: timestamp
  rate_limit_meta?: object
  warnings?: string[]
}
```

### 2.3 只读语义约束

1. **双时间尺度必备字段**：日内曲线与日级汇总必须能同时取到，否则 FE 无法完成预测驱动决策。  
2. **平台口径与店铺口径分离**：`MetricSnapshot.platform_gmv` 与 `OrderFact.shop_paid_gmv` 不得在 Adapter 层直接相减得出“真实 ROI”；差额由 BDV 计算并解释。  
3. **库存 lead time 必读**：入仓/补货提前期是库存决策变量的一部分，缺失则 `InventoryPosition` 不得标记为完整。  
4. **预算剩余与消耗速度**：为 Budget Lifetime Prediction 预留字段，不允许只给静态余额。  
5. **分页与限流**：Adapter 必须暴露分页游标与限流元数据；上层不得假设一次读全。

### 2.4 Mock 数据要求（本轮交付物语义）

Fixture 至少覆盖以下场景，供后续测试与 GA-3 预演（非真实数据）：

| Fixture ID | 场景 | 用途 |
|---|---|---|
| FX-01 | 种草计划：上午展现/点击同步下滑 | 预测驱动干预假设 |
| FX-02 | 收割计划：ROI 稳定但日波动 | 稳定性优先 / NO_ACTION |
| FX-03 | 高待付款比例导致平台 GMV 虚高 | BDV 待付款校验 |
| FX-04 | 退款回冲导致次日 ROI 跳变 | BDV 退款校验 |
| FX-05 | 同一订单跨两计划归因 | BDV 跨计划去重 |
| FX-06 | 自然成交与推广成交耦合 | BDV 耦合剥离 |
| FX-07 | 低库存 + 放量意向 | 库存作为决策变量 / Risk |
| FX-08 | 活动日上午平淡、晚间爆发 | Business Event Awareness |
| FX-09 | 预算上午过快消耗 | Budget Lifetime |
| FX-10 | 高客单长转化窗口 | 动态目标函数权重 |

---

## 3. 写操作能力清单（抽象动作）与前置门禁

### 3.1 原则

1. 写操作必须由 **已审批的 Decision Package** 驱动，禁止“读完直接写”。  
2. 门禁顺序（对齐 Architecture §7）：  
   `Reasoning 产出 → Risk Baseline → Trust Capability → Self-review → JDA 编排 → Adapter 提交`  
3. 「不调整」是合法结果（`NO_ACTION`），Adapter 不得为“有交互”而制造写操作。  
4. 所有写操作必须可审计：决策 ID、假设、预期响应窗口、执行回执、事后验证引用。

### 3.2 抽象动作目录

| 动作 ID | 抽象动作 | 语义 | 最低 Trust Level（Draft） | 计划类型敏感 | 主要风险 |
|---|---|---|---|---|---|
| WA-BID-01 | AdjustKeywordBid | 关键词出价调高/调低 | TL2 | 种草为主 | 破坏学习、成本飙升 |
| WA-BID-02 | AdjustBidStrategy | 出价策略/目标切换（抽象） | TL2–TL3 | 双方 | 系统托管被打断 |
| WA-PRM-01 | AdjustAudiencePremium | 人群溢价调整 | TL2 | 种草为主 | 获量质量漂移 |
| WA-PRM-02 | AdjustPlacementPremium | 资源位/触达范围溢价 | TL2 | 种草为主 | 无效展现 |
| WA-BGT-01 | AdjustDailyBudget | 日预算上调/下调 | TL3 | 双方 | 放量失败或断档 |
| WA-BGT-02 | ReallocateBudgetAcrossPlans | 跨计划预算再分配 | TL3 | 生命周期敏感 | 挤占收割稳定性 |
| WA-ROI-01 | AdjustTargetROI | 收割/托管目标 ROI | TL2–TL3 | 收割为主 | 目标过严导致失速 |
| WA-PLAN-01 | PausePlan | 暂停计划 | TL1–TL2 | 双方 | 打断长期稳定性 |
| WA-PLAN-02 | ResumePlan | 恢复计划 | TL2 | 双方 | 恢复节奏错误 |
| WA-PLAN-03 | CreatePlan | 新建计划（种草/收割） | TL4 | 高 | 试错成本、审核失败 |
| WA-PLAN-04 | ArchivePlan | 归档低效/失败计划 | TL2–TL3 | 双方 | 过早杀死可成长计划 |
| WA-CLS-01 | NoAction（显式决策） | 记录“维持现状”及理由 | TL0 | 双方 | 无平台副作用 |

> 上表为**语义动作**，不是平台 API 名。具体平台字段、参数域、回滚能力在联调阶段由 Adapter 映射表填充。

### 3.3 动作请求契约

```text
AbstractActionRequest {
  action_id: string
  action_type: WA-*
  decision_package_id: string      // 必须存在且已 APPROVE
  plan_mode: SEEDING | HARVEST | MIXED | UNKNOWN
  target: { campaign_id, plan_id?, unit_id?, keyword_id?, audience_id? }
  change: {
    // 按 action_type 选择；禁止全量字段乱传
    field: string
    from_value?: number|string|object
    to_value: number|string|object
    relative_pct?: number          // 相对幅度，便于风控
  }
  constraints: {
    max_absolute_delta?: number
    effective_window: { start, end }   // 期望生效窗口
    idempotency_key: string
    allow_partial: boolean
  }
  rationale_ref: string            // 指向 Observation/Hypothesis/Evidence
  expected_response_window?: { min_minutes, max_minutes, metric_hint }
  dry_run: boolean                 // 本轮所有真实路径必须 true；见 §7
}

PlatformAdapter.write(req) -> ActionReceipt {
  action_id
  status: ACCEPTED | REJECTED_BY_PLATFORM | REJECTED_BY_GATE | TIMEOUT | UNKNOWN
  platform_ack_ref?: string        // 本轮 Fixture 模拟
  applied_change?: object
  error?: { code, message, retryable }
  submitted_at, acknowledged_at?
}
```

### 3.4 前置门禁（Adapter 必须执行的“硬闸”）

即使上层已审批，Adapter 在提交前仍执行下列**不可绕过**检查：

| 门禁 ID | 检查项 | 失败结果 |
|---|---|---|
| G-01 | `decision_package_id` 有效且状态为 APPROVE | `REJECTED_BY_GATE` |
| G-02 | Trust Level ≥ 动作所需最低档 | `REJECTED_BY_GATE` |
| G-03 | Risk Baseline 允许该计划类型/幅度/频率 | `REJECTED_BY_GATE` |
| G-04 | 目标 plan 处于可写状态（非审核中/非冻结） | `REJECTED_BY_GATE` |
| G-05 | 幂等键未重复提交 | 去重返回原回执 |
| G-06 | 库存/预算类约束满足（见 §3.5） | `REJECTED_BY_GATE` 或降级为 REVISE |
| G-07 | `dry_run` 政策：本轮环境强制 dry_run=true | 任何非 dry_run 请求直接拒绝 |
| G-08 | 单日动作次数与最小间隔（Adjustment Response Window 约束） | `REJECTED_BY_GATE` |
| G-09 | 计划类型允许的动作白名单（见 §6） | `REJECTED_BY_GATE` |

### 3.5 库存与预算相关写门禁（决策变量）

理论要求：库存是广告决策变量；预算有生命周期。

| 规则 | 条件 | 接口行为 |
|---|---|---|
| INV-GATE-1 | 可售库存低于安全阈值 或 入仓 lead time 不覆盖预测放量窗口 | 拒绝 `CreatePlan` 放量配置、拒绝大幅 `AdjustDailyBudget` 上调 |
| INV-GATE-2 | 清仓生命周期且库存积压 | 允许收割向动作；限制纯种草扩量（由 JDA 策略层给出建议，RKE 终裁） |
| BUD-GATE-1 | 预测预算将在关键爆发窗口前耗尽 | 允许/建议 `AdjustDailyBudget` 上调；禁止无理由下调 |
| BUD-GATE-2 | 账户余额不足风险 | 写动作降级为 HOLD，并通知人工充值路径（接口只发事件，不自动充值） |
| BUD-GATE-3 | 探索预算池已耗尽 | 拒绝 `CreatePlan` 等探索型动作 |

### 3.6 写后必做（接口层义务）

1. 返回 `ActionReceipt` 后，JDA 必须触发**三阶段推理闭环**的“调整中”记录。  
2. 按 `expected_response_window` 注册验证任务：到期拉取 RO-MET-01/03，供 Reflection 校准 Adjustment Response Window。  
3. 失败回执进入 Failure Pattern 候选，**不得静默丢弃**。

---

## 4. 核心数据对象字段契约

> 字段为工程契约草案；命名采用稳定英文标识，中文作说明。`*` 表示必填。类型为逻辑类型。

### 4.1 Campaign / Plan

```text
Campaign {
  campaign_id*            : string      // 统一内部 ID
  platform_campaign_ref   : string      // 平台侧引用（映射表填）
  shop_id*                : string
  name                    : string
  status*                 : enum { ACTIVE, PAUSED, ENDED, ARCHIVED, UNDER_REVIEW }
  plan_mode*              : enum { SEEDING, HARVEST, MIXED, UNKNOWN }
  objective_hint          : enum { REACH, CLICK, CART, CONVERSION, ROI_STABILITY }
  product_refs*           : string[]    // SKU/商品
  lifecycle_stage         : enum { LAUNCH, GROWTH, MATURE, PROMO, CLEARANCE, UNKNOWN }
  budget_id               : ref
  created_at*, updated_at*
  trust_relevant_flags    : object      // 如 system_managed: bool
  raw_meta_ref            : string      // 平台原始字段包引用
}

Plan / AdUnit（若平台区分） {
  plan_id*, campaign_id*
  plan_type_detail        : enum { KEYWORD, CROWD, SYSTEM_MANAGED, CONTENT_BOOST, OTHER }
  targeting_summary       : object
  bid_config_ref          : ref
  status*, audit_status   : enum { PASS, FAIL, PENDING }
  plan_mode_inherited     : bool        // 是否继承 campaign.plan_mode
}
```

**契约要点**

- `plan_mode` 必填：接口层用它选择门禁与动作白名单；无法判定时为 `UNKNOWN`，并默认更严风控。  
- `system_managed: true` 表示托管型收割计划：限制细粒度关键词写操作（见 §6）。  
- `lifecycle_stage` 来自 STATE/策略层注入，Adapter 可只透传；缺失时标 `UNKNOWN`。

### 4.2 MetricSnapshot（平台口径，未校验）

```text
MetricSnapshot {
  snapshot_id*
  scope*                  : { campaign_id?, plan_id?, unit_id?, sku? }
  window*                 : { start*, end*, granularity* }
  platform_metrics*       : {
    cost                  : money
    impressions           : int
    clicks                : int
    carts                 : int
    platform_orders       : int
    platform_gmv          : money     // 平台推广口径成交额，不可直信
    platform_roi          : ratio     // 平台自算，不可直信
    cpc?, ctr?, cvr?      : ratio     // 平台自算派生
  }
  attribution_hint        : object    // 平台归因窗口/口径描述（抽象）
  fetched_at*
  validation_state*       : enum { UNVALIDATED, VALIDATING, VALIDATED, REJECTED }
  raw_ref*                : string
}
```

### 4.3 ValidatedMetricSet（BDV 输出，可进入决策）

```text
ValidatedMetricSet {
  validated_id*
  based_on_snapshots*     : string[]
  order_fact_ref*         : ref
  trusted_metrics*        : {
    spend                 : money     // 通常与平台花费一致或已知调整
    clicks, impressions, carts
    paid_orders           : int       // 已支付且未全额退款等（按校验规则）
    trusted_gmv           : money     // 去重、去待付款、回冲退款后
    trusted_roi           : ratio
    organic_overlap_ratio : ratio     // 自然与推广耦合估计
    cross_plan_dup_ratio  : ratio     // 跨计划重复归因估计
  }
  adjustments*            : OrderFactAdjustment[]
  confidence*             : enum { HIGH, MEDIUM, LOW }
  validation_report_ref*  : ref
  validated_at*
}
```

### 4.4 OrderFactAdjustment

```text
OrderFactAdjustment {
  order_ref
  reason_codes*           : enum[] {
    PENDING_PAYMENT,
    REFUNDED_FULL, REFUNDED_PARTIAL,
    CROSS_PLAN_DUPLICATE,
    ATTRIBUTION_WINDOW_EXPIRED,
    ORGANIC_COUPLED,
    ANOMALY_ORDER,          // 大额/异常，进入遗忘候选
    PLATFORM_LAG            // 数据延迟
  }
  platform_counted_gmv    : money
  trusted_counted_gmv     : money
  notes                   : string
}
```

### 4.5 InventoryPosition（决策变量）

```text
InventoryPosition {
  sku*
  available_qty*
  locked_qty, in_transit_qty
  warehouse_type          : enum { JD_WAREHOUSE, MERCHANT_WAREHOUSE, MIXED, UNKNOWN }
  replenishment_lead_time_days*
  safety_stock_threshold*
  estimated_days_of_cover : ratio     // 可售 / 预测日耗
  stock_risk_level*       : enum { OK, TIGHT, CRITICAL, OVERSTOCK }
  as_of*
  source_ref*
}
```

**契约要点：** `estimated_days_of_cover` 与 `stock_risk_level` 必须能被 RKE 与写门禁直接消费；广告放量动作不得无视 `TIGHT/CRITICAL`。

### 4.6 BudgetPosition

```text
BudgetPosition {
  budget_id*
  level                   : enum { ACCOUNT, CAMPAIGN, PLAN }
  daily_budget            : money
  spent_today             : money
  remaining_today         : money
  burn_rate_per_hour      : money      // 滚动估计
  projected_exhaust_at    : timestamp? // Budget Lifetime 预测输入/输出锚点
  account_balance         : money
  exploration_pool_left   : money      // 探索预算池（新建计划用）
  as_of*
}
```

### 4.7 BusinessEvent（活动感知）

```text
BusinessEvent {
  event_id*
  type                    : enum { PROMO_DAY, PAYDAY, PLATFORM_CAMPAIGN, INTERNAL_CLEARANCE }
  phase                   : enum { PRE, LIVE, PEAK_WINDOW, POST }
  expected_peak_window    : { start, end }
  price_release_state     : enum { NOT_RELEASED, PARTIAL, FULL }
  recommended_roi_posture : enum { HOLD, RELAX_TARGET, RAISE_ACQUIRE }
  source_ref*
}
```

> `recommended_roi_posture` 仅为**感知提示**，最终由 OFG/Risk/Reasoning 裁决；Adapter 不得自动改 ROI。

### 4.8 DecisionPackage（写操作前置对象）

```text
DecisionPackage {
  decision_id*
  status*                 : enum { DRAFT, PENDING_REVIEW, APPROVE, REVISE, HOLD, REJECT, ESCALATE_HUMAN }
  plan_mode*, plan_id*
  objective_weights_ref   : ref        // OFG 动态目标函数快照
  observations*, hypothesis*, evidence_refs*
  proposed_actions*       : AbstractActionRequest[]
  expected_response_window
  risk_level*, trust_level_required*
  self_review_result_ref*
  approved_by             : enum { AGENT, HUMAN }
  created_at*, decided_at*
}
```

### 4.9 ActionReceipt

见 §3.3。补充审计字段：

```text
ActionReceipt.audit {
  decision_id*, causal_memory_pending: bool
  response_window_due_at?: timestamp
  failure_pattern_candidate?: bool
}
```

### 4.10 ValidationReport

```text
ValidationReport {
  report_id*
  scope*, window*
  checks*                 : [{
    check_id, status: PASS|FAIL|WARN|SKIPPED
    detail, reason_codes[]
  }]
  overall                 : enum { PASS, PASS_WITH_WARNINGS, FAIL }
  blocking_for_decision   : bool       // FAIL 时必须 true，阻止 trusted 视图
}
```

### 4.11 BusinessState（Assembler 输出）

```text
BusinessState {
  state_id*, as_of*
  shop_id*
  plans[]                 : Campaign/Plan 摘要
  trusted_metrics_by_plan : map<plan_id, ValidatedMetricSet>
  inventory_by_sku        : map<sku, InventoryPosition>
  budget                  : BudgetPosition
  active_events[]         : BusinessEvent[]
  compliance              : ComplianceStatus
  gap_flags*              : enum[] {
    MISSING_INVENTORY, MISSING_ORDER_FACTS, MISSING_BUDGET_BURN,
    MISSING_INTRADAY_CURVE, MISSING_EVENT_CALENDAR,
    LOW_VALIDATION_CONFIDENCE, UNKNOWN_PLAN_MODE
  }
  confidence*             : enum { HIGH, MEDIUM, LOW }
  ready_for_forecast      : bool       // gap 未清除时可为 false
}
```

---

## 5. 数据校验规则（BDV 规范）

理论锚点：GA-1 §6.3、§8.1；交接文档 §4.1。核心原则：**平台数据不可直信**。

### 5.1 校验流水线

```text
Raw MetricSnapshot
  → V1 结构/延迟校验
  → V2 订单状态校验（待付款/取消）
  → V3 退款回冲
  → V4 跨计划归因去重
  → V5 自然与推广耦合估计
  → V6 异常订单标记（不删除，降权）
  → ValidatedMetricSet + ValidationReport
  →（仅 overall≠FAIL 时）进入 trusted 视图
```

### 5.2 规则明细

| 规则 ID | 名称 | 检测逻辑（抽象） | 输出影响 | 失败策略 |
|---|---|---|---|---|
| V-PAY-01 | 待付款计入 | 平台归因订单中状态=待支付/未支付 | `platform_gmv` 下调为 `trusted_gmv`；reason=`PENDING_PAYMENT` | 不阻断；置信度降为 MEDIUM |
| V-PAY-02 | 取消/超时关闭 | 终态非成交 | 同上，单独 reason | 同上 |
| V-REF-01 | 全额退款 | 退款完成 | `trusted_gmv -= refund`；`REFUNDED_FULL` | 同上 |
| V-REF-02 | 部分退款/售后中 | 退款比例或售后未终态 | 按可配置保守/激进策略扣减；标注 | 策略需配置；默认保守 |
| V-REF-03 | 退款滞后 | T+1~T+n 回冲 | 允许次日重算；禁止把滞后当“新异常” | 需序列重算窗口 |
| V-ATTR-01 | 跨计划重复归因 | 同一 order_ref 出现在多 plan | 仅保留主归因或按规则分摊；`CROSS_PLAN_DUPLICATE` | 若重复率>阈值→WARN/FAIL |
| V-ATTR-02 | 归因窗口 | 超出平台归因窗的成交 | 不计入该计划 trusted_gmv | WARN |
| V-ORG-01 | 自然与推广耦合 | 对照店铺自然流量/品类基线 | 输出 `organic_overlap_ratio`；禁止把全部增量记为推广功劳 | 需外部对照；缺失→gap_flag |
| V-ORG-02 | 增量 vs 搬移 | 推广花费上升但店铺总 GMV 未升 | 标记 “预算搬移/内部竞争” 候选 | WARN，进入 Learning |
| V-NOI-01 | 异常大额订单 | 金额/件数超历史分位 | 不删除；`ANOMALY_ORDER`；进入经验遗忘候选 | 置信度提示 |
| V-LAG-01 | 数据延迟 | 平台回传滞后于 wall clock | `PLATFORM_LAG`；禁止在滞后窗内做激进写决策 | 可阻断写 |

### 5.3 与决策的耦合规则

1. `confidence=LOW` 或 `blocking_for_decision=true` 时：Reasoning 最多输出 `HOLD`/`ESCALATE_HUMAN`，不得输出写计划动作。  
2. FE 输入必须引用 `ValidatedMetricSet.validated_id`，禁止引用未校验 `MetricSnapshot`。  
3. Reflection 评估“调整是否有效”时，必须使用校验后指标，否则经验会被污染。  
4. 校验规则自身进入 Learning：若某 reason_code 系统性误判，升级为规则修订候选（经 Knowledge 治理），**不得由 Adapter 静默改数**。

### 5.4 BDV 接口签名

```text
BusinessDataValidation.validate({
  metric_snapshots: ref[],
  order_facts: ref[],
  organic_baseline?: ref,
  policy: { refund_mode: CONSERVATIVE|AGGRESSIVE, dup_split: PRIMARY|PRO_RATA }
}) -> {
  validated_metrics: ValidatedMetricSet[]
  report: ValidationReport
}
```

---

## 6. 种草计划 vs 收割计划在接口层的差异

理论锚点：GA-1 §7.2–7.3、§8.2、§8.5；交接 §4.3。接口层必须**编码**这些差异，而不是留给调用方自觉。

### 6.1 能力矩阵

| 维度 | 种草 SEEDING | 收割 HARVEST |
|---|---|---|
| 主目标指标（OFG 输出提示） | 展现/点击/加购/触达 | 成交 ROI/转化/稳定性 |
| 写动作白名单 | WA-BID-01/02, WA-PRM-01/02, WA-BGT-01, WA-PLAN-01/02/03 | WA-BGT-01, WA-ROI-01, WA-PLAN-01/02/04；细粒度关键词动作受限 |
| 托管计划 | 较少 | 常见；`system_managed=true` 时禁止关键词级写 |
| 调整频率门禁 G-08 | 允许较高频（仍受 Response Window 约束） | 低频；更长最小间隔 |
| 单次幅度门禁 G-03 | 可相对宽松（小步快调） | 更严（防破坏系统学习） |
| 稳定性优先 | 一般不默认启用 | 默认启用；`NO_ACTION` 优先权重更高 |
| 日内曲线依赖 | 强（上午下滑可触发干预） | 中（更重 7/15/30 天） |
| 库存门禁 | 放量前必须检查 | 清仓期可配合提高收割 |
| 预算生命周期 | 关注获量连续性 | 关注关键成交窗口连续性 |
| 失败处理 | 新建失败可进 Failure Pattern，允许再探索 | 暂停/归档需更长观察窗 |

### 6.2 接口层编码方式

1. **Plan.mode 必填**（§4.1）；`UNKNOWN` 时 Adapter 使用 `HARVEST` 更严门禁兜底。  
2. **G-09 动作白名单**按 `plan_mode` 过滤；白名单外返回 `REJECTED_BY_GATE` + 原因码 `ACTION_NOT_ALLOWED_FOR_PLAN_MODE`。  
3. **DecisionPackage.objective_weights_ref** 由 OFG 生成；Adapter 不解释权重，但 Self-review 必须校验权重与 plan_mode 一致（防种草计划套收割 ROI 权重却做种草动作的语义冲突）。  
4. **Adjustment Response Window 默认值**可不同（种草短、收割长）；实际值由 Learning 回写，接口只读取。  
5. **CreatePlan** 必须携带 `plan_mode` 与生命周期；否则门禁拒绝。

### 6.3 动态目标函数在接口中的位置

- 接口**不实现**目标函数算法。  
- 接口**必须透传** `objective_weights` 快照，并在审计中可追溯。  
- 低客单 vs 中高客单权重差异由 OFG 负责；接口保证状态字段（价格带、生命周期、计划类型、库存、活动）足够组装权重。

---

## 7. 安全边界与运行策略（本轮）

### 7.1 环境策略

```text
AdapterRuntime.mode ∈ {
  FIXTURE_ONLY,      // 默认：只读写本地 Fixture
  SIMULATION,        // 可选：本地状态机模拟写回执
  SANDBOX_LIVE,      // 预留：平台沙箱（需单独授权，本轮禁止）
  LIVE               // 预留：生产（需单独授权+人工，本轮禁止）
}
```

本轮要求：

| 控制项 | 本轮取值 |
|---|---|
| Runtime mode | `FIXTURE_ONLY` 或 `SIMULATION` |
| LiveTransport | 未装配 / 硬失败 |
| 凭证源 | 不存在；`CredentialProvider` 接口可声明但实现为空对象并拒绝提供密钥 |
| dry_run 政策 | 所有 `write` 请求必须 `dry_run=true`（G-07） |
| 网络出口 | 设计评审前不允许配置真实域名白名单 |
| 日志 | 不得打印任何形式的密钥、完整账户标识、买家隐私 |

### 7.2 接口层“禁止发明能力”清单

1. 不得把 Fixture 回执表述为“平台已执行”。  
2. 不得在文档/代码中暗示已打通京准通或巨量引擎。  
3. 不得提供“一键投放”示例脚本。  
4. 不得在校验失败时伪造 `PASS`。  
5. 不得让 L2 引擎直接持有 Adapter 写句柄。

### 7.3 授权升级路径（供后续决策，非本轮执行）

```text
GA-2 设计评审通过
  → 单独 GA-DEC：是否进入 SANDBOX_LIVE
  → 凭证与合规评审（人工）
  → 只读沙箱联调
  → 写操作沙箱 + 更严 Trust
  → 生产（仍保留人工否决）
```

---

## 8. 理论追踪

| 理论主张 | 章节/创新点 | 本文落点 |
|---|---|---|
| 平台数据不可直信 | §6.3, §8.1, GA-INNOV-003 | §1.3–1.4, §2.3, §5 全文 |
| 预测驱动决策 / 双时间尺度 | §6.2, §8.3 | §2.1 RO-MET-02/03, §2.3, §4.2 |
| 预算生命周期 | 交接 §5.3 | §4.6 projected_exhaust_at, §3.5 BUD-GATE |
| 活动事件感知 | 交接 §5.2 | §4.7 BusinessEvent |
| 库存是决策变量 | 交接 §4.4, §6.3 | §4.5, §3.5 INV-GATE |
| 动态目标函数 | §7.2, §8.2 | §4.8 objective_weights_ref, §6.3 |
| 种草 vs 收割行为模式 | §7.3, 交接 §4.3 | §6 能力矩阵与 G-09 |
| 稳定性优先 / NO_ACTION | §8.5 | §3.1, §6.1, WA-CLS-01 |
| 调整响应窗口 | §8.6 | §3.3 expected_response_window, §3.6, §6.2 |
| 风险受控自治 / Trust 分级 | §6.7, §11, Arch §7 | §3.2 Trust Level, §3.4 门禁 |
| Self-review 前置 | §11.2 | §3.1 门禁顺序, DecisionPackage |
| 失败即学习事件 | §9.4 / 交接 §6.1 | §3.6 失败回执进 Failure Pattern |
| 三阶段推理闭环 | §9.2 / 交接 §6.2 | §3.6, DecisionPackage 字段 |
| 平台隔离（场景≠理论边界） | §4 | §1 分层、Adapter 可替换 |

追踪矩阵对齐：`Theory_Engineering_Trace.md` 中 BDV/STATE/ADAPT/JDA 与 GA2-T06「平台接口规范：先只读，后写操作」。

---

## 9. 待决问题

| ID | 问题 | 建议 | 阻塞联调？ |
|---|---|---|---|
| JD-Q1 | `plan_mode` 由人工标注、平台字段推断，还是策略层反推？ | 混合：平台字段+人工覆盖+UNKNOWN 兜底 | 是（语义） |
| JD-Q2 | 跨计划归因采用主计划归因还是按触点分摊？ | 先 PRIMARY，策略可配置；Learning 评估 | 否（可后置） |
| JD-Q3 | 自然/推广耦合是否必须有店铺自然流量数据源？ | 是；无源则 gap_flag，不得伪精确 | 部分 |
| JD-Q4 | 退款“保守/激进”默认策略如何按品类/客单切换？ | 交 GA2-T07 参数预标定 | 否 |
| JD-Q5 | 托管收割计划是否允许任何关键词级写？ | 默认否；仅预算/目标 ROI/启停 | 否 |
| JD-Q6 | Adapter 写门禁与 Risk Engine 规则由谁权威执行？ | Risk 定策略，Adapter 执行不可绕过子集（G-01..G-09） | 是（权责） |
| JD-Q7 | 库存数据源是广告域外 Provider，接入优先级？ | 先 Merchant/JD WMS 抽象 Provider，Fixture 仿真 | 是（数据源） |
| JD-Q8 | 日内分钟级曲线的采样与存储成本 | HOUR 默认，关键日 MINUTE；属 T04/T07 | 否 |
| JD-Q9 | 抖音 Adapter 是否复用同一 `AbstractAction` 枚举？ | 尽量复用；平台特有动作进 extension 字段 | 否 |
| JD-Q10 | ActionReceipt 在 SIMULATION 下如何避免污染 Memory？ | `source=SIMULATION` 标记，Learning 默认降权或隔离池 | 是（学习污染） |

---

## 10. 与后续任务的接口

| 下游任务 | 本文供给 |
|---|---|
| GA2-T04 Memory/Knowledge 数据边界 | DecisionPackage、ActionReceipt.audit、三阶段必填字段 |
| GA2-T05 Risk+Trust+Self-review | 门禁 G-01..G-09、Trust Level 映射、DecisionPackage.status |
| GA2-T07 参数预标定与默认模板 | plan_mode 差异、幅度/频率门禁占位、退款策略开关、Fixture 场景清单 |
| GA-3 验证 | 校验前后 GMV/ROI 偏差、响应窗口命中率、种草/收割成功率可测指标定义入口 |

---

## 11. 变更记录

| 日期 | 版本 | 变更 | 依据 |
|---|---|---|---|
| 2026-09-11 | v0.1 | 首次建立京东接入层抽象接口契约：分层、只读/写能力、数据对象、BDV 规则、种草/收割差异、安全边界、理论追踪 | GA2-T06；GA-1 Theory v1.0；Architecture_Overview_v0.1；GA-DEC-003 |

---

**Document Status:** Draft  
**Next Review:** 项目负责人 / Research Architect  
**Explicit Non-claim:** 本文档不代表已对接京东或抖音官方 API；所有平台侧引用均为设计占位。
