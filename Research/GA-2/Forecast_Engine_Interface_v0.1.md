# GA-2：Forecast Engine 接口与预测对象清单

**文档编号：** GA-2-FE-001  
**任务编号：** GA2-T13  
**版本：** v0.1  
**状态：** Draft  
**阶段：** GA-2 Engineering Design  
**输入基线：** `Research/GA-1/GA-1_Theory_v1.0.md`（GA-1.0 / v1.0，Confirmed）  
**主线架构：** `Research/GA-2/Architecture_Overview_v0.2.md`（Confirmed，GA-DEC-004）  
**关联详设：**  
- `Decision_Packet_Schema_v0.1.md`（`forecast_ref` 字段与 DPK-I3）  
- `Shadow_Mode_Design_v0.1.md`（L2 预测对照评估、SM-M03/M04）  
- `JD_Adapter_Interface_v0.2.md`（`BusinessState` / `ValidatedMetricSet` / `BudgetPosition` / `BusinessEvent`）  
- `Parameter_Genome_Templates_v0.1.md`（期望窗口与调参频率先验）  
- `Memory_Knowledge_Boundary_v0.1.md`（IF-ME-03：FE 可读 WorkingContext）  

**授权依据：** `GA-DEC-004`（主线冻结 + 启动 GA2-T13）  
**作者角色：** Research Engineer 子代理  
**约束：** 仅接口契约与对象设计；不接真实 API；不实现模型代码；所有精度阈值与窗口默认值一律 **Proposed**。

---

## 0. 范围声明

### 0.1 本轮要做

1. 定义 Forecast Engine（FE）在四回路中的位置、职责边界与输入/输出契约。  
2. 建立预测对象目录（Catalog）：日内指标曲线、预算寿命、计划稳定性、活动爆发概率、库存风险。  
3. 为每个预测对象规定：对象 ID、粒度、horizon、输入特征、输出结构、置信度字段、更新频率（Proposed）。  
4. 定义 FE 与 Business State Assembler（STATE）的输入契约。  
5. 定义 FE 与 Reasoning Engine（RE）/ Decision Packet 的 `forecast_ref` 结构。  
6. 定义 Shadow 模式下预测回看评估的记录格式。  
7. 定义失败 / 低置信度时的降级行为。  
8. 给出理论追踪与待决问题。

### 0.2 本轮明确不做

- 真实平台数据拉取、模型训练、在线推理服务实现；  
- 存储引擎与消息队列选型；  
- 修改 `GA-1_Theory_v1.0.md` / `PROJECT_SPEC.md` / `Architecture_Overview_v0.2.md`；  
- 抖音侧预测对象扩展（占位后置）。

### 0.3 术语约定

| 术语 | 含义 |
|---|---|
| **ForecastBundle** | 一次 FE 调用产出的全部预测对象集合 |
| **ForecastObject** | Bundle 内单个可独立引用的预测产物（如一条 ROI 曲线、一个 ETA） |
| **预测对象 ID** | 本文定义的稳定对象编码（如 `FC-CURVE-SPEND`） |
| **Proposed** | 工程草案值，须经历史标定与 GA-3 验证后方可升格 |

---

## 1. Forecast Engine 定位

### 1.1 一句话

> **FE 是经营状态到未来状态的映射器：只消费 Trusted State 与历史序列，产出结构化预测对象与置信度，不拍板动作。**

### 1.2 在架构中的位置

对齐 `Architecture_Overview_v0.2.md` §5 组件边界表：

| 输入 | 输出 | 不做什么 |
|---|---|---|
| Trusted State（STATE）、历史序列、事件（BusinessEvent）、WorkingContext（ME） | 走势 / 预算寿命 / 稳定性 / 爆发概率 / 库存风险 | 最终拍板；生成动作；绕过 BDV 用 Raw 数据 |

### 1.3 在四条主回路中的位置

```text
回路 A（日内/单计划）—— FE 是核心前置节点：

  Adapter(RO) → BDV → STATE → FE → RE → Risk/Trust/SRA → Domain Agent → Execute → Audit
                                ▲
                                │  消费 TrustedBusinessState + ValidatedMetricSet
                                │  产出 ForecastBundle
                                ▼
                          forecast_ref 写入 Decision Packet

回路 B（经验蒸馏）：FE 不直接写 Memory；但预测误差作为 RFE 的评估输入，
  通过 Shadow 评估报告 / 预测回看记录间接进入学习链。

回路 C（知识演化）：FE 可消费 KE 提供的历史稳定性知识与参数基因先验；
  预测精度趋势可作为 Genome 质量分的参考信号（后置）。

回路 D（信任与自治）：FE 预测置信度是 SRA 谓词 CHK_CONF 的输入之一；
  长期预测准确率可进入 Trust 评估材料（间接，非直接计分）。
```

### 1.4 设计原则（自理论派生）

| ID | 原则 | 理论锚点 | 工程含义 |
|---|---|---|---|
| FE-P1 | 预测先于动作 | GA-1 §6.2；架构 P2 | Forecast 输出是 Reasoning 的一等公民输入，不是可选装饰 |
| FE-P2 | 只信校验后数据 | GA-1 §6.3；架构 P3；DPK-I3 | FE 输入必须引用 `validated_id`，禁止引用 Raw MetricSnapshot |
| FE-P3 | 置信度必填 | GA-1 §8.4 | 每个预测对象必须携带置信度；低于阈值须触发降级而非静默 |
| FE-P4 | 双时间尺度 | GA-1 §8.3 | 同时支持日内 horizon（1h–to_day_end）与长周期 horizon（7d–30d） |
| FE-P5 | 稳定性可量化 | GA-1 §8.5 | 稳定性本身是预测对象，不是主观标签 |
| FE-P6 | 活动事件可感知 | GA-1 §6.2 预测对象；Trace §5.2 | 活动爆发概率是独立预测对象，不是隐含在曲线里 |
| FE-P7 | 失败可解释 | 架构 P6 | 低置信度 / 缺数据时显式输出降级信号，不伪精确 |
| FE-P8 | 不拍板 | 架构 §5 | FE 不输出动作建议；只输出预测与置信度 |

