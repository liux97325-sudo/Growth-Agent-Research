# GA-2：商品推广参数基因与默认策略模板体系设计

**文档编号：** GA-2-GENOME-001  
**版本：** v0.1  
**状态：** Draft  
**阶段：** GA-2 Engineering Design  
**输入基线：** `Research/GA-1/GA-1_Theory_v1.0.md`（GA-1.0 / v1.0，Confirmed）  
**关联架构：** `Architecture_Overview_v0.2.md`（Confirmed，GA-DEC-004）  
**关联追踪：** `Theory_Engineering_Trace.md`（GA-INNOV-009 → Partial → 本文件）  
**任务编号：** GA2-T07  
**约束：** 本文档为工程设计草案，不是新理论；所有数值默认值均标注为 **Proposed** 或 **Pending**，不得作为已验证真值引用；与理论冲突时以 GA-1 为准并修订本文。

---

## 1. 文档目的与范围

将 GA-1 §10.2 **Promotion Parameter Genome（商品推广参数基因）** 与 §15 中「参数预标定、默认策略模板」工程入口，收敛为：

1. 参数基因的**对象模型**（字段、类型、约束）；
2. 商品维度**分类空间**（客单价带、推广目的、生命周期）；
3. **动态目标函数权重模板**（对齐 §7.2–7.4、§8.2 指标优先级）；
4. 默认策略模板的**目录结构建议**；
5. 从历史优秀计划抽取基因的**参数预标定流程**（流程设计，非真实数据实现）；
6. **风险基线与调整频率**默认区间（全部 Proposed）；
7. 理论追踪与**待决问题**。

**本文件不包含：** 真实广告账户操作、真实参数标定结果、平台 API 联调、GA-3 实验结论。

---

## 2. 设计原则（自理论派生）

| ID | 原则 | 理论锚点 | 工程含义 |
|---|---|---|---|
| G1 | 基因是知识资产，不是运行时缓存 | GA-INNOV-006/009；§6.6, §10.2 | 参数基因由 Knowledge Engine 治理，有版本、质量分与生命周期 |
| G2 | 无固定目标函数 | §7.2, §8.2 | 权重模板由 OFG 按维度组合生成，基因只携带模板引用与偏置 |
| G3 | 稳定性可优先于单日 ROI | §8.5 | 基因可包含 `NO_ACTION` 偏好与调整冷却，而非仅“追求最优” |
| G4 | 种草与收割行为模式不同 | §7.3 | 调整频率、权限依赖、稳定性敏感度分型建模 |
| G5 | 默认值是先验，不是结论 | 理论边界 §14 | 所有 Proposed 区间待历史标定与 GA-3 验证后升格 |
| G6 | 风险基线动态 | §11.1 | 基因携带风险档位与探索预算上限，由 Risk Engine 联合解释 |
| G7 | 经验可降权/遗忘 | §9.4 | 基因实例支持 decay、merge、deprecate，不可静默硬删 |
| G8 | 平台隔离 | 架构 P8 | 基因字段区分 `platform_binding` 与可迁移核心 |

---

## 3. 参数基因对象模型

### 3.1 概念定位

```text
Promotion Parameter Genome（基因型 / Template）
        ↓  apply + 企业/商品实例化
Genome Instance（表现型 / Instance）
        ↓  绑定到具体计划上下文
Effective Plan Parameters（运行参数快照）
```

- **Genome（基因型）**：可复用的知识结晶，存在于默认模板库与企业知识库。  
- **Instance（表现型）**：某商品×某阶段×某平台下的一次具体采用，带观测统计与质量分。  
- **Effective Snapshot**：实际下发给场景 Agent 的参数包，必须可追溯到 Instance 与 Genome 版本。

> 理论对应：§10.2「为不同类型商品建立参数模板」；§10.3 Knowledge Crystallization。

### 3.2 核心字段模型（Genome）

> 类型说明为工程草案（Draft），最终以 GA2-T04 数据模型评审为准。

