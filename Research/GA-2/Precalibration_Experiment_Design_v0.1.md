# GA-2：Proposed 参数预标定实验设计（历史导出 / 模拟，非真实写）

**文档编号：** GA-2-PRECAL-001  
**任务编号：** GA2-T15  
**版本：** v0.1  
**状态：** Draft  
**阶段：** GA-2 Engineering Design（参数治理 / GA-DEC-004）  
**输入基线：** `Research/GA-1/GA-1_Theory_v1.0.md`（GA-1.0 / v1.0，Confirmed）  
**上游架构：** `Architecture_Overview_v0.2.md`（Confirmed，GA-DEC-004）  
**强关联（只读复用，不重复实现）：**  
- `Threshold_Calibration_Method_v0.1.md`（GA2-T14，TCAL）— 阈值清单、清洗/分层/稳健估计、CalibrationPatch、版本治理  
- `Parameter_Genome_Templates_v0.1.md`（GA2-T07）— Genome 对象与 20 槽位  
- `Shadow_Mode_Design_v0.1.md`（GA2-T11）— SM-M01…M10、隔离与防污染  
- `Forecast_Engine_Interface_v0.1.md`（GA2-T13）— 预测对象、置信度阈值、ForecastEvalRecord  
**授权依据：** `GA-DEC-003`（Accepted）+ `GA-DEC-004`（Accepted；**参数默认值一律 Proposed**）  
**作者角色：** Research Engineer 子代理（实验设计派生，不新增理论主张、不重复阈值清单）  
**约束：** 本文只定义**预标定实验设计**；不改 GA-1 / PROJECT_SPEC；不接真实写 API；不输出真实账户脚本；一切数值与阈值均为 **Proposed / Example-Only**；阈值字段语义与清单以 TCAL 为准，冲突时以 TCAL + GA-1 为准并修订本文。

---

## 0. 安全边界与范围声明（强制阅读）

### 0.1 与 GA2-T14（TCAL）的分工

| 维度 | TCAL（T14） | 本文（T15） |
|---|---|---|
| 回答的问题 | 阈值**怎么回填**（清单、字段、清洗、估计、Patch、版本） | 在**无真实写前提下**，如何用历史导出/模拟数据**评估 Proposed 参数是否可用** |
| 产出 | 方法论 + CalibrationPatch 骨架 | 实验分组、数据集/切分、泄漏防护、指标定义、统计原则、报告模板 |
| 阈值清单 | **权威入口** | **不重复枚举**；仅按实验组引用 TCAL ID（如 TC-R01、TC-Q02、TC-T05） |
| 执行前提 | 历史抽取需单独授权 | 实验可用：匿名化历史导出、Fixture、SIM/Shadow 隔离池；**禁止 live 写** |

**交叉引用约定（呼应 TCAL-Q9）：** T14=阈值回填方法；T15=实验与模拟设计。两文交叉引用，不互相复制清单。

### 0.2 本轮明确不做

| 项 | 说明 |
|---|---|
| 真实平台写操作 | 不调用任何改价/改预算/建计划 API；不提供可执行投放脚本 |
| 真实历史标定结果 | 不写入任何企业“已标定终值”；实验输出默认仍为 **Proposed** |
| 凭证与密钥 | 不创建、不示例、不落盘任何 AppKey / Token / Secret |
| 伪造企业真值 | 不用 SIM/Fixture 分布冒充企业历史；不用合成数据“证明” live 最优 |
| 自动升格 Proposed → Confirmed | 实验通过也不得自动升格；须人工评审 + 版本化决策（TCAL §8） |
| 修改 GA-1 / 架构主线 | 不修改理论、PROJECT_SPEC、Architecture v0.2 |
| 影子分升 live Trust | 实验若使用 Shadow Pool，结果不得写入 live Trust（SM §5/§7） |

### 0.3 本轮明确要做

1. 定义实验目标：评估哪些 Proposed 参数、在何种数据上、达到什么“可用”判据。  
2. 定义数据集设计：字段需求（引用 TCAL §3，不重复全表）、分层、时间切分、泄漏防护。  
3. 定义实验组：Genome 实例化、Risk/Trust 阈值敏感性、Forecast 置信度阈值。  
4. 定义指标：与 SM-M*、预测精度、门禁拒绝率、NO_ACTION 率的关系。  
5. 定义统计与最小样本量原则（**Proposed**，非最终功效结论）。  
6. 定义伦理/合规边界。  
7. 给出 calibration report 模板（预标定实验报告）。  
8. 列出待决问题。

### 0.4 一句话定位