---

## 2. 输入契约（与 Business State Assembler）

### 2.1 输入总览

FE 的唯一状态输入源是 STATE 组装的 `TrustedBusinessState`。FE 不直接调用 Adapter。

```text
ForecastRequest {
  request_id*         : string          // 前缀 FC-REQ-
  triggered_by*       : enum {
    CBA_DECISION_LOOP,    // 回路 A 常规触发
    RE_FOLLOWUP,          // RE 请求补充预测
    PERIODIC_REFRESH,     // 周期刷新
    SHADOW_EVAL           // 影子评估回看
  }
  state_ref*          : ref             // TrustedBusinessState.state_id
  scope*              : {
    shop_id*          : ref
    plan_ids?         : ref[]
    campaign_ids?     : ref[]
    skus?             : ref[]
  }
  forecast_targets*   : enum[]          // 请求哪些预测对象，见 §3 目录
  horizons*           : string[]        // 请求的 horizon 集合，如 ["2h","to_day_end","7d"]
  as_of*              : timestamp
  runtime_envelope    : RuntimeEnvelope // 透传 Shadow/Live 标签（GA2-T11 §3.4）
}
```

### 2.2 STATE 提供的字段（FE 消费清单）

对齐 `JD_Adapter_Interface_v0.1.md`（历史，已被 v0.2 承接）§4.11 `BusinessState`：

| BusinessState 字段 | FE 用途 | 缺失时行为 |
|---|---|---|
| `trusted_metrics_by_plan` | 所有曲线类预测的主数据源 | 该 plan 不产出曲线；`gap_flag` 显式 |
| `budget`（BudgetPosition） | 预算寿命预测主输入 | 不产出 `FC-ETA-BUDGET`；`gap_flag=MISSING_BUDGET_BURN` |
| `inventory_by_sku` | 库存风险预测主输入 | 不产出 `FC-RISK-INVENTORY`；`gap_flag=MISSING_INVENTORY` |
| `active_events[]`（BusinessEvent） | 活动爆发概率主输入 | 爆发概率退化为"无活动基线"模式 |
| `confidence` | FE 整体置信度上限约束 | `LOW` 时 FE 可拒绝产出写动作相关预测 |
| `ready_for_forecast` | FE 前置门禁 | `false` 时 FE 返回 `FE_STATUS_BLOCKED` |
| `gap_flags[]` | FE 降级信号 | 透传到 ForecastBundle |
| `as_of` / `state_id` | 预测时间锚点与可追溯性 | 必填，缺失则请求非法 |

### 2.3 STATE 必须提供的历史序列

除当前快照外，FE 需要 STATE 或 ME 提供以下历史序列（经 BDV 校验）：

| 序列类型 | 最小长度 | 粒度 | 来源 | 说明 |
|---|---|---|---|---|
| 日内分时曲线 | 当日已过时段 | 小时（Proposed） | RO-MET-03 → BDV | 日内走势预测主输入 |
| 近 7 日日级序列 | ≥5 有效日（Proposed） | 日 | RO-MET-02 → BDV | 基线带与趋势 |
| 近 14–30 日日级序列 | ≥10 有效日（Proposed） | 日 | RO-MET-02 → BDV | 稳定性与长周期 |
| 预算消耗序列 | 当日 + 近 3 日 | 小时/日 | RO-BUD-01 | 燃烧率估计 |
| 活动日历 | 当前 + 未来 7 日 | 事件级 | RO-ACT-01 | 爆发概率 |
| 库存快照 + 历史日耗 | 当前 + 近 7 日日耗 | 日 | RO-INV-01 | 库存风险 |

> **硬约束：** 序列必须携带 `validated_id` 或等价校验标记。未经 BDV 的序列不得进入 FE（对齐 JD §5.3 第 2 条）。

### 2.4 FE 前置门禁

```text
FE.precheck(request, state) -> {
  status: READY | DEGRADED | BLOCKED
  blocking_gaps: string[]
  degraded_targets: enum[]     // 哪些预测对象降级或跳过
  max_allowed_confidence: [0,1] // 由 state.confidence 映射
}
```

| 条件 | status | 行为 |
|---|---|---|
| `ready_for_forecast=false` | BLOCKED | 返回 FE_STATUS_BLOCKED；不产出任何预测对象 |
| `confidence=LOW` | DEGRADED | 产出预测但 `max_allowed_confidence ≤ 0.5`（Proposed） |
| 关键序列缺失（如无日内曲线） | DEGRADED | 跳过对应预测对象，`degraded_targets` 显式列出 |
| `validation_confidence=LOW` | DEGRADED | 曲线类预测标记 `confidence_capped=true` |

---

## 3. 预测对象目录（Catalog）

### 3.1 目录总览