| 字段 | 类型 | 必填 | 约束 / 说明 | 理论锚点 |
|---|---|---|---|---|
| `genome_id` | string | Y | 稳定 ID，如 `JD-LOWFM-SEED-S1` | §10.2 |
| `genome_name` | string | Y | 人类可读名 | — |
| `version` | semver | Y | `major.minor.patch`；默认模板从 `0.1.0` 起 | 架构 KE 版本治理 |
| `status` | enum | Y | `Proposed` / `Active` / `Deprecated` / `Retired` | 本文约束 |
| `source` | enum | Y | `Expert_Prior`（专家先验）/ `Calibrated`（历史标定）/ `Evolved`（运行演化） | §10.1, §15 |
| `platform` | enum[] | Y | `JD` / `Douyin` / `Multi` | P8 |
| `category` | object | Y | 商品维度分类，见 §4 | §7.2 |
| `objective_profile` | object | Y | 目标函数权重模板引用与偏置，见 §5 | §7.2/7.3/8.2 |
| `budget_profile` | object | Y | 初始预算、日预算、种草/收割比例 | §10.2, §7.4 |
| `bidding_profile` | object | Y | 关键词出价、人群溢价策略 | §7.3, §10.2 |
| `kpi_expectations` | object | Y | 预期 CTR / 加购率 / 转化率 / ROI | §10.2 |
| `risk_baseline` | object | Y | 风险档位、探索预算、止损条件 | §11.1 |
| `adjustment_policy` | object | Y | 调整频率、冷却、幅度上限、响应窗口假设 | §7.3, §8.5, §8.6 |
| `lifecycle_fit` | enum[] | Y | 适用生命周期阶段集合 | §7.4 |
| `purpose_fit` | enum[] | Y | `Seed`（种草）/ `Harvest`（收割）/ `Both` | §7.3 |
| `trust_required_level` | int 0–5 | Y | 采用该基因实例所需最低 Trust Level | §6.7, 架构 §7 |
| `quality_score` | object | N* | 复用次数、稳定性、可迁移性等；Calibrated 后必填 | §9.3 |
| `lineage` | object | N | 父基因、标定样本集摘要、决策日志引用 | §9.2, 架构 TRACE |
| `constraints` | object | N | 平台字段硬约束、合规白名单 | §11.2 |
| `metadata` | object | N | 负责人、标签、备注 | — |

\* `Expert_Prior` 可暂空 `quality_score`；升为 `Calibrated` 前必须补齐。

### 3.3 关键子对象字段

#### 3.3.1 `category`（商品维度）

| 字段 | 类型 | 取值 |
|---|---|---|
| `price_band` | enum | `Low_Frequency_Fast_Moving`（低客单快消） / `Mid_High_Brand`（中高客单/品牌） / `Unclassified` |
| `life_cycle_stage` | enum | `Explore` / `Grow` / `Mature` / `Campaign` / `Decline_Clearance`（对应 §7.4 五阶段） |
| `plan_purpose` | enum | `Seed` / `Harvest` |
| `category_tags` | string[] | 企业类目标签（可选） |

#### 3.3.2 `budget_profile`

| 字段 | 类型 | 约束 | 标注 |
|---|---|---|---|
| `initial_budget` | number | ≥ 0；单位：平台货币 | Proposed 区间见 §6 |
| `daily_budget_cap` | number | ≥ `initial_budget` 日摊建议 | Proposed |
| `seed_harvest_ratio` | object | `{seed: 0–1, harvest: 0–1, sum≈1}` | 按 §7.4 表动态 |
| `explore_budget_ceiling` | number | 新建/试错预算上限 | Proposed |
| `scale_up_step_pct` | number | 放量步长百分比 | Proposed |

#### 3.3.3 `bidding_profile`

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `kw_bid_strategy` | enum | `Manual_Range` / `System_Auto` / `Hybrid` | 收割偏 System_Auto（§7.3） |
| `kw_bid_range` | object | `{min, max, default}` | Currency |
| `audience_premium_strategy` | enum | `Manual_Range` / `System_Auto` / `Hybrid` | |
| `audience_premium_range` | object | `{min, max, default}` 百分比 | |
| `roi_target` | number | > 0；收割计划主控项 | §7.3 |
| `adjust_on_click_drop` | boolean | 种草常为 true | §9.2 因果样例 |

#### 3.3.4 `kpi_expectations`（先验区间，非考核硬指标）