> **预标定实验不是“跑一次调参赛”，而是在零真实写副作用的约束下，用可审计的对照设计回答：当前 Proposed 参数在历史/模拟分布上是否处于“可用区间”，以及哪些槽位必须维持 Prior。**

---

## 1. 实验目标

### 1.1 总目标

| 目标 ID | 目标 | 非目标 |
|---|---|---|
| PE-G1 | 在无真实写前提下，评估 GA-2 默认 Proposed 参数族（Genome / Risk / Trust / FE 置信度）的**可用性与脆弱点** | 不声称全局最优、不替代 GA-3 验证 |
| PE-G2 | 量化各参数族对 SM-M*、预测精度、门禁行为、NO_ACTION 率的**敏感方向与幅度** | 不把敏感性结果直接写成 ACTIVE 阈值 |
| PE-G3 | 识别“样本不足 / 结果不稳定 / 方向矛盾”的槽位，输出**维持 Prior 或收窄带宽**建议 | 不在 n 不足时输出段内独立终值 |
| PE-G4 | 产出可审计的预标定实验报告与 CalibrationPatch 候选包（status=PROPOSED） | 不跳过 TCAL S9 人工评审 |

### 1.2 “可用”的操作定义（Proposed）

参数在某槽位/实验组被判定为 **Usable（可用）** 当且仅当同时满足：

1. **证据充分：** `n_eff` 达到该实验类型的最小样本原则（见 §5）；CI 不因样本过宽而拒绝提案。  
2. **方向稳定：** 在时间切分的 holdout 或 bootstrap 重采样中，效应方向与“收紧/放宽”建议一致，无翻转。  
3. **约束投影合法：** 满足 TCAL §4.2-S7（硬红线、单调性、理论序、θ 顺序）。  
4. **门禁/决策可解释：** 不导致“硬红线仍 APPROVE”；误拒率可解释；NO_ACTION 不被系统性压成 0 或 1。  
5. **隔离合规：** 若使用非 LIVE 样本，证据在报告中显式标注 `origin_env`，且不进入 live Trust / live 主分位终值。

任一不满足 → 判定 **Not-Usable** 或 **Inconclusive**；输出“维持 Prior / 收窄区间 / 待补样本”而非“更优数值”。

### 1.3 分阶段实验阶梯（对齐 Shadow 升级阶梯）

```text
E0  数据可用性与泄漏审计（只读）
      → 字段齐套率、BDV 通过率、时间切分可行性、泄漏检查清单全绿
        │
E1  离线回放（历史导出 / Fixture）
      → Genome 实例化 + 门禁回放 + FE 回看；无状态推进写
        │
E2  阈值敏感性扫描（单参数族 / 单槽位）
      → Risk/Trust/FE 置信度 ± 档；输出敏感曲线与“可用区间”
        │
E3  Shadow / SIM 对照（隔离池）
      → SM-M* 反馈；仍不升 live Trust；结果仅作 Proposed 材料
        │
E4  预标定报告 + CalibrationPatch 候选（PROPOSED）
      → 进入 TCAL S9 评审队列；不自动 ACTIVE
```

**本设计覆盖 E0–E4 的实验契约；不授权任何 live 写或真实账户联调。**

---

## 2. 数据集设计

### 2.1 数据源类型与适用范围

| 数据源类型 | 代码 | 适用实验 | 权限 | 硬约束 |
|---|---|---|---|---|
| 历史只读导出（脱敏/匿名化） | `SRC-EXPORT` | E1 主集；分层分位；门禁回放 | 只读；租户内 | 不含写接口；字段映射须经 BDV 语义对齐 |
| Fixture / 合成场景库 | `SRC-FIXTURE` | E0 管道自检；边界案例 | 开发池 | **不得**用于“证明 live 最优”（TCAL §6.4） |
| Shadow / SIM 隔离池 | `SRC-SHADOW` | E3 反馈；冷启动对照 | 隔离池 | 不进 live Trust；不与 live 主集合并分位（SM §7.3 / TCAL §7.3） |
| Live-Read 平台只读（若已授权） | `SRC-LIVE-RO` | E1/E2 的真实轨迹对照 | 只读 | dry_run 恒 true；禁止 write |

> 默认主证据 = `SRC-EXPORT`（经 BDV 验证）。`SRC-FIXTURE` / `SRC-SHADOW` 只能作辅证或管道自检。

### 2.2 字段需求（引用权威，不重复全表）

字段字典以 **TCAL §3.2** 为权威入口。本实验在此之上增加**实验专用最小附录**：