| 对象 ID | 名称 | 类别 | 理论锚点 | 必选 |
|---|---|---|---|---|
| `FC-CURVE-SPEND` | 花费走势曲线 | 日内/长周期 | §6.2 预测对象；§8.3 | Y |
| `FC-CURVE-IMPRESSION` | 展现走势曲线 | 日内/长周期 | §6.2；§8.3 | Y |
| `FC-CURVE-CLICK` | 点击走势曲线 | 日内/长周期 | §6.2；§8.3 | Y |
| `FC-CURVE-ADD_CART` | 加购走势曲线 | 日内/长周期 | §6.2 加购数；§8.3 | Y |
| `FC-CURVE-GMV` | 成交额走势曲线 | 日内/长周期 | §6.2 GMV；§8.3 | Y |
| `FC-CURVE-ROI` | ROI 走势曲线 | 日内/长周期 | §6.2 ROI；§8.3 | Y |
| `FC-ETA-BUDGET` | 预算耗尽时间 | 日内 | §6.2 预算耗尽时间；Trace §5.3 | Y |
| `FC-STAB-PLAN` | 计划稳定性评估 | 长周期 | §6.2 计划稳定性；§8.5 | Y |
| `FC-BURST-CAMPAIGN` | 活动爆发概率 | 日内+事件 | §6.2 活动爆发周期；Trace §5.2 | Y |
| `FC-RISK-INVENTORY` | 库存风险投影 | 日内/短周期 | §6.2 商品库存；§6.3 | 条件（有库存源） |
| `FC-SUM-BUNDLE` | Bundle 摘要与综合置信度 | 元对象 | 架构 §6 forecast_ref.summary | Y（自动合成） |

> **说明：** `FC-SUM-BUNDLE` 不是独立预测模型，而是 FE 将各对象摘要聚合后写入 Decision Packet `forecast_ref.summary` 的合成产物。

---

### 3.2 对象详设

#### FC-CURVE-SPEND：花费走势曲线

| 属性 | 值 |
|---|---|
| **对象 ID** | `FC-CURVE-SPEND` |
| **粒度** | plan / campaign / shop |
| **horizon** | `2h` / `4h` / `to_day_end` / `7d` / `14d` / `30d` |
| **输出结构** | `{ points: [{t, p50, p20, p80}], cumulative_to_horizon, direction }` |
| **置信度字段** | `confidence ∈ [0,1]`；`confidence_capped: bool` |
| **更新频率** | 日内 horizon：每 30 min（Proposed）；长周期：每日 1 次（Proposed） |
| **输入特征** | 当日已过时段花费、近 7/14 日同时段花费、预算剩余、活动日历、plan_mode |

**输出示例（示意）：**

```json
{
  "object_id": "FC-CURVE-SPEND",
  "scope": {"plan_id": "PLAN-8821"},
  "horizon": "to_day_end",
  "as_of": "2026-09-11T11:00:00+08:00",
  "points": [
    {"t": "12:00", "p50": 1850, "p20": 1600, "p80": 2100},
    {"t": "18:00", "p50": 4200, "p20": 3600, "p80": 4900},
    {"t": "23:59", "p50": 6100, "p20": 5200, "p80": 7200}
  ],
  "cumulative_to_horizon": {"p50": 6100, "p20": 5200, "p80": 7200},
  "direction": "recovering",
  "confidence": 0.74,
  "confidence_capped": false,
  "based_on_validated_ids": ["VM-20260911-0900", "VM-20260911-1100"]
}
```

---

#### FC-CURVE-IMPRESSION：展现走势曲线

| 属性 | 值 |
|---|---|
| **对象 ID** | `FC-CURVE-IMPRESSION` |
| **粒度** | plan / campaign / shop |
| **horizon** | `2h` / `4h` / `to_day_end` / `7d` |
| **输出结构** | 同 `FC-CURVE-SPEND` 结构 |
| **置信度字段** | `confidence ∈ [0,1]` |
| **更新频率** | 日内：每 30 min（Proposed）；长周期：每日 |
| **输入特征** | 日内展现曲线、近 7 日同时段展现、出价/溢价历史、类目竞争（可得则用）、活动日历 |

---

#### FC-CURVE-CLICK：点击走势曲线

| 属性 | 值 |
|---|---|
| **对象 ID** | `FC-CURVE-CLICK` |
| **粒度** | plan / campaign / shop |
| **horizon** | `2h` / `4h` / `to_day_end` / `7d` |
| **输出结构** | 同上 |
| **置信度字段** | `confidence ∈ [0,1]` |
| **更新频率** | 日内：每 30 min（Proposed）；长周期：每日 |
| **输入特征** | 日内点击曲线、展现预测、CTR 历史、素材/创意状态 |

---

#### FC-CURVE-ADD_CART：加购走势曲线

| 属性 | 值 |
|---|---|
| **对象 ID** | `FC-CURVE-ADD_CART` |
| **粒度** | plan / shop / sku |
| **horizon** | `4h` / `to_day_end` / `7d` |
| **输出结构** | 同上 |
| **置信度字段** | `confidence ∈ [0,1]` |
| **更新频率** | 日内：每 1 h（Proposed）；长周期：每日 |
| **输入特征** | 点击预测、历史加购率、客单价带、生命周期阶段 |

> **说明：** 加购对高客单商品是更稳定的先导指标（理论 §7.2/§7.3），horizon 起点建议 ≥4h。

---

#### FC-CURVE-GMV：成交额走势曲线

| 属性 | 值 |
|---|---|
| **对象 ID** | `FC-CURVE-GMV` |
| **粒度** | plan / shop / sku |
| **horizon** | `to_day_end` / `7d` / `14d` |
| **输出结构** | 同上；额外字段 `trusted_gmv_flag: bool`（是否基于 trusted 口径） |
| **置信度字段** | `confidence ∈ [0,1]` |
| **更新频率** | 每日 2 次（Proposed：午间 + 日终前） |
| **输入特征** | 加购预测、历史 CVR、客单价分布、退款率、待付款率、活动日历、生命周期 |