| 字段 | 类型 | 标注 |
|---|---|---|
| `ctr_p50` / `ctr_band` | number / range | Proposed |
| `add_to_cart_rate_p50` / band | number / range | Proposed |
| `cvr_p50` / band | number / range | Proposed |
| `roi_p50` / band | number / range | Proposed |
| `cpc_p50` / band | number / range | Proposed |

> 说明：区间用于 Forecast 校准与 Self-review 对照，**不是**已验证企业真值。

#### 3.3.5 `risk_baseline`

| 字段 | 类型 | 说明 | 标注 |
|---|---|---|---|
| `risk_profile` | enum | `Conservative` / `Balanced` / `Aggressive_Exploration` / `Campaign_Go` / `Inventory_Constrained` | 对齐 §11.1 表 |
| `max_daily_loss_ratio` | number | 相对日预算 | Proposed |
| `min_effectiveness_ratio` | number | 低于则停新建、转优化既有（§11.1） | Proposed |
| `max_concurrent_new_plans` | int | 探索并发上限 | Proposed |
| `stop_loss_triggers` | object[] | 触发条件表达式列表 | 设计占位 |

#### 3.3.6 `adjustment_policy`

| 字段 | 类型 | 说明 | 标注 |
|---|---|---|---|
| `adjust_freq_class` | enum | `High`（种草） / `Medium` / `Low`（收割/高客单） | §7.3 定性已确认；数值 Proposed |
| `min_cooldown_hours` | number | 同参数两次调整最小间隔 | Proposed |
| `max_bid_change_pct` | number | 单次出价变动上限 | Proposed |
| `max_budget_change_pct` | number | 单次预算变动上限 | Proposed |
| `response_window_hours` | object | 按动作类型的调整响应窗口先验 | §8.6；数值 Proposed |
| `prefer_stability` | boolean | 成熟计划优先不调整 | §8.5 |

### 3.4 生命周期与状态机（Genome）

```text
[Expert_Prior / Proposed]
        ↓  预标定（§7）+ 审核
[Calibrated / Active]
        ↓  运行反馈 + Weekly Reflection
[Evolved / Active vN+1]  ←可并行保留旧版本
        ↓  质量分过低 / 平台规则变更 / 企业策略变更
[Deprecated]
        ↓  无引用且观察期满
[Retired]（保留审计，不物理删除）
```

### 3.5 完整性与校验规则（Draft）

1. `seed_harvest_ratio.seed + harvest` ∈ `[0.98, 1.02]`（允许舍入）。  
2. `price_band=Low_Frequency_Fast_Moving` 且 `plan_purpose=Harvest` 时，`objective_profile` 必须以 `gmv_roi` 为第一优先（§7.2）。  
3. `price_band=Mid_High_Brand` 且 `plan_purpose=Seed` 时，`objective_profile` 必须以 `ctr` 为第一优先（§7.2）。  
4. `life_cycle_stage=Explore` 时，`risk_profile` 不得为 `Campaign_Go`。  
5. `adjust_freq_class=Low` 时，`min_cooldown_hours` 必须 ≥ `Medium` 档下限（见 §6）。  
6. `status=Active` 且 `source=Calibrated` 时，`quality_score` 与 `lineage` 必填。  
7. 任何字段变更必须 bump `version` 并写 `lineage.change_log`。

---

## 4. 商品维度分类空间

### 4.1 客单价带（理论 §7.2）

| 代码 | 名称 | 定性特征（理论） | 主导指标序（理论原序） |
|---|---|---|---|
| `Low_Frequency_Fast_Moving` | 低客单快消 | 人群广、同质化强、偏快速成交 | 成交 ROI > 加购 > 点击率 > 点击单价 > 点击数 > 展现量 |
| `Mid_High_Brand` | 中高客单/品牌溢价 | 转化周期长、种草与人群积累更重要 | 点击率 > 点击数 > 加购 > 展现数 > 点击单价 > 成交 ROI |
| `Unclassified` | 未分类 | 冷启动/数据不足 | 使用企业默认混合模板，观察期后重分类 |

> 工程注记：价格带切分阈值 **Pending**（需企业类目与历史分布标定），本文不发明数值切分。