| 附录字段 | 用途 | 来源 |
|---|---|---|
| `split_id` / `fold_id` | 时间切分与交叉验证索引 | 实验工作区生成 |
| `origin_env` | LIVE / SHADOW / SIMULATION / FIXTURE | RuntimeEnvelope（SM §3.4） |
| `experiment_arm` | 对应实验组/对照臂 ID | 实验编排 |
| `param_snapshot_id` | 回放时使用的 Proposed 参数包指纹 | Genome / Risk / TE 配置 |
| `forecast_bundle_id` / `forecast_eval_id` | FE 回看关联 | FE §6 |
| `gate_result` / `review_result` | 门禁回放结果 | Risk/Trust/SRA 回放 |
| `no_action_flag` | 是否输出 NO_ACTION / HOLD | RE 回放 |
| `leakage_flags[]` | 泄漏审计结果（见 §2.5） | E0 审计器 |

**齐套率门槛（Proposed）：** 进入 E1 主集的槽位，关键字段（分层键 + 动作幅度/频率 + 结果标签 + `origin_env`）齐套率 ≥ 0.95；低于门槛的槽位降为观察集，不进敏感性主结论。

### 2.3 分层设计（继承 TCAL S4 / Genome 20 槽）

实验分层键与 TCAL / Genome 一致，**不新增槽位空间**：

| 层级 | 键 | 实验用途 |
|---|---|---|
| 主槽位 | `price_band` × `plan_purpose` × `life_cycle_stage`（2×2×5=20） | Genome 实例化与分位估计的报告单元 |
| 风险子层 | `inventory_state`、R 档（R0–R4） | Risk 阈值敏感性分层 |
| 频率/目的子层 | `plan_mode`（seed/harvest/mixed） | 调整频率与 NO_ACTION 敏感性 |
| 活动子层 | `activity_phase`（无/预热/爆发/收尾） | **单独臂**，不与常态混合估主阈值（TCAL TC-O01） |
| 环境子层 | `origin_env` | live 主集 vs shadow 辅集硬隔离 |

**继承规则（同 TCAL）：** `n_segment < n_min_segment` → 不输出该段独立估计；标记 `sample_size_low`；使用父层分位 → 理论 Prior → 全局更保守值（三选一并记录）。

**活动 Overlay 实验原则：** Campaign 相关放宽幅度（TC-R10 等）必须独立 `calibration_version` 前缀，不与常态 patch 混报（TCAL-Q5）。

### 2.4 时间切分（防未来信息）

> 预标定是**时间序列决策参数**问题，禁止随机打乱切分作为主协议。

| 切分方案 | 结构 | 适用 | 备注 |
|---|---|---|---|
| **T-Holdout（主协议）** | 按日历时间：`train` 前段 → `valid` 中段 → `test` 后段 | E1–E2 主结论 | 比例 **Proposed**：60% / 20% / 20%；或按“一个完整大促周期 + 常态窗”边界切 |
| **T-Expanding** | 扩展窗回测：t1 训练评估 t1+1；滚动推进 | 稳定性与漂移 | 用于判断 patch 是否 `stale` 候选（TCAL §5.3） |
| **T-Blocked-Kfold** | 按周/旬分块，块内不随机、块间可轮换 | 小样本稳健 SE | 块大小 **Proposed**：7–14 日 |
| **事件窗隔离** | 活动窗单独成块；窗前窗后各留 buffer | Overlay 与爆发样本 | buffer **Proposed**：活动前后各 ≥1 个冷却周期 |

**硬规则：**

1. 同一 `plan_id` / `product_id` 的样本在 train/test 间按时间严格前后切分，禁止“后段样本进入前段估计”。  
2. 任何依赖未来统计量的特征（全局分位、跨窗归一化参数）只能用 train 段计算后再映射到 valid/test。  
3. 活动爆发窗、平台异常窗默认不进主阈值 train（对齐 TCAL §3.3 排除规则）。

### 2.5 泄漏防护清单（E0 强制审计）

| 泄漏 ID | 风险 | 检查 | 不通过处置 |
|---|---|---|---|
| PE-L01 | 未来标签泄漏 | train 截止时刻后产生的 outcome/回看结果不得进入 train 特征 | 剔除字段或重切分 |
| PE-L02 | 全局统计泄漏 | 分位/标准化仅用 train 重算 | 重跑变换 |
| PE-L03 | 同实体跨集泄漏 | 同 plan/product 的“后验质量分”回填到 train | 按时间切或按实体分组切（披露局限） |
| PE-L04 | 环境池泄漏 | `origin_env!=LIVE` 混入 live 主分位 / live Trust | 强制双池；审计 SM-M10 |
| PE-L05 | 活动窗污染常态 | 爆发样本抬高幅度/放宽 ROI | 独立 Overlay 臂；常态 train 剔除 |
| PE-L06 | 多重比较刷分 | 同一数据上反复扫阈值挑“最好看” | **预注册**实验组与主指标（见 §3.1）；探索性结果标 EXPLORE |
| PE-L07 | 只报成功计划 | 只用 Top-P 成功样本估“安全幅度” | 成功/失败联合入集（TCAL §5.2） |
| PE-L08 | 人工事后知道答案 | 用“后来运营怎么改”直接当标签而不定义窗口 | 必须预注册 `expected_response_window` 语义 |