> **硬约束：** GMV 曲线必须基于 `trusted_gmv` 口径；若仅有平台口径，`trusted_gmv_flag=false` 且置信度强制降档。

---

#### FC-CURVE-ROI：ROI 走势曲线

| 属性 | 值 |
|---|---|
| **对象 ID** | `FC-CURVE-ROI` |
| **粒度** | plan / shop |
| **horizon** | `to_day_end` / `7d` / `14d` |
| **输出结构** | `{ points: [{t, p50, p20, p80}], baseline_band: {p20, p80}, within_band_prob }` |
| **置信度字段** | `confidence ∈ [0,1]` |
| **更新频率** | 每日 2 次（Proposed） |
| **输入特征** | GMV 预测、花费预测、历史 ROI 序列、退款回冲率、自然/推广耦合估计 |

> **说明：** `within_band_prob` 是"ROI 是否仍在基线带内"的概率，直接支撑稳定性判断与 NO_ACTION 决策（§8.5）。`baseline_band` 由 STATE 提供的历史分位带（Proposed p20–p80）定义。

---

#### FC-ETA-BUDGET：预算耗尽时间

| 属性 | 值 |
|---|---|
| **对象 ID** | `FC-ETA-BUDGET` |
| **粒度** | plan / campaign / account |
| **horizon** | `to_day_end`（当日预算）；可选 `to_week_end` |
| **输出结构** | `{ projected_exhaust_at, burn_rate_now, burn_rate_projected, remaining_now, scenario_if_spend_up, scenario_if_spend_down }` |
| **置信度字段** | `confidence ∈ [0,1]` |
| **更新频率** | 每 30 min（Proposed） |
| **输入特征** | BudgetPosition（daily_budget, spent_today, remaining_today, burn_rate_per_hour）、花费曲线预测、活动日历、历史日内消耗模式 |

**输出示例（示意）：**

```json
{
  "object_id": "FC-ETA-BUDGET",
  "scope": {"plan_id": "PLAN-8821"},
  "horizon": "to_day_end",
  "as_of": "2026-09-11T11:00:00+08:00",
  "projected_exhaust_at": "2026-09-11T16:30:00+08:00",
  "burn_rate_now": 420.0,
  "burn_rate_projected": 380.0,
  "remaining_now": 2100.0,
  "scenario_if_spend_up": {"exhaust_at": "2026-09-11T15:10:00+08:00", "trigger": "+15% bid"},
  "scenario_if_spend_down": {"exhaust_at": "2026-09-11T18:00:00+08:00", "trigger": "no change"},
  "confidence": 0.81,
  "based_on_validated_ids": ["VM-20260911-1100"]
}
```

> **理论锚点：** GA-1 §6.2「预算耗尽时间」；Trace §5.3 预算生命周期预测。`projected_exhaust_at` 直接对应 JD Adapter `BudgetPosition.projected_exhaust_at` 字段语义，但 FE 是该字段的**预测来源**，Adapter 只是读取/展示。

---

#### FC-STAB-PLAN：计划稳定性评估

| 属性 | 值 |
|---|---|
| **对象 ID** | `FC-STAB-PLAN` |
| **粒度** | plan |
| **horizon** | `7d` / `14d` / `30d`（回看窗口）+ `to_day_end`（前瞻稳定性） |
| **输出结构** | `{ stability_score, stability_class, noise_threshold, adjustment_sensitivity, system_managed_flag }` |
| **置信度字段** | `confidence ∈ [0,1]` |
| **更新频率** | 每日 1 次（Proposed）；重大事件后即时刷新 |
| **输入特征** | 近 14–30 日指标变异系数、调整频率历史、系统托管状态、plan_mode、生命周期阶段、历史 NO_ACTION 正确率（若可得） |

**输出示例（示意）：**

```json
{
  "object_id": "FC-STAB-PLAN",
  "scope": {"plan_id": "PLAN-9012"},
  "horizon": "14d",
  "as_of": "2026-09-11T14:00:00+08:00",
  "stability_score": 0.82,
  "stability_class": "HIGH",
  "noise_threshold": {"impressions_pct": 0.12, "roi_pct": 0.08},
  "adjustment_sensitivity": "LOW",
  "system_managed_flag": true,
  "confidence": 0.78,
  "based_on_validated_ids": ["VM-20260911-1400"]
}
```

> **理论锚点：** GA-1 §8.5 稳定性优先原则；§6.2 计划稳定性。`stability_score` 与 `noise_threshold` 直接支撑 RE 的 NO_ACTION 决策路径（决策包样例 B 的 `CHK_STAB` 谓词）。`stability_class` 枚举：`HIGH` / `MEDIUM` / `LOW` / `UNKNOWN`。

---

#### FC-BURST-CAMPAIGN：活动爆发概率

| 属性 | 值 |
|---|---|
| **对象 ID** | `FC-BURST-CAMPAIGN` |
| **粒度** | shop / campaign / plan |
| **horizon** | `to_peak_window` / `2h` / `4h` / `to_day_end` |
| **输出结构** | `{ burst_prob, expected_peak_window, burst_magnitude_band, event_phase, post_burst_falloff_risk }` |
| **置信度字段** | `confidence ∈ [0,1]` |
| **更新频率** | 活动 PRE/PEAK 阶段：每 15 min（Proposed）；非活动期：每 2 h |
| **输入特征** | BusinessEvent（type, phase, expected_peak_window, price_release_state）、历史同类活动曲线、当前时段基线、计划获量能力 |