### 4.2 推广目的（理论 §7.3）

| 代码 | 名称 | 目标 | 行为模式 | 调整倾向 |
|---|---|---|---|---|
| `Seed` | 种草计划 | 曝光、点击、触达、加购积累 | 关键词出价、人群溢价、触达范围、展现/点击质量 | 更高频 |
| `Harvest` | 收割计划 | 成交与 ROI | 商品选择、ROI 设置、预算、推广目标；偏系统托管 | 更强调稳定，低频 |

### 4.3 生命周期五阶段（理论 §7.4）

| 代码 | 中文 | 种草权重（定性） | 收割权重（定性） | 主要目标 |
|---|---|---|---|---|
| `Explore` | 新品探索期 | 高 | 低 | 获取人群与数据 |
| `Grow` | 成长放量期 | 中高 | 中 | 扩大有效流量 |
| `Mature` | 成熟稳定期 | 中低 | 高 | 提高成交效率 |
| `Campaign` | 活动爆发期 | 动态提高 | 动态提高 | 抢占爆发流量 |
| `Decline_Clearance` | 衰退/清仓期 | 低 | 高 | 快速转化与清库存 |

### 4.4 分类笛卡尔积与基因覆盖策略

合法组合（第一轮建议）：

- `price_band(2 有效值) × purpose(2) × life_cycle(5) = 20` 个**主槽位**。  
- `Unclassified` 使用 `default/` 混合模板，不单独占用 20 槽。  
- `Campaign` 阶段可复用主基因并叠加 **Campaign Overlay**（见 §5.4），避免为活动单独复制全套基因。

覆盖原则：**先主槽位全覆盖（Expert_Prior）→ 再按企业历史数据标定高频槽位 → 长尾槽位保持 Prior + 观察。**

---

## 5. 动态目标函数权重模板

### 5.1 指标词典（与理论对齐）

| 指标代码 | 含义 | 理论用语 |
|---|---|---|
| `gmv_roi` | 成交 ROI | 成交 ROI |
| `add_cart` | 加购 | 加购总数/加购数 |
| `ctr` | 点击率 | 点击率 |
| `cpc` | 点击单价 | 点击单价 |
| `clicks` | 点击数 | 点击数/点击 |
| `impressions` | 展现 | 展现量/展现数 |

> 工程映射：OFG（Objective Function Generator）按 §7.2 序关系生成**有序权重**，而非任意自由权重，降低过拟合与不可解释性。

### 5.2 序关系模板（直接来自理论，Confirmed 语义）

#### T-LFM-HARVEST：低客单 × 收割

```text
gmv_roi > add_cart > ctr > cpc > clicks > impressions
```

#### T-LFM-SEED：低客单 × 种草

理论未给低客单种草专序。**工程草案（Proposed）**：在 T-LFM-HARVEST 上将触达类上提，仍保留成交导向：

```text
add_cart > ctr > clicks > impressions > gmv_roi > cpc
```

#### T-MHB-SEED：中高客单 × 种草

```text
ctr > clicks > add_cart > impressions > cpc > gmv_roi
```

#### T-MHB-HARVEST：中高客单 × 收割

理论未给中高客单收割专序。**工程草案（Proposed）**：偏成交，但因客单高，稳定性与点击质量仍重要：

```text
gmv_roi > add_cart > ctr > clicks > cpc > impressions
```

### 5.3 权重数值模板（全部 Proposed）

将序关系映射为可计算权重（总和 = 1.0）。推荐 **等比递减** 起点：`w_i = r^{rank-1} / Σ r^{k-1}`，默认 `r = 0.75`（Proposed）。示意（`r=0.75` 时约）：

| 模板 | r1 | r2 | r3 | r4 | r5 | r6 |
|---|---:|---:|---:|---:|---:|---:|
| T-LFM-HARVEST | 0.31 | 0.23 | 0.17 | 0.13 | 0.10 | 0.06 |
| T-MHB-SEED | 0.31 | 0.23 | 0.17 | 0.13 | 0.10 | 0.06 |
| T-LFM-SEED / T-MHB-HARVEST | 同结构，按各自序填入 | | | | | |