**E0 产出：** `LeakageAuditReport`（通过/失败项、证据、修复动作）。任一 PE-L04/L01 失败 → 实验熔断，不得进入 E2。

### 2.6 样本纳入 / 排除（与 TCAL 对齐）

沿用 TCAL §3.3：`env!=LIVE` 默认不进 live 主集；BDV quarantined/FAIL 排除出主集；标签缺失过高仅观察；异常订单降权/winsorize；活动窗单独分层；平台异常窗不参与主蒸馏/主标定。  
**实验补充：** 排除计数必须写入报告 `excluded_summary`，禁止静默丢样本。

---

## 3. 实验组设计

> **预注册原则：** 每个实验在跑之前固定：主假设、主指标、参数臂、槽位范围、最小样本、熔断条件。探索性扫描结果标 `EXPLORE`，不得直接进入 CalibrationPatch 终值建议。

### 3.0 实验臂通用结构

```text
Experiment {
  exp_id,                     // PE-E##
  hypothesis,                 // 可证伪陈述
  target_class,               // GENOME | RISK_BASELINE | TRUST_SCORE | FORECAST_CONF
  param_refs[],               // 引用 TCAL ID / Genome 字段 / FE 对象 ID（不复制清单）
  arms[],                     // Prior 对照臂 + 变动臂
  segments[],                 // 槽位范围
  split_protocol,             // T-Holdout 等
  primary_metrics[],          // 预注册主指标
  guardrail_metrics[],        // 护栏：硬红线违反、SM-M10、误杀率
  min_n_principle,            // §5
  stop_rules[],               // 熔断
  output_patch_template       // TCAL CalibrationPatch
}
```

**对照臂默认：** `ARM-0 = 当前 Expert_Prior / Proposed 默认包`（不修改）。  
**变动臂：** 仅改变被测参数族，其余族冻结（避免 TCAL TC-O05 多族耦合噪声）。

---

### 3.1 实验组 A：Genome 实例化可用性

**目的：** 在历史导出上实例化 20 槽 Genome，检验“默认基因是否能区分成败模式、是否覆盖高频槽位、是否触发完整性校验失败”。

| 项 | 内容 |
|---|---|
| **假设（示例）** | H-A1：Expert_Prior 基因在多数主槽位上，其 `adjustment_policy` 与 `risk_baseline` 相对历史“无重大风险事件的成功动作”分布偏保守或偏激进，存在可报告的偏差方向。 |
| **方法** | E1 离线：对每个有样本槽位，将历史会话映射到最近 Genome 实例；回放“若采用该基因的幅度/频率/冷却约束，多少历史动作会被裁剪/拒绝”。 |
| **臂** | ARM-0 Prior 默认；ARM-1 仅放宽/收紧幅度族（TC-R01/02）；ARM-2 仅频率/冷却（TC-R03/04）；**一次只动一族**。 |
| **主指标** | 动作裁剪率、裁剪后 vs 历史实际幅度的分位差、槽位覆盖矩阵（Prior/可标定/样本不足） |
| **护栏** | 不得输出违反硬红线的实例；`seed_harvest_ratio` 等完整性规则失败率 |
| **输出** | 槽位覆盖矩阵 + 候选 Genome 字段 Proposed patch（引用 `genome_id`） |

**明确不做：** 不在此组直接把基因 `status` 升为 Calibrated；升 Calibrated 须走 Genome §7 + TCAL S9。

---

### 3.2 实验组 B：Risk / Trust 阈值敏感性

**目的：** 扫描 Risk 幅度/频率/窗口与 Trust 分带/迟滞，观察门禁行为与风险后验代理指标如何变化。

#### 3.2.1 Risk 族敏感性（引用 TCAL TC-R*）