**输出示例（示意）：**

```json
{
  "object_id": "FC-BURST-CAMPAIGN",
  "scope": {"shop_id": "SHOP-DEMO-01"},
  "horizon": "to_peak_window",
  "as_of": "2026-09-11T19:00:00+08:00",
  "burst_prob": 0.71,
  "expected_peak_window": {"start": "2026-09-11T20:00:00+08:00", "end": "2026-09-11T22:00:00+08:00"},
  "burst_magnitude_band": {"p50_impression_multiplier": 2.4, "p20": 1.6, "p80": 3.5},
  "event_phase": "PRE",
  "post_burst_falloff_risk": "MEDIUM",
  "confidence": 0.65,
  "based_on_validated_ids": ["VM-20260911-1900"]
}
```

> **理论锚点：** GA-1 §6.2「活动爆发周期」；§7.4 活动爆发期策略；§8.3「晚间爆发预测」。`burst_prob` 为概率值而非二值判断；`post_burst_falloff_risk` 提示活动结束后回落风险，供 RE 区分"该抢量"与"该收敛"。

---

#### FC-RISK-INVENTORY：库存风险投影（条件启用）

| 属性 | 值 |
|---|---|
| **对象 ID** | `FC-RISK-INVENTORY` |
| **粒度** | sku / plan |
| **horizon** | `3d` / `7d` / `14d` |
| **输出结构** | `{ projected_stockout_at, days_of_cover_projected, stock_risk_level_projected, reorder_signal }` |
| **置信度字段** | `confidence ∈ [0,1]` |
| **更新频率** | 每日 1 次（Proposed）；放量动作前强制刷新 |
| **输入特征** | InventoryPosition（available_qty, replenishment_lead_time_days, safety_stock_threshold）、GMV/销量预测、历史日耗 |

> **启用条件：** 仅当 STATE 提供了完整的 `InventoryPosition`（`gap_flags` 不含 `MISSING_INVENTORY`）。否则 FE 不产出此对象，在 Bundle 中标记 `FC-RISK-INVENTORY: SKIPPED_MISSING_INPUT`。

---

### 3.3 汇总表（Proposed 默认值速查）

| 对象 ID | 粒度 | 主 horizon | 更新频率（Proposed） | 置信度阈值（Proposed） |
|---|---|---|---|---|
| FC-CURVE-SPEND | plan/campaign/shop | to_day_end | 30 min | ≥0.6 可触发写动作 |
| FC-CURVE-IMPRESSION | plan/campaign/shop | to_day_end | 30 min | ≥0.6 |
| FC-CURVE-CLICK | plan/campaign/shop | to_day_end | 30 min | ≥0.6 |
| FC-CURVE-ADD_CART | plan/shop/sku | to_day_end | 1 h | ≥0.55 |
| FC-CURVE-GMV | plan/shop/sku | to_day_end / 7d | 2 次/日 | ≥0.55 |
| FC-CURVE-ROI | plan/shop | to_day_end / 7d | 2 次/日 | ≥0.6 |
| FC-ETA-BUDGET | plan/campaign/account | to_day_end | 30 min | ≥0.7（ETA 对误差敏感） |
| FC-STAB-PLAN | plan | 14d | 1 次/日 | ≥0.5（稳定性判断容忍度较高） |
| FC-BURST-CAMPAIGN | shop/campaign/plan | to_peak_window | 15 min（活动期） | ≥0.65 |
| FC-RISK-INVENTORY | sku/plan | 7d | 1 次/日 | ≥0.7（库存风险误判代价高） |

> **全部 Proposed。** 置信度阈值定义：当预测对象置信度低于阈值时，对应预测**不可单独作为写动作的充分依据**；RE 可将其作为辅助信号但须结合其他证据。

---

## 4. ForecastBundle 与输出结构

### 4.1 ForecastBundle

一次 FE 调用返回一个 `ForecastBundle`：

```text
ForecastBundle {
  bundle_id*          : string          // 前缀 FC-
  request_id*         : ref             // 对应 ForecastRequest
  state_id*           : ref             // TrustedBusinessState.state_id
  as_of*              : timestamp
  runtime_envelope    : RuntimeEnvelope // 透传
  status*             : enum { OK, DEGRADED, BLOCKED }
  objects*            : ForecastObject[]  // 各预测对象完整输出
  summary*            : object            // 见 §4.2，写入 forecast_ref.summary
  overall_confidence* : number            // [0,1]，各对象置信度加权综合
  degraded_targets*   : enum[]            // 降级或跳过的对象 ID
  gap_flags*          : enum[]            // 从 STATE 透传 + FE 自身新增
  based_on_validated_ids* : string[]      // 全部输入 ValidatedMetricSet ID
  model_version       : string            // FE 模型/规则版本（可追溯）
  created_at*         : timestamp
}
```

### 4.2 summary 结构（对齐 Decision Packet forecast_ref.summary）

`summary` 是 FE 合成的摘要，供 RE 快速消费并写入 Decision Packet：