> **Pending：** `r` 值、是否采用非均匀衰减、是否允许企业覆盖，待历史优秀计划标定与敏感性分析。

### 5.4 生命周期叠加偏置（Lifecycle Bias，Proposed）

在基础模板上对权重做**乘性偏置**后重归一化：

| 阶段 | 偏置方向 |
|---|---|
| Explore | ↑ `ctr`, `clicks`, `impressions`；↓ `gmv_roi` |
| Grow | ↑ `clicks`, `add_cart`；轻微 ↓ `cpc` 敏感度 |
| Mature | ↑ `gmv_roi`, `add_cart` |
| Campaign | 活动日：整体 ↑ 获量类；允许 ↓ `gmv_roi` 权重（§11.1「动态放宽 ROI，保障获量」） |
| Decline_Clearance | ↑↑ `gmv_roi`, `add_cart`；↓ 新客探索类 |

`Campaign Overlay` 可临时替换/覆盖 `objective_profile`，有效期绑定活动窗口，结束后回落到主基因。

### 5.5 与 Reasoning 的接口约定（Draft）

```text
OFG.generate(context) -> ObjectiveProfile {
  template_id, weights{6}, overrides[], explanation, valid_until
}
```

- `context` 至少含：`price_band`, `plan_purpose`, `life_cycle_stage`, `inventory_state`, `activity_event`, `enterprise_goal`, `risk_level`（§8.2 动态因素）。  
- 输出必须可解释（引用模板 ID 与偏置原因），供 Self-review 使用。  
- 允许企业**只改序与偏置强度**，默认不允许随意打乱理论序（需 `status=Evolved` + 质量分门槛）。

---

## 6. 风险基线与调整频率默认区间

> **本节全部数值为 Proposed，非实证结论。** 用于工程占位与评审讨论，GA-3 前不得升格表述。

### 6.1 风险档案默认映射（对齐 §11.1）

| risk_profile | 适用 | 策略语义（理论） |
|---|---|---|
| `Conservative` | 高 ROI 商品、成熟收割 | 稳步推进，严格风控 |
| `Balanced` | 成长放量、一般计划 | 默认档 |
| `Aggressive_Exploration` | 新品探索 | 小预算试错 |
| `Campaign_Go` | 活动爆发 | 动态放宽 ROI，保障获量 |
| `Inventory_Constrained` | 库存紧张 | 限制加预算或暂停扩量 |

### 6.2 数值默认区间（Proposed）

| 参数 | Explore | Grow | Mature | Campaign | Decline_Clearance |
|---|---|---|---|---|---|
| 初始/测试日预算相对档 | 低 | 中低 | 中 | 中高（活动窗） | 中（清库存） |
| `max_daily_loss_ratio` | 0.15–0.25 | 0.10–0.20 | 0.08–0.15 | 0.20–0.35 | 0.10–0.20 |
| `min_effectiveness_ratio` | 0.60–0.75 | 0.70–0.85 | 0.80–0.95 | 活动期放宽 +0.05–0.15 | 0.75–0.90 |
| `max_concurrent_new_plans` | 1–3 | 2–5 | 0–2 | 按活动策略 | 0–1 |
| `scale_up_step_pct` | 10–20% | 15–30% | 5–15% | 20–50%（窗内） | 5–10% |

> 相对档（低/中/高）需企业预算标定后写入绝对值（Pending）。

### 6.3 调整频率与冷却（Proposed）

| adjust_freq_class | 典型场景 | min_cooldown_hours | max_bid_change_pct | max_budget_change_pct |
|---|---|---|---|---|
| `High` | 低客单种草、探索期 | 2–6 | 10–20% | 15–30% |
| `Medium` | 成长期、混合 | 6–12 | 10–15% | 10–20% |
| `Low` | 高客单收割、成熟稳定 | 24–72 | 5–10% | 5–15% |

补充规则（定性已确认 / 数值 Proposed）：

1. `prefer_stability=true` 时，即使预测有小幅改进，若 < 噪声阈值，输出 `NO_ACTION`（§8.5）。  
2. 同一动作未过 `response_window_hours` 不得二次同向调整（§8.6）。  
3. Campaign 窗口内可临时将频率上调一档，窗口结束后强制回落并观察 1 个冷却周期。