| 项 | 内容 |
|---|---|
| **被测参数（引用）** | TC-R01/02 幅度上限；TC-R03 日内频率；TC-R04 响应窗口；TC-R07/08 成效比与日损；TC-R09 `risk_scale(R)` |
| **扫描设计** | 对每个被测标量：在 Prior 两侧取 **Proposed** 臂网格，例如 ±1 档相对变化或分位臂（p50/p75/p90），**一次一参** |
| **方法** | 历史动作回放：动作是否触发约束；被约束样本的事后“风险事件代理”（超损、异常归因、人工否决、R 档升级）发生率 |
| **主指标** | 门禁拒绝率（按 R 档）、被拒动作的事后风险代理率、幅度校准误差（对齐 SM-M08） |
| **护栏** | R4 语义不得被放宽；单调性：更高 R 档上限 ≤ 更低档；连续两期方向与建议相反 → 回退评审 |

#### 3.2.2 Trust 族敏感性（引用 TCAL TC-T*）

| 项 | 内容 |
|---|---|
| **被测参数（引用）** | TC-T01 权重；TC-T05 分带；TC-T06 升级附加条件；TC-T07 迟滞 k；TC-T08 惩罚上界 |
| **方法** | 用历史 `human_override` / 硬红线 / 否决事件作标签，回放 Trust Level 与门禁结果；统计误放行（应拦未拦）与误杀（应放未放）代理 |
| **主指标** | 误放行代理率、误杀代理率、分带边界抖动率（对齐 TC-T07）、SM-M06/M07 映射 |
| **护栏** | 实验**不**改写 live Trust 历史分轨迹；只评估规则包；影子信号不得计入 live 分（SM §7.3） |

**耦合控制：** A/B 组不得在同一报告里联合调参成“最优组合”；组合效应仅标 EXPLORE，供后续预注册。

---

### 3.3 实验组 C：Forecast 置信度阈值

**目的：** 评估 FE 各预测对象 Proposed 置信度门槛与 `overall_confidence` 对写动作资格、NO_ACTION 的影响（FE §3.3、§5.2 FR-I3、§7）。

| 项 | 内容 |
|---|---|
| **被测对象（引用 FE）** | 曲线类、`FC-ETA-BUDGET`、`FC-STAB-PLAN`、`FC-BURST-CAMPAIGN`、`FC-RISK-INVENTORY` 的置信度阈值；`overall_confidence` 低置信边界 |
| **数据** | 历史序列回放生成 ForecastBundle + 事后 `ForecastEvalRecord`（FE §6.2）；或既有 shadow 回看池 |
| **臂** | Prior 阈值；提高阈值（更严，更多 DEGRADED/HOLD）；降低阈值（更松，更多可写资格）— 数值网格 **Proposed**，预注册后扫描 |
| **主指标** | 分 horizon 的 `within_band`（SM-M03）、MAPE（SM-M04）、低置信子集 vs 高置信子集的误差差、被 FR-I3 拦下的动作占比 |
| **决策耦合指标** | 门禁拒绝率、NO_ACTION 率、误拒代理（人工认为该动但被置信度拦下） |
| **护栏** | 预测差时 **禁止**用放宽业务阈值掩盖（TCAL §6.3 SM-M03 规则）；先修 FE/BDV，阈值冻结 |

**FE-Q01 衔接：** 分位带首期用历史分位数校准的结论可作为 C 组输入；本文不实现分位回归。

---

### 3.4 实验组 D：组合门禁回放（薄）

**目的：** 在 A–C 单参结论稳定后，用“推荐收窄/放宽包”做一次**联合门禁回放**，只回答行为指标，不搜索新最优点。

| 项 | 内容 |
|---|---|
| **输入** | A–C 输出的 Proposed patch 候选（仍 PROPOSED） |
| **方法** | 同一 holdout 上回放完整 Risk×Trust×SRA 链；对比 ARM-0 |
| **主指标** | 总门禁拒绝率、NO_ACTION 率、SM-M01/02 代理、硬红线违反=0 |
| **约束** | D 组不得产生新的数值搜索；只能验证已预注册包的行为是否可接受 |

---

## 4. 指标体系

### 4.1 指标总图（与 SM-M* / FE / 门禁的映射）

> 不重复定义 SM-M* 全文；此处只定义**预标定实验如何消费/对齐**。