```text
summary: {
  // 日内走势摘要
  impression_trend: enum { up, down, flat, up_vs_baseline, down_vs_baseline }
  click_trend:      enum { up, down, flat }
  spend_trend:      enum { accelerating, steady, decelerating }
  roi_band:         enum { within_baseline, above_baseline, below_baseline }
  
  // 预算寿命
  budget_lifetime:  enum { adequate, tight, critical, exhausted_soon }
  projected_exhaust_at: timestamp | null
  
  // 稳定性
  stability_score:  number [0,1]
  stability_class:  enum { HIGH, MEDIUM, LOW, UNKNOWN }
  improvement_if_adjust: enum { above_noise, below_noise, unknown }
  
  // 活动
  burst_prob:       number [0,1] | null
  event_phase:      enum { NONE, PRE, LIVE, PEAK_WINDOW, POST } | null
  
  // 库存（若有）
  inventory_risk:   enum { OK, TIGHT, CRITICAL, OVERSTOCK } | null
  
  // 元信息
  risk_note:        string | null
  overall_confidence: number [0,1]
}
```

> **对齐说明：** Decision Packet 样例 A 中 `forecast_ref.summary` 的字段（`impression_trend`, `ctr_trend`, `budget_lifetime`, `risk_note`）是本结构的子集。本结构是 superset，Packet 只需引用 FE 返回的 summary 对象。

### 4.3 overall_confidence 计算（Proposed）

```text
overall_confidence = min(
  max_confidence_by_state,           // STATE confidence 映射上限
  weighted_mean(objects[].confidence, w = importance_weight)
)
```

其中 `importance_weight` 按预测对象对当前决策类型的相关性分配（Proposed）：
- 日内干预决策：曲线类权重高
- NO_ACTION 决策：`FC-STAB-PLAN` 权重高
- 预算决策：`FC-ETA-BUDGET` 权重高

---

## 5. 与 Reasoning Engine / Decision Packet 的 forecast_ref

### 5.1 forecast_ref 结构（对齐 Decision Packet Schema §2.3）

Decision Packet 中 `forecast_ref` 由 FE 产出的 ForecastBundle 填充：

```text
forecast_ref: {
  forecast_id*          : string      // ForecastBundle.bundle_id
  horizon*              : string      // 主 horizon，如 "to_18:00"
  confidence*           : number      // overall_confidence
  summary*              : object      // ForecastBundle.summary
  based_on_validated_ids* : string[]  // ValidatedMetricSet ID 列表
}
```

### 5.2 forecast_ref 写入规则

| 规则 | 说明 | 依据 |
|---|---|---|
| FR-I1 | `forecast_id` 必须是真实存在的 `ForecastBundle.bundle_id`，不可伪造 | DPK-I3 |
| FR-I2 | `based_on_validated_ids` 必须非空，且全部是 `ValidatedMetricSet` 的 ID | DPK-I3 |
| FR-I3 | `confidence < 0.6`（Proposed）时，Decision Packet 不得包含非 NO_ACTION 写动作 | DEC-PKT §2.3；架构 P2 |
| FR-I4 | `forecast_ref` 在 Executed 后不可修改（可变性 F） | DPK-I7 |
| FR-I5 | Shadow Packet 的 `forecast_ref` 与 standard 结构完全一致，仅 `runtime_envelope.env` 不同 | GA2-T11 |

### 5.3 RE 消费 FE 输出的方式

```text
RE.input = {
  state: TrustedBusinessState,
  forecast_bundle: ForecastBundle,     // 完整对象，不只 summary
  objective: ObjectiveSnapshot,
  knowledge_refs: KnowledgeRef[]
}

RE 在推理时：
  1. 读取 summary 做快速判断
  2. 对相关对象读取完整曲线/分位带做精细推理
  3. 将所引用的 forecast_id 写入 Decision Packet 的 forecast_ref
  4. 若 FE status=DEGRADED，RE 必须在 hypothesis.supporting_signals 中
     标注"基于降级预测"，且 Risk Engine 可据此收紧约束
```

### 5.4 FE 不输出动作的边界

FE 只输出预测与置信度。以下字段 FE **不产出**：

| 字段 | 归属 | 说明 |
|---|---|---|
| `proposed_actions[]` | RE | FE 不建议调价/调预算 |
| `hypothesis.cause_claim` | RE | FE 不归因 |
| `expected_response_window` | RE（参考 FE） | FE 可提供参考值，但最终由 RE 决定并写入 |
| `risk.risk_level` | RKE | FE 不做风险裁决 |

> **例外：** FE 的 `improvement_if_adjust=below_noise` 可以作为 RE 输出 NO_ACTION 的强信号，但 NO_ACTION 本身仍是 RE 的决策。

---

## 6. Shadow 模式下预测评估（回看）

### 6.1 定位

对齐 `Shadow_Mode_Design_v0.1.md` §4.2 L2 预测一致性对照。FE 在 Shadow 模式下**行为与 Live 完全一致**（同一套输入契约、同一套输出结构），差异仅在于：

1. `runtime_envelope.env ∈ {SHADOW, SIMULATION, FIXTURE}`  
2. 评估产物进入隔离池  
3. 预测误差样本可作为 FE 校准输入（标注来源）

### 6.2 回看评估记录格式

```text
ForecastEvalRecord {
  eval_id*              : string          // 前缀 FE-EVAL-
  bundle_id*            : ref             // 被评估的 ForecastBundle
  object_id*            : enum            // 被评估的预测对象 ID
  scope                 : object
  horizon               : string
  forecast_made_at*     : timestamp       // 预测产出时间
  evaluated_at*         : timestamp       // 回看时间
  actual_window*        : { start, end }
  
  // 预测值 vs 实际值
  predicted             : object          // 该对象的 p50 / 点估计
  actual                : object          // BDV 后的实际值
  error_metrics*        : {
    mae?: number
    mape?: number
    direction_hit?: bool
    within_band?: bool          // 实际值是否落在 p20–p80 分位带内
    lead_time_minutes?: number  // 拐点提前量（仅曲线类）
  }
  
  // 元信息
  env*                  : RuntimeEnvelope
  based_on_validated_ids* : string[]
  learning_pool*        : enum { LIVE_POOL, SHADOW_POOL }  // 默认 SHADOW_POOL
  notes                 : string
}
```