### 6.4 调整响应窗口先验（Proposed）

| 动作类型 | 先验观察窗 | 标注 |
|---|---|---|
| 关键词出价 ↑ → 展现变化 | 2–6 h | Pending |
| 人群溢价 → 点击变化 | 2–8 h | Pending |
| ROI 目标 ↓ → 获量变化 | 4–12 h | Pending |
| 预算 ↑ → 晚间成交 | 至当日高峰后 / 6–12 h | Pending |

---

## 7. 参数预标定流程（非真实数据实现）

目标：从**历史优秀计划**抽取基因，将 `Expert_Prior` 升为 `Calibrated`。本节定义流程与门禁，不实现代码、不跑真实账户数据。

### 7.1 流程总览

```text
[历史计划日志 + 经营状态 + 动作审计]
        → S1 数据真实性校验（BDV）
        → S2 标签完备（分类维度回填）
        → S3 优秀计划筛选（Effectiveness Filter）
        → S4 特征抽取与聚类（同槽位内）
        → S5 分位数区间估计（KPI/预算/出价）
        → S6 生成 Candidate Genome
        → S7 反事实/稳定性抽检（样本内）
        → S8 Self-review + 风险对齐
        → S9 Knowledge Engine 入库（status=Calibrated）
        → S10 小流量验证（GA-3 / 企业沙箱）后 Active 推广
```

### 7.2 各阶段要点

#### S1 数据真实性校验

- 剔除/降权：待付款、退款、重复归因、跨计划污染、异常大额订单（§8.1, §9.4）。  
- 使用去重后真实成交额，而非平台展示成交额直接标定 ROI。

#### S2 标签完备

为每条计划会话回填：`price_band`, `plan_purpose`, `life_cycle_stage`, 活动标记、库存紧张标记。  
标签缺失率过高 → 该会话仅作观察样本，不进入标定主集。

#### S3 优秀计划筛选

优秀定义**不固定单一 ROI**，而按动态目标函数得分：

```text
score = Σ w_i(context) * normalize(metric_i)
```

筛选建议（Proposed）：同槽位内得分 Top-P（如 P=20–30%）且满足风险底线、无重大合规事件、观察天数 ≥ 下限。

#### S4 特征抽取与聚类

- 抽取：初始预算、日预算轨迹、种草/收割比、出价/溢价分布、ROI 目标轨迹、调整次数与幅度、`NO_ACTION` 占比。  
- 在**同一槽位**（price_band × purpose × stage）内做简单聚类或分位分组，得到 1–N 个候选基因簇。

#### S5 分位数区间估计

对每个簇输出 p25/p50/p75，写入 `kpi_expectations` 与 `bidding_profile` 区间；样本过少 → 保持 Prior 并标 `sample_size_low`。

#### S6 Candidate Genome 生成

- `source=Calibrated`，`version=0.1.0` 或 `major` 升版。  
- 写入 `lineage`：样本 ID 列表摘要、时间窗、筛选阈值、排除规则。

#### S7 样本内抽检

- 留出一部分优秀/失败计划做对照：候选基因参数是否能区分成败模式。  
- 计算初步 `quality_score`（重复验证次数、稳定性、可迁移性代理指标，§9.3）。

#### S8 门禁

Self-review 检查清单（§11.2 + 架构 SRA）：

- 是否符合历史优秀计划模型；  
- 是否低于风控底线；  
- 库存/预算/合规风险；  
- 是否符合生命周期策略与企业目标；  
- 置信度是否足够进入 Active。

#### S9–S10 入库与验证

- 入库后默认可给 Trust Level ≥ 1 的 Agent 作为建议来源。  
- 真正自动新建计划仍受 Trust Level 与探索预算约束。  
- **验证结论产出在 GA-3，不在本设计文档。**

### 7.3 预标定输出物

| 产物 | 说明 |
|---|---|
| Candidate/Calibrated Genome JSON | 入 KE 基因库 |
| 槽位覆盖矩阵 | 20 槽 × Prior/Calibrated 状态 |
| 标定报告 | 样本量、剔除规则、分位表、未决槽位 |
| 失败模式附录 | 低产效计划特征，供 Failure Pattern（不直接进默认模板） |