| 实验指标 ID | 名称 | 定义（实验语义） | 对齐 |
|---|---|---|---|
| PE-M01 | 动作方向一致率 | 回放建议方向 vs 人工/事后合理方向一致占比 | SM-M01 |
| PE-M02 | NO_ACTION 正确率 | HOLD 后窗口内指标未破阈比例 | SM-M02 |
| PE-M03 | 预测命中率 | 实际落 p20–p80 分位带比例 | SM-M03；FE `within_band` |
| PE-M04 | 预测 MAPE | 分 horizon 误差 | SM-M04 |
| PE-M05 | 干预提前量 | 相对事后拐点 lead time | SM-M05；TC-R04 |
| PE-M06 | 门禁通过率 | APPROVE / 候选总数 | SM-M06 |
| PE-M07 | 误拒代理率 | 人工/事后应做但 REJECT/HOLD | SM-M07 |
| PE-M08 | 幅度校准误差 | \|回放 Δ − 合理 Δ\| / 合理 Δ | SM-M08；TC-R01/02 |
| PE-M09 | 数据校验影响率 | 因 BDV 降级导致决策改变比例 | SM-M09 |
| PE-M10 | 隔离完整率 | 零 live 污染事件 | SM-M10；硬门槛 1.0 |
| PE-M11 | 门禁拒绝率（分 R 档） | 被约束/拒绝动作 / 候选动作 | Risk 族敏感性主指标 |
| PE-M12 | NO_ACTION 率 | HOLD/NO_ACTION / 全部决策 | 稳定性优先（理论 §8.5） |
| PE-M13 | 误放行代理率 | 应拦未拦（硬红线/高风险） | Trust 族 |
| PE-M14 | 槽位可标定率 | n_eff 达标且 CI 可接受的槽位 / 有样本槽位 | 覆盖矩阵 |
| PE-M15 | 约束裁剪率 | 因幅度/频率被裁剪的历史动作占比 | Genome A 组 |

### 4.2 主指标 vs 护栏指标

| 实验组 | 主指标（预注册） | 护栏（否决项） |
|---|---|---|
| A Genome | PE-M15、PE-M14 | 完整性校验失败；硬红线实例=0 但需可解释 |
| B Risk | PE-M11、PE-M08、PE-M07 | R4 放宽=0；单调性违反=0 |
| B Trust | PE-M13、误杀代理、分带抖动 | 不改 live 分轨迹 |
| C FE | PE-M03、PE-M04、低高置信误差差 | 预测差时业务阈值冻结 |
| D 组合 | PE-M06、PE-M12、PE-M01/02 | PE-M10=1.0；硬红线违反=0 |

### 4.3 与“可用判定”的关系

- 主指标落在预注册可接受带 **且** 护栏全过 → 可提交 `Usable` 建议（仍 PROPOSED）。  
- 主指标边缘或 CI 过宽 → `Inconclusive`：维持 Prior 或仅收窄区间。  
- 护栏失败 → `Not-Usable`：即使主指标漂亮也不得提案放宽。

**NO_ACTION 解释纪律（呼应 SM-R05）：** NO_ACTION 率升高不自动等于“更好”或“失能”；必须与 PE-M02（正确率）联合解读。实验报告禁止只报 NO_ACTION 率单指标。

---

## 5. 统计与最小样本量原则（全部 Proposed）

> 本节给出**原则与占位门槛**，不是已完成的功效分析结论。最终 `n_min` 须在首次 E0 数据盘点后由负责人修订（对齐 TCAL-Q1、Genome GQ10）。

### 5.1 效应与区间

| 原则 | 内容 |
|---|---|
| S1 | 主估计用**稳健分位 / 加权中位数**；避免均值被活动与大额订单绑架（TCAL §6） |
| S2 | 报告必须给出区间：bootstrap CI 或分位带；区间跨“无效应”或跨 Prior 边界 → 标 Inconclusive |
| S3 | 同一 plan/product 重复样本用聚类稳健 SE 或降权，防止刷 n |
| S4 | 多重比较：预注册主指标；探索网格结果必须标 EXPLORE 并校正声明 |
| S5 | 时间自相关：优先 T-Blocked / T-Holdout，禁止 i.i.d. 随机切分做主结论 |

### 5.2 最小样本量原则（Proposed 占位）

| 场景 | 最小 n 原则（Proposed） | 说明 |
|---|---|---|
| 分位估计（幅度/频率） | 槽位内有效动作样本 `n_eff ≥ 30`；否则继承 Prior | 对齐 Trust `n_min` 量级占位；可修订 |
| 比率类（拒绝率/NO_ACTION 正确率） | 可判定事件 `n ≥ 50`；或相对误差目标 ±10pp 的粗算需求取大者 | 与 SM 升权材料 n≥50 对齐（SM §4.4/§7.2） |
| 预测回看（within_band / MAPE） | 每 horizon 至少 `n_horizon ≥ 30` 条独立 ForecastEvalRecord | 不足则只报方向不报阈值提案 |
| 敏感性曲线 | 臂网格每臂 `n_eff` 达同上；否则只做单侧收紧方向（更保守） | 放宽方向需要更高证据（TCAL §6.3） |
| Trust 误放行/误杀 | 标签事件（否决/硬红线）`n_label ≥ 20` 每主槽位或合并父层并披露 | 稀疏维标 sparse，不硬估 |