### 6.3 评估指标映射（对齐 Shadow Mode SM-M03/M04）

| 评估指标 | 对应 Shadow Mode 指标 | 定义 |
|---|---|---|
| `within_band` | SM-M03 预测命中率 | 实际值落在 p20–p80 分位带内的比例 |
| `mape` | SM-M04 预测 MAPE | 分 horizon 的平均绝对百分比误差 |
| `direction_hit` | SM-M01 方向一致率 | 走势方向（↑/↓/HOLD）是否正确 |
| `lead_time_minutes` | SM-M05 干预提前量 | 预测拐点相对实际拐点的提前量 |

### 6.4 评估调度

```text
ForecastBundle 产出时
  → 预注册：记录 forecast_made_at、predicted、horizon
  → 等待 actual_window 结束
  → 重新拉取 RO-MET-* + BDV（env 可为 LIVE_READ，但评估产物标 shadow-eval）
  → 生成 ForecastEvalRecord
  → 写入 Shadow Pool（隔离）
  → 周期汇总为 FE 校准报告
```

### 6.5 与 Learning 的关系

| 产物 | env=LIVE | env=SHADOW/SIMULATION/FIXTURE |
|---|---|---|
| ForecastEvalRecord | 主链，可进 FE 校准 | 隔离池；可作为"只读预测校准"输入（标注来源） |
| FE 校准信号 | 可调整模型权重/阈值 | 仅产生校准建议，不直接改 live 模型 |
| Trust 影响 | 预测准确率可间接进入 Trust 评估材料 | **禁止**直接提升 live Trust Score |

> 对齐 GA2-T11 §5.2 Learning 过滤矩阵：FE 校准样本在 shadow 下"可作为只读预测校准输入（标注来源）"。

---

## 7. 失败 / 低置信度行为

### 7.1 降级阶梯

```text
Level 0: 正常（status=OK）
  → 所有请求的预测对象正常产出，置信度在阈值以上

Level 1: 轻度降级（status=DEGRADED，部分对象置信度低于阈值）
  → 低置信度对象仍产出，但标记 confidence_capped=true
  → summary.overall_confidence 受影响
  → RE 须在 hypothesis.supporting_signals 中标注

Level 2: 重度降级（status=DEGRADED，关键对象跳过）
  → 跳过缺失输入的预测对象，degraded_targets 显式列出
  → summary 中对应字段为 null 或 UNKNOWN
  → RE 对缺失对象相关决策应倾向 HOLD / NO_ACTION

Level 3: 阻断（status=BLOCKED）
  → ready_for_forecast=false 或关键数据源完全缺失
  → 不产出任何预测对象
  → RE 不得形成非 NO_ACTION 写动作
  → Decision Packet 仍须成包（NO_ACTION 路径）
```

### 7.2 降级触发条件与行为

| 触发条件 | 降级级别 | FE 行为 | RE/SRA 行为 |
|---|---|---|---|
| STATE `confidence=LOW` | L1 | 所有对象置信度上限 ≤0.5（Proposed） | 写动作被 CHK_CONF 拒绝 |
| 日内曲线缺失 | L2 | 跳过曲线类对象 | 日内干预类决策 HOLD |
| 预算数据缺失 | L2 | 跳过 `FC-ETA-BUDGET` | 预算类决策 HOLD |
| 活动日历缺失 | L1 | `FC-BURST-CAMPAIGN` 退化为"无活动基线" | 爆发类决策降置信 |
| 库存数据缺失 | L2 | 跳过 `FC-RISK-INVENTORY` | 放量类决策 HOLD（Risk R3+） |
| `ready_for_forecast=false` | L3 | 返回 BLOCKED | 仅 NO_ACTION 可过门禁 |
| BDV FAIL | L3 | 返回 BLOCKED | 同上 |

### 7.3 "请求更多数据"机制

当 FE 因数据缺失降级时，可在 ForecastBundle 中输出数据请求信号：

```text
ForecastBundle.data_requests: [{
  missing_resource: enum { INTRADAY_CURVE, BUDGET_BURN, INVENTORY, EVENT_CALENDAR, ORDER_FACTS }
  scope: object
  priority: enum { HIGH, MEDIUM, LOW }
  blocks_targets: enum[]    // 哪些预测对象被阻塞
}]
```

STATE 或 CBA 可据此触发补拉取（经 Adapter RO），然后重新调用 FE。FE **不直接调用 Adapter**——数据请求是信号，不是命令。

### 7.4 建议 NO_ACTION 的条件（FE → RE 信号）

FE 不直接输出 NO_ACTION，但以下信号是 RE 输出 NO_ACTION 的强依据：

| FE 信号 | 含义 | 理论锚点 |
|---|---|---|
| `FC-STAB-PLAN.stability_class=HIGH` + `improvement_if_adjust=below_noise` | 调整收益低于噪声 | §8.5 |
| `FC-CURVE-ROI.within_band_prob ≥ 0.8` | ROI 在基线带内 | §8.5 |
| `FC-BURST-CAMPAIGN.burst_prob < 0.3` + `event_phase=NONE` | 无活动窗口 | §8.3 |
| FE status=BLOCKED | 数据不足，不可支撑写动作 | 架构 P3 |
| `overall_confidence < 0.5`（Proposed） | 预测整体不可靠 | §8.4 |