### 7.4 明确非目标

- 本文不提供真实企业数据标定结果；  
- 不自动改写 GA-1 理论序关系；  
- 不在无历史数据时编造“最优参数”。

---

## 8. 默认策略模板目录结构建议

> 文件系统/对象存储布局建议（Draft）。逻辑上由 Knowledge Engine 的 Genome Registry 管理；下列树便于评审与版本管理。

```text
knowledge/
  genomes/
    registry.json                         # 索引：id → path, version, status
    defaults/                             # GA-2 出厂默认（Expert_Prior / Proposed）
      _schema/
        genome.schema.json                # 字段与约束校验
        objective_profile.schema.json
        risk_baseline.schema.json
      objective_templates/
        T-LFM-HARVEST.json
        T-LFM-SEED.json
        T-MHB-SEED.json
        T-MHB-HARVEST.json
        biases/
          lifecycle_explore.json
          lifecycle_grow.json
          lifecycle_mature.json
          lifecycle_campaign.json
          lifecycle_decline_clearance.json
      jd/
        low_fmq/
          seed/
            explore.json
            grow.json
            mature.json                   # 若业务上少见，可 stub + 说明
            campaign_overlay.json
            decline_clearance.json
          harvest/
            explore.json
            grow.json
            mature.json
            campaign_overlay.json
            decline_clearance.json
        mid_high_brand/
          seed/
            ...（同上五阶段 + overlay）
          harvest/
            ...（同上五阶段 + overlay）
      douyin/
        ...                               # 结构同构；字段平台绑定不同
      unclassified/
        mixed_default.json
    enterprise/                           # 企业标定结果（运行期写入，不在本仓库）
      {tenant_id}/
        jd/... 
        calibration_reports/
          {yyyymmdd}_slot_coverage.md
    archive/                              # Deprecated/Retired，只读审计
```

### 8.1 文件命名约定

- 生命周期文件名与 `life_cycle_stage` 枚举小写一致。  
- `campaign_overlay.json` 不替代主基因，引用 `base_genome_id`。  
- 企业目录不得提交到研究仓库默认树（隐私与租户隔离）。

### 8.2 单文件最小骨架（示例，数值 Proposed）

```json
{
  "genome_id": "JD-LFM-HARVEST-MATURE",
  "genome_name": "京东·低客单快消·收割·成熟稳定期",
  "version": "0.1.0",
  "status": "Proposed",
  "source": "Expert_Prior",
  "platform": ["JD"],
  "category": {
    "price_band": "Low_Frequency_Fast_Moving",
    "life_cycle_stage": "Mature",
    "plan_purpose": "Harvest"
  },
  "objective_profile": {
    "template_id": "T-LFM-HARVEST",
    "bias_ref": "lifecycle_mature",
    "weight_mode": "ordinal_decay",
    "decay_r": 0.75
  },
  "budget_profile": {
    "initial_budget": "PENDING_ENTERPRISE_SCALE",
    "daily_budget_cap": "PENDING_ENTERPRISE_SCALE",
    "seed_harvest_ratio": {"seed": 0.25, "harvest": 0.75},
    "explore_budget_ceiling": 0,
    "scale_up_step_pct": 10
  },
  "bidding_profile": {
    "kw_bid_strategy": "Hybrid",
    "roi_target": "PENDING_CALIBRATION",
    "audience_premium_strategy": "Hybrid"
  },
  "kpi_expectations": {
    "ctr_p50": "PENDING_CALIBRATION",
    "roi_p50": "PENDING_CALIBRATION"
  },
  "risk_baseline": {
    "risk_profile": "Conservative",
    "max_daily_loss_ratio": 0.12,
    "min_effectiveness_ratio": 0.85,
    "max_concurrent_new_plans": 1
  },
  "adjustment_policy": {
    "adjust_freq_class": "Low",
    "min_cooldown_hours": 24,
    "max_bid_change_pct": 8,
    "max_budget_change_pct": 10,
    "prefer_stability": true
  },
  "trust_required_level": 2,
  "quality_score": null,
  "lineage": {"parent": null, "calibration_ref": null}
}
```