### 5.3 熔断与停止规则

| 规则 | 触发 | 动作 |
|---|---|---|
| PE-S01 | PE-M10 < 1.0（隔离失败） | **立即停标定/停实验**；修复防污染 |
| PE-S02 | 泄漏审计 PE-L01/L04 失败 | 熔断 E2；回到 E0 |
| PE-S03 | 关键决策使用 BDV FAIL 数据 | 熔断该实验组 |
| PE-S04 | 连续两期敏感方向与 Proposed 修正建议相反 | 回退评审；冻结放宽 |
| PE-S05 | 主指标 CI 宽度超过预注册上限 | 不输出 new_value；维持 Prior |
| PE-S06 | 护栏指标任一硬失败 | 整包 Not-Usable，即使单参好看 |

### 5.4 功效与计算（后置，不阻塞本文）

完整 power analysis（效应量、α、1−β、多重校正）属实现期任务；本文只要求：**任何“可用”提案必须披露 n_eff、CI、切分协议**。计算工具/脚本不绑定技术栈（TCAL-Q7）。

---

## 6. 伦理 / 合规边界

| ID | 边界 | 实验要求 |
|---|---|---|
| PE-E01 | 不触碰真实投放 | 无 write API、无可执行改参脚本、无 dry_run=false 路径 |
| PE-E02 | 不伪造企业真值 | SIM/Fixture 结果必须标 `origin_env`；不得写入“企业已验证”表述；预算绝对值用 `PENDING_ENTERPRISE_SCALE` |
| PE-E03 | 不把影子当 live 证据 | Shadow/SIM 不进 live Trust、不晋升 Rule/Genome（SM §5.4 特批除外且需负责人） |
| PE-E04 | 数据最小化与脱敏 | 历史导出优先脱敏；企业明细不提交研究仓库默认树（Genome §8） |
| PE-E05 | 可审计 | 每个实验有 exp_id、参数快照、切分、排除计数；报告可复现 |
| PE-E06 | 人工否决保留 | 实验产物不得表述为“已授权自动执行” |
| PE-E07 | 理论优先 | 任何与 GA-1 冲突的“更优”实验结论 → 改工程文档或否决，不改理论 |
| PE-E08 | 租户隔离 | 默认租户内实验；不合并跨租户数值（TCAL-Q2） |

---

## 7. 产出物：Calibration Report 模板（预标定实验）

> 文件名建议：`enterprise/{tenant}/calibration_reports/{yyyymmdd}_precal_experiment_{exp_batch_id}.md`  
> 研究仓库仅保留**空白模板**与 Example-Only 骨架，不提交真实租户结果。

### 7.1 报告模板结构

```markdown
# 预标定实验报告（模板）

- report_id: PRECAL-RPT-{tenant}-{yyyymmdd}-{seq}
- experiment_batch_id: PE-BATCH-…
- calibration_version_candidates: [CAL-…-PROPOSED]
- runtime_envelope_root: { env, mode, dry_run: true }
- status: DRAFT_EXPERIMENT_RESULT | PROPOSED_FOR_REVIEW
- explicit_non_claim: 一切数值为实验估计；非 Confirmed；未触达真实写

## 1. 范围与预注册摘要
- 实验组列表（exp_id、hypothesis、主指标、臂）
- 槽位范围；排除的活动/异常窗
- 预注册时间：____；偏离预注册的项：____（必须披露）

## 2. 数据与切分
- 数据源类型与 origin_env 比例
- 时间窗：train / valid / test（或 expanding 定义）
- 分层覆盖矩阵：20 槽 × n_eff × 状态（Prior / 可标定 / sample_size_low）
- excluded_summary: { bdv_reject, activity, anomaly, env_filter, label_missing }
- LeakageAuditReport 摘要：PE-L01…L08 通过情况

## 3. 实验组结果
### 3.x exp_id
- 臂定义（仅引用 TCAL/Genome/FE ID，附 param_snapshot_id）
- 主指标表（点估计 + CI）
- 护栏结果
- 敏感方向描述（收紧/放宽/不确定）
- 判定：Usable | Inconclusive | Not-Usable

## 4. 与 SM-M* / FE / 门禁的关系
- PE-M01…M15 摘要表
- FE 回看：分 horizon within_band / MAPE
- 门禁：拒绝率（分 R 档）、NO_ACTION 率 + PE-M02 联合解读
- 隔离：PE-M10；P-01…P-05 审计

## 5. CalibrationPatch 候选（仍 PROPOSED）
- 每条引用 TCAL §4.2 S8 结构：
  { calibration_id, target_class, segment, field, old_value, new_value,
    estimator, evidence_refs, excluded_summary, confidence, status: PROPOSED }
- 明确：未评审不得装载为 ACTIVE

## 6. 未决槽位与风险声明
- sample_size_low 槽位列表与继承选择
- 分布漂移 / 活动季标记
- 已知局限（选择偏差、Fixture≠真实、反事实不可识别等）

## 7. 建议决策
- Accept / Accept-with-narrower-band / Reject / Defer
- 需人工评审队列：Research Architect / 负责人 / SRA
- 是否触发重跑 E0/E2

## 8. 附件
- exp 配置快照、切分索引、审计日志摘要、CHANGELOG
```