---

## 8. 理论追踪

| 理论主张 | GA-1 锚点 | 本文落点 | 覆盖 |
|---|---|---|---|
| Prediction-driven Decision | §6.2, GA-INNOV-002 | §1 FE 定位；§3 预测对象目录；§5 forecast_ref | Mapped |
| 预测对象清单（CTR/CPC/CVR/ROI/GMV/加购/预算耗尽/库存/日内/爆发/稳定性/生命周期） | §6.2 | §3 Catalog 覆盖曲线类 + ETA + 稳定性 + 爆发 + 库存 | Mapped |
| 双时间尺度决策 | §8.3 | §1.4 FE-P4；§3 各对象 horizon 双档 | Mapped |
| 决策可信度验证 | §8.4 | §3.2 ROI within_band_prob；§7 降级阶梯 | Mapped |
| 稳定性优先原则 | §8.5 | `FC-STAB-PLAN`；§7.4 NO_ACTION 信号 | Mapped |
| 调整响应窗口 | §8.6 | §5.3 RE 参考 FE 提供的预期窗口 | Partial（FE 提供参考，RE 决定） |
| Business State Awareness | §6.3, GA-INNOV-003 | §2 输入契约强制 Trusted State | Mapped |
| 活动事件感知 | Trace §5.2；§7.4 | `FC-BURST-CAMPAIGN` | Mapped |
| 预算生命周期预测 | Trace §5.3；§6.2 | `FC-ETA-BUDGET` | Mapped |
| 日内走势预测 | Trace §5.1；§8.3 | 曲线类对象日内 horizon | Mapped |
| 活动爆发期参数动态调整 | §7.4 | `burst_prob` + `burst_magnitude_band` 供 OFG/RE 消费 | Mapped |
| 失败即学习事件 | §9.4 | §6 ForecastEvalRecord 进入 Shadow Pool | Mapped（shadow 隔离） |
| Shadow/只读红线 | GA-DEC-004 | §6 shadow 评估隔离 | Mapped |

---

## 9. 待决问题

| ID | 问题 | 建议（Draft） | 阻塞 | 归属 |
|---|---|---|---|---|
| FE-Q01 | 曲线类预测的分位带（p20/p50/p80）如何校准？ | 首期用历史分位数；后续用分位回归模型 | 否 | GA2-T15 |
| FE-Q02 | `overall_confidence` 的加权公式是否需要按 plan_mode 分型？ | 是；SEEDING 曲线权重高，HARVEST 稳定性权重高 | 否 | OFG 联调 |
| FE-Q03 | 活动爆发概率的历史基线从哪里来？ | 同类活动 Event 的历史曲线（需积累 ≥3 次，Proposed） | 否 | 数据积累 |
| FE-Q04 | FE 模型版本（`model_version`）的治理归属？ | KE 治理，与 Parameter Genome 同级 | 否 | KE / GA2-T14 |
| FE-Q05 | 预测回看的 `actual_window` 到期由谁调度？ | 与 Decision Packet `expected_response_window` 同源调度（DPK-Q09） | 否 | 运行时 |
| FE-Q06 | FE 是否需要消费 Parameter Genome 的期望值作为先验？ | 是；Genome `kpi_expectations` 可作为曲线先验锚点 | 否 | Genome 联调 |
| FE-Q07 | 多 plan 并发时 FE 的计算资源分配策略？ | 后置；先保证单 plan 正确性 | 否 | 基础设施 |
| FE-Q08 | Shadow 评估的 ForecastEvalRecord 是否影响 FE 模型更新？ | 仅产生校准建议；不直接改 live 模型（对齐 T11 §5.2） | 否 | GA2-T11 联调 |
| FE-Q09 | `FC-RISK-INVENTORY` 的 `projected_stockout_at` 与 JD `estimated_days_of_cover` 的关系？ | FE 提供时间投影，JD 提供当前天数；两者互补 | 否 | JD 联调 |
| FE-Q10 | 曲线预测的时间粒度（小时 vs 30min）如何选择？ | 日内 horizon 用小时；活动 PEAK_WINDOW 可加密到 15 min（Proposed） | 否 | 标定 |

---

## 10. 与后续任务的接口

| 下游 | 本文供给 |
|---|---|
| GA2-T14 知识演化 | FE 模型版本治理接口；预测精度作为 Genome 质量分参考信号 |
| GA2-T15 参数预标定 | 预测对象 horizon 与阈值 Proposed 默认值；评估指标定义 |
| GA-3 验证 | ForecastEvalRecord 格式；SM-M03/M04 对齐的评估协议 |
| Decision Packet（GA2-T10） | `forecast_ref` 完整填充规则与 FR-I1..I5 不变式 |
| Shadow Mode（GA2-T11） | L2 评估的数据格式与调度约定 |

---

## 11. 变更记录

| 日期 | 版本 | 变更 | 依据 |
|---|---|---|---|
| 2026-09-11 | v0.1 | 首次建立：FE 定位与四回路位置、输入契约、11 个预测对象目录、ForecastBundle 输出、forecast_ref 规则、Shadow 回看评估、降级阶梯、理论追踪与待决 | GA2-T13；Architecture v0.2；GA-1 §6.2/§8.3/§8.5；Decision Packet Schema；Shadow Mode Design |

---

**Document Status:** Draft  
**Next Review:** 项目负责人 / Research Architect  
**Explicit Non-claim:** 本文不代表已实现任何预测模型或接入真实数据源；所有阈值、窗口、更新频率与置信度门槛均为 Proposed；FE 不产生任何平台副作用。