> 预算绝对值用 `PENDING_ENTERPRISE_SCALE` 占位，避免在研究仓库写入伪造“企业真值”。

---

## 9. 理论追踪矩阵（本文件覆盖项）

| 内容 | GA-1 锚点 | 本文件章节 | 工程组件 | 状态 |
|---|---|---|---|---|
| 参数基因字段集 | §10.2 | §3 | KE Genome Registry | Mapped（Draft） |
| 低客单 vs 中高客单 | §7.2 | §4.1, §5.2 | OFG, KE | Mapped |
| 种草 vs 收割 | §7.3 | §4.2, §6.3 | 场景 Agent, Risk | Mapped |
| 生命周期五阶段 | §7.4 | §4.3, §5.4, §6.2 | OFG, Risk, CBA | Mapped |
| 动态目标函数 | §8.2 | §5 | OFG | Mapped（权重数值 Proposed） |
| 稳定性优先 / NO_ACTION | §8.5 | §3.3.6, §6.3 | RE, SRA | Mapped |
| 调整响应窗口 | §8.6 | §3.3.6, §6.4 | RFE, LE | Mapped（数值 Pending） |
| 经验质量分 | §9.3 | §3.2, §7.2-S7 | KE, LE | Partial |
| 知识结晶 | §10.3 | §3, §8 | KE | Mapped |
| 跨计划学习 | §10.1 | §7 | LE | Mapped（流程） |
| 动态风险基线 | §11.1 | §6 | RKE | Mapped（数值 Proposed） |
| 自审批检查项 | §11.2 | §7.2-S8 | SRA | Mapped |
| Trust 权限门槛 | §6.7, §11.3, 架构 §7 | §3.2, §7.2-S9 | TE, SRA | Mapped |
| GA-INNOV-009 | §13 | 全文 | KE / GA2-T07 | 本文件将 Trace 中 Partial 推进为详设 Draft |

---

## 10. 待决问题

| ID | 问题 | 建议 | 阻塞谁 |
|---|---|---|---|
| GQ1 | 客单价带切分阈值如何定义？ | 企业类目分位数 + 人工确认；不写入理论 | 标定 S2 |
| GQ2 | 低客单种草、中高客单收割的指标序是否采纳 §5.2 Proposed 序？ | 评审确认后可进默认模板，保持 Proposed 直至 GA-3 | OFG |
| GQ3 | 权重衰减系数 `r` 与是否允许自由权重 | 先固定 ordinal decay，敏感性分析后调整 | OFG |
| GQ4 | `Campaign` 是否独立基因 vs Overlay | 建议 Overlay，避免 20→30 槽爆炸 | 目录结构 |
| GQ5 | 基因存储用文件树还是 DB | 第一轮文件树便于评审；Registry 可迁 DB（GA2-T04） | KE |
| GQ6 | 与 GA2-T04 Memory/Knowledge schema 的字段对齐 | 以 T04 为权威 schema，本文件字段作提案 | 联调 |
| GQ7 | 抖音维度是否与京东同构 | 目录同构；抖音字段与目的枚举后置细化 | Douyin Agent |
| GQ8 | 默认模板是否允许租户级覆盖写回 defaults/ | 否；仅写 `enterprise/`，defaults 变更走版本评审 | 治理 |
| GQ9 | `min_effectiveness_ratio` 绝对口径（ROI？得分？） | 与 Risk Engine 统一口径后回填 | RKE |
| GQ10 | 预标定样本最小 n | 统计功效评估后定；当前 Pending | S5–S7 |

---

## 11. 变更记录

| 日期 | 版本 | 变更 | 依据 |
|---|---|---|---|
| 2026-09-11 | v0.1 | 首次建立：对象模型、分类空间、目标权重模板、目录树、预标定流程、风险/频率 Proposed 区间 | GA-1 §7.2–7.4/8.2/10.2/11.1；架构 v0.1；Trace GA-INNOV-009 |

---

**Document Status:** Draft  
**Owner Review:** 待 Research Architect / Project Owner 评审  
**Next:** GA2-T04 schema 对齐；历史数据到位后执行 §7 预标定（需单独授权）