### 7.2 报告验收检查（与 TCAL S9 对齐）

| 检查 | 通过条件 |
|---|---|
| R-01 | 无 live 写痕迹；`dry_run`/env 声明完整 |
| R-02 | 泄漏审计无未修复的 L01/L04 |
| R-03 | 所有 new_value 带 CI 与 n_eff |
| R-04 | 硬红线与单调性投影已做 |
| R-05 | 未把 shadow 证据写成 live 终值 |
| R-06 | 偏离预注册部分已披露 |
| R-07 | 未决槽位未被编造段内估计 |

---

## 8. 与既有文档的接口

| 上游/下游 | 本文关系 |
|---|---|
| TCAL（T14） | 复用阈值 ID、分层、稳健估计、Patch 结构、禁止事项；不重复清单 |
| Genome（T07） | 实例化对象与 20 槽；预标定流程 S1–S10 与本文 E 阶梯互补 |
| Shadow（T11） | SM-M* 消费方式、隔离、升权边界；E3 只用隔离池 |
| FE（T13） | ForecastEvalRecord、置信度阈值、FE-Q01 分位带校准输入 |
| Gate Playbook（T12） | 门禁回放语义与 REJECT 可解释性 |
| GA-3 | 本文不执行 GA-3；只预留对照指标与样本组织 |

---

## 9. 待决问题

| ID | 问题 | 建议 | 阻塞 |
|---|---|---|---|
| PE-Q01 | 历史导出最小可用时间跨度？ | 优先覆盖常态 + ≥1 次大促；否则只做管道与 Prior 稳定性 | E0 |
| PE-Q02 | 主切分用日历比例还是业务事件边界？ | 首期 T-Holdout 按日历 60/20/20；大促年改为事件边界版本 | E1 |
| PE-Q03 | n_min 统一 30/50 还是按槽位功效？ | 先统一保守占位 + 披露 CI；E0 盘点后修订 | §5 |
| PE-Q04 | 敏感性网格宽度与臂数上限？ | 预注册每参 ≤5 臂；防多重比较 | E2 |
| PE-Q05 | Trust 标签噪声（人工否决不一致）如何降权？ | 分层专家抽检；不一致样本进观察不进主拟合 | B-Trust |
| PE-Q06 | FE 置信度与业务阈值谁先冻结？ | 预测不达标时业务阈值冻结（TCAL §6.3）；先修 FE/BDV | C 组 |
| PE-Q07 | 跨租户是否允许方法共享而不合并数值？ | 是；默认租户内（TCAL-Q2） | 治理 |
| PE-Q08 | 实验管道技术栈（Notebook vs 服务）？ | 方法与报告模板先行；实现后置（TCAL-Q7） | 实现 |
| PE-Q09 | D 组联合包是否需要独立 calibration_version？ | 是；与单参 patch 分离，便于回滚 | 版本 |
| PE-Q10 | 何种结果才允许提交“放宽”而非仅“收紧”？ | 双证据：holdout 稳定 + 护栏全过 + 人工评审；影子单独不够 | 评审 |

---

## 10. 变更记录

| 日期 | 版本 | 变更 | 依据 |
|---|---|---|---|
| 2026-09-11 | v0.1 | 首次建立预标定实验设计：目标与可用定义、数据集与泄漏防护、实验组 A–D、指标与 SM-M* 映射、统计与最小样本原则、伦理边界、报告模板、待决问题 | GA2-T15；TCAL T14；Genome T07；Shadow T11；FE T13；GA-DEC-004 |

---

**Document Status:** Draft  
**Next Stage:** Research Architect / 负责人评审 → 修订 v0.2；真实历史导出实验执行需单独授权  
**Explicit Non-claim:** 一切数值、门槛与网格均为 Proposed / Example-Only；未运行真实账户或真实历史标定；未修改 GA-1 / PROJECT_SPEC；未接真实写 API；实验结果不得自动升格 Confirmed，也不得直接提升 live Trust。
