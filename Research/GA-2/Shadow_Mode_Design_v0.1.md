# GA-2：Shadow Mode（影子运行）设计稿

**文档编号：** GA-2-SHADOW-001  
**任务编号：** GA2-T11  
**版本：** v0.1  
**状态：** Draft  
**阶段：** GA-2 Engineering Design  
**输入基线：** `Research/GA-1/GA-1_Theory_v1.0.md`（GA-1.0 / v1.0，Confirmed）  
**关联架构：** `Architecture_Overview_v0.2.md`（Confirmed，GA-DEC-004）  
**强关联：** `JD_Adapter_Interface_v0.2.md`、`Risk_Trust_SelfReview_v0.1.md`、`Memory_Knowledge_Boundary_v0.1.md`  
**授权依据：** `GA-DEC-003`（Accepted）+ `GA-DEC-004`（Accepted，主线冻结）  
**作者角色：** Research Engineer 子代理（工程派生，不新增理论主张）  
**约束：** 本文仅为影子运行设计契约；**不含真实写操作、无可执行投放脚本、无任何凭证**；所有阈值与指标默认 `Proposed`；与理论冲突时以 GA-1 为准并修订本文。

---

## 0. 安全边界与范围声明（强制阅读）

### 0.1 本轮明确不做

| 项 | 说明 |
|---|---|
| 真实平台写操作 | 不调用任何真实投放/改价/改预算/建计划接口 |
| 凭证与密钥 | 不创建、不示例、不落盘任何 AppKey / Token / Secret |
| 可执行投放脚本 | 不提供任何可对真实广告账户产生副作用的脚本或命令 |
| 反事实“完美复原”主张 | 不声称影子决策可被反事实证明为“必然成功” |
| Trust 自动升权 | 影子运行结果**不得**直接把 Trust Level 升到可写档（见 §7） |
| Memory/Knowledge 企业级污染 | `env=shadow` 的回执/经验默认隔离，不得晋升企业规则（见 §5） |

### 0.2 本轮明确要做

1. 定义 Shadow Mode 的目标、四运行模式边界与权限矩阵。  
2. 定义只读数据通路与决策“记账但不外发”的门禁语义。  
3. 定义 Shadow Packet（影子决策包）契约与对照评估方法。  
4. 定义环境标签与 Learning 过滤规则，防止 SIMULATION/SHADOW 回执污染 Memory/Learning。  
5. 给出京东第一验证场的最小影子任务清单。  
6. 给出退出影子 / 升级写权限的条件（Trust + 验证指标，均为 Proposed）。  
7. 给出风险局限与理论追踪。

### 0.3 与 JD Adapter 风险的对齐声明

`JD_Adapter_Interface_v0.1.md`（历史，已被 v0.2 承接）已在待决问题 **JD-Q10** 标记：  
> ActionReceipt 在 SIMULATION 下如何避免污染 Memory？——`source=SIMULATION` 标记，Learning 默认降权或隔离池。

本文将该风险升级为 **Shadow Mode 的一等硬约束**：任何非 LIVE 环境产生的动作回执、经验候选与信任信号，必须携带环境标签，并默认进入隔离/降权路径，**禁止静默混入 live 语义的 Memory→Learning→Knowledge 主链**。

---

## 1. Shadow Mode 目标

### 1.1 一句话目标

> 在**不产生任何真实投放副作用**的前提下，完整演练 Growth Agent 的决策闭环（感知→校验→预测→推理→门禁→记账），并系统评估：**若该决策被执行，预测与决策质量会达到什么水平**。

### 1.2 目标拆解

| 目标 ID | 目标 | 非目标（明确排除） |
|---|---|---|
| SM-G1 | 验证 **预测质量**（走势 / 预算寿命 / 稳定性 / 爆发概率） | 不追求平台侧真实调参反馈 |
| SM-G2 | 验证 **决策质量**（动作选择、幅度、时机、NO_ACTION 比例是否合理） | 不证明反事实必然成功 |
| SM-G3 | 验证 **门禁闭环**（Risk / Trust / Self-review / Adapter G-01–G-09 可运行且可审计） | 不解锁写权限 |
| SM-G4 | 验证 **数据校验链**（BDV 偏差是否被正确识别并影响决策） | 不替代真实数据接入评审 |
| SM-G5 | 为 GA-3 预留可测验证钩子（指标定义、对照窗口、样本组织） | 不在本阶段执行 GA-3 实验 |
| SM-G6 | 建立 **环境隔离与学习防污染**机制 | 不把影子经验当作企业知识资产 |

### 1.3 判断准则（什么算 Shadow Mode 做成了）

1. **可重放：** 同一 `state_digest` + 同一知识/参数版本，影子决策应可复现（或可解释地随机）。  
2. **可审计：** 每个影子决策都有完整 Decision/Shadow Packet 与门禁痕迹。  
3. **可对照：** 能回答“影子建议 vs 实际人工/既有投放结果，差在哪里”。  
4. **零副作用：** 对平台状态、真实账户、企业规则库均无可写变更。  
5. **零污染：** 影子回执不进入 live Trust 计分、不晋升 Rule/Strategy/Genome。

---

## 2. 运行模式对比与权限说明

### 2.1 四模式总览

```text
┌──────────────────────────────────────────────────────────────────────┐
│  Mode-A  Live-Read          只读真实/半真实数据；不产出决策动作         │
│  Mode-B  Shadow-Decide      只读数据 → 完整决策与门禁 → 记账，不外发   │
│  Mode-C  Shadow-Execute-Sim 决策 + 本地模拟回执/状态机，仍不触平台写   │
│  Mode-D  Live-Write         真实写路径（本轮禁止；单独授权后才可进入）  │
└──────────────────────────────────────────────────────────────────────┘
   本设计默认覆盖：A / B / C
   本设计只预留：  D 的升级门禁与授权条件
```

### 2.2 模式定义

| 模式 | 代号 | 数据来源 | 是否产出动作 | 动作是否外发 | 回执来源 | Memory/Learning 语义 |
|---|---|---|---|---|---|---|
| Live-Read | `MODE_READ` | 平台只读 / Fixture / 历史导出 | 否（仅状态与预测） | 否 | 无动作回执 | 读路径允许；无动作样本 |
| Shadow-Decide | `MODE_SHADOW_DECIDE` | 同上（只读） | 是（Shadow Packet） | **否** | 门禁记账回执（`simulated`） | 隔离池；**禁止晋升企业规则** |
| Shadow-Execute-Sim | `MODE_SHADOW_EXEC_SIM` | 只读 + 本地状态机/反事实模型 | 是 | **否** | 模拟 ActionReceipt | 隔离池；可做内部校准，不可写 Trust live 分 |
| Live-Write | `MODE_LIVE_WRITE` | 真实读 + 真实写 | 是 | 是 | 平台真实回执 | 主链；须 Trust + 人工/决策授权 |

### 2.3 权限矩阵（权限说明）

对齐 `Risk_Trust_SelfReview_v0.1.md` Trust Level 0–5 与 `JD_Adapter_Interface` `dry_run`/Runtime mode：

| 能力 | MODE_READ | MODE_SHADOW_DECIDE | MODE_SHADOW_EXEC_SIM | MODE_LIVE_WRITE |
|---|:---:|:---:|:---:|:---:|
| 平台只读资源（RO-*） | ✅（需数据源授权） | ✅ | ✅ | ✅ |
| 组装 BusinessState / 触发 FE | ✅ | ✅ | ✅ | ✅ |
| Reasoning 产出候选动作 | ❌ | ✅ | ✅ | ✅ |
| Risk/Trust/Self-review 门禁跑通 | ❌ | ✅ | ✅ | ✅ |
| Adapter `write(dry_run=true)` 记账 | ❌ | ✅（强制） | ✅（强制） | 可选（预演） |
| 本地模拟状态推进 / 反事实 rollout | ❌ | ❌ | ✅ | ✅（真实结果） |
| 真实平台 `write(dry_run=false)` | ❌ | ❌ | ❌ | 需 MODE 授权 + Trust 达标 |
| 影子样本写入 Shadow Pool | — | ✅ | ✅ | ❌（应写主链） |
| 影子样本驱动 Trust 升权 | ❌ | ❌ | ❌ | 仅 LIVE 样本 |
| 影子经验晋升 Rule/Strategy/Genome | ❌ | ❌ | ❌ | 须 KE 治理 + 负责人特批 |

**硬约束（全模式）：**

1. 本轮任何部署的默认模式必须是 `MODE_READ` 或 `MODE_SHADOW_DECIDE`；`MODE_SHADOW_EXEC_SIM` 需显式开启；`MODE_LIVE_WRITE` 必须未装配或硬失败。  
2. Adapter 对非 LIVE 模式强制 `dry_run=true`（对应 JD 接口 G-07）。  
3. `CredentialProvider` 在非 LIVE 模式必须拒绝提供真实凭证。  
4. 任何模式不得绕过 Self-review；任何模式不得绕过 Risk 硬红线。

### 2.4 模式选择原则

| 场景 | 建议模式 |
|---|---|
| 只校验 BDV / 只跑 Forecast，不讨论动作 | MODE_READ |
| 跑完整决策闭环、产出可审计影子动作、做人工对照 | MODE_SHADOW_DECIDE（默认影子档） |
| 需要“若执行后若干小时走势”的局部反事实推演 | MODE_SHADOW_EXEC_SIM（隔离加强） |
| 真实账户调参 | MODE_LIVE_WRITE（本轮禁止） |

---

## 3. 数据通路（只读拉取 → … → Shadow Packet）

### 3.1 端到端通路图

```text
[平台/ Fixture / 历史导出]
        │  只读 ResourceQuery（dry_run 恒 true）
        ▼
Platform Adapter (RO)
        │  RawPlatformPayload / FixturePayload
        ▼
Business Data Validation (BDV)
        │  ValidatedMetricSet + ValidationReport
        ▼
Business State Assembler (STATE)
        │  BusinessState（confidence / gap_flags）
        ▼
Forecast Engine (FE)
        │  ForecastBundle（走势/预算寿命/稳定性/爆发概率）
        ▼
Reasoning Engine (RE)
        │  候选动作 + 假设 + 预期窗口 + NO_ACTION 候选
        ▼
Risk Engine → Trust Engine → Self-review Agent
        │  门禁结果（APPROVE/REVISE/HOLD/REJECT/ESCALATE）
        │
        │  ★ 关键分叉：Shadow Gate ★
        │    if runtime.mode != LIVE:
        │         记账（Shadow Packet + TRACE）并 STOP
        │         不调用任何真实 write
        │    else:
        │         进入 Mode-D（本轮禁止）
        ▼
Shadow Packet Store（隔离池）
        │
        ├── 对照评估管道（§4）
        └── Shadow Metrics / GA-3 验证钩子
```

### 3.2 分段职责与约束

| 段 | 组件 | Shadow 下的特殊约束 |
|---|---|---|
| 1 | Adapter RO | 只允许 RO-* 能力；分页/限流元数据必须保留；`validation_state` 初始为 `UNVALIDATED` |
| 2 | BDV | 与 live 同一套校验规则；禁止因为是 shadow 就伪造 `PASS` |
| 3 | STATE | 缺失源必须打 `gap_flag`；`ready_for_forecast=false` 时 Reasoning 最多 HOLD |
| 4 | FE | 输入必须引用 `validated_id`，禁止引用未校验 snapshot |
| 5 | RE | 允许完整候选集（含 NO_ACTION）；必须写 observation→hypothesis |
| 6 | 门禁链 | Risk/Trust/Self-review **原样执行**；shadow 不是“跳过门禁的捷径” |
| 7 | Shadow Gate | 在 Adapter 写路径前强制分流：记账后终止外发 |
| 8 | Shadow Packet | 落入隔离存储；带 `env=shadow` / `mode` / `source` 标签 |

### 3.3 Shadow Gate（记账但不外发）语义

```text
ShadowGate.evaluate(decision, runtime) -> {
  env: SHADOW | LIVE,
  mode: MODE_READ | MODE_SHADOW_DECIDE | MODE_SHADOW_EXEC_SIM | MODE_LIVE_WRITE,
  allow_platform_write: bool,          // 非 LIVE 恒 false
  accounting_required: bool,           // shadow 必须 true
  receipt_policy: SIM_ONLY | PLATFORM,
  learning_pool: SHADOW_POOL | LIVE_POOL,
  trust_update_allowed: bool           // shadow 恒 false
}
```

**行为契约：**

1. `allow_platform_write=false` 时，JDA/Adapter **不得**发起任何平台副作用；只生成 `SimulatedActionReceipt`。  
2. `SimulatedActionReceipt.status` 必须能区分：`GATE_APPROVED_NOT_SENT`（门禁过但未外发）、`GATE_REJECTED`、`SIMULATED_APPLIED`（仅 EXEC_SIM）。  
3. 禁止把 `SimulatedActionReceipt` 表述为“平台已执行”。  
4. 失败/拒绝同样记账：影子 REJECT/HOLD 是有价值的门禁样本。

### 3.4 最小字段：影子回执与隔离标记

在 `ActionReceipt` 基础上扩展环境元数据（与 JD-Q10 对齐）：

```text
RuntimeEnvelope {
  env: enum { LIVE, SHADOW, SIMULATION, FIXTURE }
  mode: enum { MODE_READ, MODE_SHADOW_DECIDE, MODE_SHADOW_EXEC_SIM, MODE_LIVE_WRITE }
  adapter_runtime: enum { FIXTURE_ONLY, SIMULATION, SANDBOX_LIVE, LIVE }
  dry_run: bool
  receipt_source: enum { PLATFORM, GATE_ONLY, LOCAL_SIM, FIXTURE }
  learning_pool: enum { LIVE_POOL, SHADOW_POOL, DROPPED }
  trust_credit_allowed: bool
  captured_at: timestamp
}
```

**不变量：**

- `env != LIVE` ⇒ `learning_pool != LIVE_POOL`  
- `env != LIVE` ⇒ `trust_credit_allowed=false`  
- `dry_run=true` 在 MODE_SHADOW_DECIDE / MODE_SHADOW_EXEC_SIM 中强制成立

---

## 4. 与真实经营的对照评估设计

> 核心问题：影子决策没有真实执行结果，如何衡量“若执行会怎样”？

### 4.1 对照原则

1. **不主张完美反事实。** 影子评估是“决策质量代理指标”，不是因果证明。  
2. **优先用真实发生的经营轨迹作参照系**（人工操作结果、既有投放自然演化），而不是凭空仿真。  
3. **分三层证据：** 决策合理性层 → 预测一致性层 → 轨迹相似层（置信递减）。  
4. **所有对照结论标记为 `PROPOSED`，不得直接改 Trust/Risk 阈值。**

### 4.2 三层对照评估

#### L1 决策合理性对照（最强可操作、无需反事实引擎）

| 方法 | 说明 | 输出 |
|---|---|---|
| 人工对照集 | 选取已有人工/运营已处理的事件窗口，输入 shadow 只读状态，比较 shadow 建议 vs 人工实际动作 | 一致率、方向一致率、幅度差、NO_ACTION 吻合 |
| 专家抽检 | 负责人对 Shadow Packet 抽样评分（合理/勉强/错误） | 合理率、错误类型分布 |
| 门禁一致性 | 同一动作在不同 Risk/Trust 版本下的 APPROVE/REJECT 稳定性 | 门禁抖动率 |

#### L2 预测一致性对照（利用 FE 本身）

| 方法 | 说明 | 输出 |
|---|---|---|
| 事后校准 | 用 T+1…T+n 真实只读指标回看当时 Forecast | MAE/MAPE、分 horizon 准确率、区间覆盖率 |
| 决策触发是否“预对了” | 影子若建议干预，当时预测的恶化/放量窗口是否事后命中 | 触发精度/召回、提前量分布 |
| NO_ACTION 是否正确 | 影子选 HOLD 时，事后指标是否仍在可接受带内 | NO_ACTION 正确率 |

#### L3 轨迹相似 / 局部反事实（仅 MODE_SHADOW_EXEC_SIM，最弱）

| 方法 | 说明 | 输出 |
|---|---|---|
| 带约束 rollout | 用历史相似窗口或本地状态机，推演“动作后 k 步”指标带 | 相对基线的带状改善估计 |
| 邻近计划对照 | 同类计划未干预 vs 影子建议干预的自然对照（准实验） | 差分指标（谨慎解释） |
| 敏感性扫描 | 动作幅度 ±1 档的预测响应 | 是否存在过度干预 |

**L3 局限必须写进评估报告：** 存在选择偏差、并发干扰、平台系统学习打断不可建模等问题；L3 结论不得单独作为升权证据。

### 4.3 对照评估流水线

```text
ShadowPacket(i) at t0
    │
    ├─► 预注册对照：写下 expected_response_window / 预期方向
    │
    ▼
等待真实只读轨迹（t0 + window）
    │
    ▼
重新拉取 RO-MET-* + BDV（env 可以是 LIVE_READ，但评估产物仍标 shadow-eval）
    │
    ▼
Compare {
  human_action?, forecast_error, direction_hit, amplitude_gap,
  no_action_verdict, gate_consistency, data_quality_flags
}
    │
    ▼
ShadowEvalReport（进入 Shadow Pool；不写 live Trust）
```

### 4.4 评估指标（全部 Proposed）

| 指标 ID | 名称 | 定义草案 | 默认观察窗（Proposed） |
|---|---|---|---|
| SM-M01 | 动作方向一致率 | shadow 方向（↑/↓/HOLD）与人工/事后合理方向一致占比 | 事件级 |
| SM-M02 | NO_ACTION 正确率 | HOLD 后窗口内指标未破阈的比例 | 随 plan_mode |
| SM-M03 | 预测命中率 | 事后落在预测分位带的比例 | 1h / 6h / 24h / 7d |
| SM-M04 | 预测 MAPE | 分 horizon 误差 | 同上 |
| SM-M05 | 干预提前量 | 相对事后确认拐点的 lead time | 事件级 |
| SM-M06 | 门禁通过率 | APPROVE / 总候选 | 周 |
| SM-M07 | 门禁误拒代理 | 人工认为应做但 shadow REJECT/HOLD | 周抽检 |
| SM-M08 | 幅度校准误差 | \|shadow Δ − 合理 Δ\| / 合理 Δ | 动作级 |
| SM-M09 | 数据校验影响率 | 因 BDV 降级导致决策改变的比例 | 周 |
| SM-M10 | 隔离完整率 | 零 live 污染事件 | 连续日 |

**阈值建议（Proposed，非理论结论）：**

- 进入“考虑升权评审”的粗门槛草案：`SM-M01 ≥ 0.7`、`SM-M02 ≥ 0.8`、`SM-M03(24h) ≥ 0.6`、`SM-M10 = 1.0`，且有效样本量 `n ≥ 50` 个可判定影子决策。  
- 上述数值仅为工程占位，须在影子运行首期后由负责人修订。

---

## 5. 环境标签与 Learning 过滤规则

> 本节直接回应硬约束 4 与 JD-Q10。

### 5.1 标签传播规则（强制）

1. 入口：Adapter / Fixture / 模拟器在首条 payload 上写入 `RuntimeEnvelope`。  
2. 中游：BDV/STATE/FE/RE/门禁 **原样透传** `env` / `mode`，禁止清洗。  
3. 出口：Memory 写入时，Episode / CausalRecord / ActionReceipt 必须保留 envelope。  
4. 不变量：任何组件不得把 `env∈{SHADOW, SIMULATION, FIXTURE}` 的对象改写为 `LIVE`。

### 5.2 Learning 过滤矩阵

| 产物 | env=LIVE | env=SHADOW | env=SIMULATION | env=FIXTURE |
|---|---|---|---|---|
| TRACE / 审计日志 | 主链 | **隔离池（保留）** | 隔离池 | 开发池 |
| CausalRecord / Episode | 主链 | 隔离池 | 隔离池 | 开发池 |
| Experience Candidate | 可进 LE 主蒸馏 | **默认不进主蒸馏**；可进 shadow-only 蒸馏 | 同左 | 否 |
| Rule / Strategy / Genome 晋升 | 需 KE 治理 | **禁止自动晋升** | **禁止** | **禁止** |
| Trust Score 更新 | 允许 | **禁止入 live 分** | **禁止** | **禁止** |
| Risk Baseline Patch | 可 PROPOSED→确认 | 仅可产生“影子观察建议”，不写入 baseline_version | 同左 | 否 |
| Failure Pattern | 主链强制入库 | 影子失败单独标注，不与 live 失败混计 | 同左 | 开发用 |
| FE 校准样本 | 主 | 可作为“只读预测校准”输入（标注来源） | 谨慎，默认否 | 否 |

### 5.3 过滤伪逻辑（非实现代码）

```text
on_memory_write(obj):
  obj.envelope = current_runtime_envelope   # 必填
  if obj.envelope.env != LIVE:
      obj.learning_pool = SHADOW_POOL
      obj.trust_credit_allowed = false
      obj.enterprise_rule_eligible = false

on_learning_distill(batch):
  main_batch = filter(batch, env==LIVE)
  shadow_batch = filter(batch, env in {SHADOW, SIMULATION})
  # main_batch → 正常 LE→KE
  # shadow_batch → ShadowOnly 蒸馏；产物默认 visibility=shadow_analytic
  # 任何 shadow 产物进入企业规则，必须走负责人特批评估（§5.4）

on_trust_update(signal):
  if signal.envelope.trust_credit_allowed == false:
      record(signal, pool=SHADOW_POOL)
      return  # 不更新 TS / Level
```

### 5.4 特批升级通道（env=shadow → 企业规则）

默认**不允许**。若负责人认为某条影子经验具备企业规则价值，必须满足：

1. 单独立项评估记录（新 Decision/GA-DEC 或评审纪要）；  
2. 提供 **live 只读证据** 或 **人工对照 L1 高置信证据**，不能只靠 SIM rollout；  
3. Knowledge Engine 正式晋升流程（质量分、版本、可回滚）；  
4. 明确标注 `origin_env=shadow` 与迁移依据；  
5. 负责人显式批准后，才允许写入 Rule/Strategy/Genome。

### 5.5 防污染验收检查（工程自检清单）

| 检查 | 通过条件 |
|---|---|
| P-01 | Shadow Packet 存储与 live Memory 存储物理/逻辑隔离可配置 |
| P-02 | Trust 更新接口拒绝 `trust_credit_allowed=false` 的样本 |
| P-03 | KE 晋升接口拒绝 `env!=LIVE` 且无特批单号的候选 |
| P-04 | 日志中 `simulated` 回执不得出现 “platform accepted/成功投放” 文案 |
| P-05 | 抽样审计 0 条 live 规则引用 shadow-only 证据（无特批） |

---

## 6. 京东场景最小影子任务清单

> 第一验证场 = 京东广告。任务均可在 Fixture / 历史导出 / 只读状态下完成。

### 6.1 任务总表

| 任务 ID | 名称 | 计划类型 | 主能力链路 | 成功判据（Proposed） | 依赖 Fixture/数据 |
|---|---|---|---|---|---|
| SM-JD-01 | 种草获量下滑干预 | SEEDING | RO-MET-01/03 → BDV → FE → RE → 门禁 | 能在下滑拐点前给出“干预 or HOLD”且方向事后可核 | FX-01 |
| SM-JD-02 | 预算寿命与续量 | 双方 | RO-BUD-01 → FE.BudgetLifetime → RE | `projected_exhaust_at` 误差可量化；续量建议可审计 | FX-09 |
| SM-JD-03 | 收割稳定性优先 | HARVEST | 日序列 + 稳定性预测 → NO_ACTION 候选 | 高比例正确 HOLD；避免“为动而动” | FX-02 |
| SM-JD-04 | 待付款/退款致 ROI 虚高 | 双方 | BDV V-PAY/V-REF → 决策降级或改窗口 | 平台 ROI vs trusted ROI 偏差被解释；决策不被虚高带偏 | FX-03, FX-04 |
| SM-JD-05 | 跨计划重复归因 | 双方 | BDV V-ATTR → State → RE | 重复率进入 gap/WARN；避免双计功劳 | FX-05 |
| SM-JD-06 | 自然与推广耦合 | 双方 | BDV V-ORG → 目标函数/放量建议 | 不把自然成交全部记为推广成功 | FX-06 |
| SM-JD-07 | 低库存 + 放量意向 | SEEDING/新计划 | INV-GATE + Risk R3/R4 | 放量类动作被正确限制/拒绝 | FX-07 |
| SM-JD-08 | 活动日上午平淡晚间爆发 | 双方 | BusinessEvent + FE | 事件窗内建议与窗后回落可区分 | FX-08 |
| SM-JD-09 | 高客单长转化窗口 | HARVEST | OFG 权重 + 稳定性 | 不因短窗 ROI 抖动误杀计划 | FX-10 |
| SM-JD-10 | 门禁全链路演练 | 双方 | Risk×Trust×SRA×G-01..G-09 | 每个影子动作均有完整门禁痕迹；REJECT 可解释 | 组合 |
| SM-JD-11 | NO_ACTION 价值评估 | HARVEST 为主 | 对照评估 L1/L2 | HOLD 不是“系统失能”，而是稳定性优势 | 历史对照 |
| SM-JD-12 | 隔离与防污染审计 | — | §5 检查 P-01..P-05 | 连续运行零 live 污染 | 运行日志 |

### 6.2 最小可运行子集（建议首期只做这些）

若资源有限，首期影子闭环建议锁定：

1. **SM-JD-01**（种草获量下滑）  
2. **SM-JD-02**（预算寿命）  
3. **SM-JD-03**（收割稳定性 / NO_ACTION）  
4. **SM-JD-04**（BDV 虚高校验，保证“决策用的数是对的”）  
5. **SM-JD-10 + SM-JD-12**（门禁与防污染，保证系统可信）

其余任务在最小集稳定后扩展。

### 6.3 单任务执行骨架（SM-JD-01 示例）

```text
1. MODE_READ：拉取种草计划日内曲线（RO-MET-01/03）
2. BDV：校验是否存在延迟/异常/归因问题 → ValidatedMetricSet
3. STATE：组装，确认 gap_flags 不阻断
4. FE：预测未来 1–6h 展现/点击/加购走势
5. RE：若预测下滑超阈 → 候选动作（提价/溢价/预算）或 HOLD
6. Risk/Trust/Self-review：门禁
7. Shadow Gate：记账，不外发
8. T+window：只读复盘，计算 SM-M01/M03/M05/M02
9. 产物进 Shadow Pool；更新影子评估报告（不更新 live Trust）
```

---

## 7. 退出 / 升级到写权限的条件

> 影子运行不是终点。退出影子、进入写权限必须是**显式授权事件**，不是运行时自动发生。

### 7.1 升级阶梯

```text
S0  设计与 Fixture 自检（本文档 + 接口契约）
S1  MODE_READ 稳定：BDV/STATE/FE 可用
S2  MODE_SHADOW_DECIDE 稳定：完整决策 + 门禁 + Shadow Packet
S3  对照评估达标：L1/L2 指标满足 Proposed 门槛，样本量达标
S4  防污染审计通过：P-01..P-05 全绿
S5  负责人评审：是否允许进入 SANDBOX_LIVE（只读沙箱）  ← 需新 GA-DEC
S6  沙箱只读联调通过
S7  沙箱写（仍 dry_run / 仿真）验证
S8  生产 Live-Write：需新 GA-DEC + Trust 达标 + 人工否决权保留
```

**本轮设计只覆盖到 S4 的条件定义；S5 起均需单独授权决策，不在本文授权范围内。**

### 7.2 进入“可评审升权”的必要条件（Proposed）

必须**同时**满足：

| 类别 | 条件 | 门槛草案（Proposed） |
|---|---|---|
| 样本 | 可判定影子决策样本量 | n ≥ 50；覆盖 ≥3 个最小任务 |
| 预测 | SM-M03（24h） / SM-M04 | 命中率 ≥ 0.6；MAPE 进入可接受带（待标定） |
| 决策 | SM-M01 / SM-M02 / SM-M08 | 方向一致 ≥ 0.7；NO_ACTION 正确 ≥ 0.8 |
| 门禁 | SM-M06/07 | 无“硬红线仍 APPROVE”；误拒可解释 |
| 数据 | SM-M09 / BDV FAIL 阻断有效 | 关键决策 0 次使用 FAIL 数据 |
| 隔离 | SM-M10 / P-01..05 | 连续 14 日零污染 |
| 治理 | Shadow 经验未非法晋升 | 审计通过 |
| 授权 | 新 GA-DEC / 负责人签字 | 显式记录 |

### 7.3 Trust 映射说明（重要）

| 问题 | 约定 |
|---|---|
| 影子表现能否提高 Trust Score？ | **不能直接提高 live Trust Score**（`trust_credit_allowed=false`） |
| 影子表现有什么用？ | 作为**升权评审材料**与 FE/门禁校准输入；可建立 `shadow_trust_proxy`（仅影子域） |
| Live-Write 最低条件 | 新授权决策 + live 只读验证 + Trust Level 满足动作类（见 Risk 文档矩阵）+ 人工否决保留 |
| 升权后是否丢掉影子？ | 否。LIVE 与 SHADOW 可并行：写动作走主链，影子继续用于探索与对照 |

### 7.4 降级 / 回退条件

出现任一情况，应从当前档位回退或冻结升权：

1. 发现 live Memory/Rule 被 shadow 污染（P-05 失败）；  
2. 影子决策系统性触发硬红线建议（说明门禁或推理失效）；  
3. 对照评估显示方向一致率显著低于门槛；  
4. 数据校验被绕过或伪造 PASS；  
5. 负责人主动冻结。

---

## 8. 风险与局限

| 风险 ID | 风险 | 影响 | 缓解 |
|---|---|---|---|
| SM-R01 | **学习污染**：SIMULATION/SHADOW 回执被当成真实经验 | 学到假规律，错误升规则 | §5 标签强制 + 隔离池 + P-01..05 验收 |
| SM-R02 | **反事实不可识别**：影子“若执行”无法被同一世界验证 | 高估决策能力 | 只主张代理指标；L3 结论降权；升权需 L1/L2+负责人 |
| SM-R03 | **选择偏差**：影子只在可读/有 Fixture 的窗口运行 | 指标乐观 | 样本覆盖多样化；报告中声明覆盖偏差 |
| SM-R04 | **与人工动作互相干扰**（若并行观察真实投放） | 对照失真 | 优先用历史窗口；并行时标注 concurrent_action |
| SM-R05 | **NO_ACTION 被误判为系统无能/或过度自信** | 误停或误放 | SM-M02 专项；人工抽检 |
| SM-R06 | **BDV 规则在 shadow 被放宽** | 决策建立在脏数据上 | 禁止伪造 PASS；SM-M09 监控 |
| SM-R07 | **模式误配**：以为在 shadow 实际装配了 live transport | 真实副作用 | Runtime mode 默认 FIXTURE_ONLY；LiveTransport 硬失败；启动自检 |
| SM-R08 | **指标阈值过早固化** | 为了刷分优化错误目标 | 全部 Proposed；首期后由负责人修订 |
| SM-R09 | **影子建议被外传给运营执行却无审计** | 形成“影子外的影子写” | 任何外传建议必须仍走 Decision Packet + 人类记录，禁止口头改价 |
| SM-R10 | **Fixture 场景过少导致过拟合演示** | 高估闭环成熟度 | 最小任务集扩展计划；明确 Fixture≠真实分布 |

**固有局限（接受，不假装解决）：**

1. 影子运行**不能**提供平台系统学习/竞争环境被干预后的真实因果效应。  
2. 影子运行**不能**替代真实写权限下的 Trust 证据。  
3. 在无真实订单/库存源时，BDV 与决策变量可能不完整（`gap_flag` 必须显式）。

---

## 9. 理论追踪

| 理论主张 | GA-1 锚点 | 本文落点 | 覆盖 |
|---|---|---|---|
| 预测驱动决策 | §6.2, §8.3, GA-INNOV-002 | §3 FE 前置；§4 L2 预测对照；§6 SM-JD-01/02 | Mapped |
| 经营状态感知 / 数据不可直信 | §6.3, §8.1, GA-INNOV-003 | §3 BDV 强制；§6 SM-JD-04/05/06 | Mapped |
| 稳定性优先 / NO_ACTION | §8.5 | §6 SM-JD-03/11；SM-M02 | Mapped |
| 调整响应窗口 | §8.6 | §4 预注册 expected_response_window；SM-M05 | Mapped |
| 风险受控成长 / Trust 分级 | §6.7, §11, GA-INNOV-007 | §2 权限矩阵；§7 升级阶梯；影子不直接升 Trust | Mapped |
| 自审批前置 | §11.2 | §3 门禁链原样执行；§6 SM-JD-10 | Mapped |
| 失败即学习事件 | §9.4 | Shadow REJECT/HOLD 记账；但进隔离池不与 live 混计 | Mapped |
| 知识演化不越级 | §10, GA-INNOV-005/006 | §5.4 特批通道；禁止自动晋升 | Mapped |
| 权限随信任生长 | GA-DEC-004 红线；架构回路 D | §7 显式授权，shadow proxy ≠ live Trust | Mapped |
| 平台隔离 / 场景可插拔 | §4, 架构 P8 | 京东为第一验证场；抖音后置 | Mapped（本场） |

---

## 10. 与后续任务的接口

| 下游 | 本文供给 |
|---|---|
| GA2-T10 Decision Packet | Shadow Packet = Decision Packet + RuntimeEnvelope + 对照字段 |
| GA2-T12 门禁联调手册 | Shadow Gate 分流点；门禁演练任务 SM-JD-10 |
| GA2-T13 Forecast 接口 | 对照评估 L2 的 horizon/指标需求 |
| GA2-T15 参数预标定 | Shadow 指标 SM-M01..10 可作为标定反馈（仍 Proposed） |
| GA-3 验证 | 最小任务清单、对照方法、升权必要条件、防污染验收 |

---

## 11. 待决问题

| ID | 问题 | 建议 | 阻塞 |
|---|---|---|---|
| SM-Q1 | Shadow Pool 与 live Memory 的隔离是逻辑库还是物理库？ | 先逻辑隔离 + 硬查询视图；上线前可升级物理隔离 | 否 |
| SM-Q2 | `shadow_trust_proxy` 是否需要独立公式？ | 需要；仅影子域使用，不映射 live Level | 否 |
| SM-Q3 | 人工对照集如何抽样避免泄露与偏差？ | 分层抽样（计划类型×生命周期）；报告披露覆盖 | 否 |
| SM-Q4 | MODE_SHADOW_EXEC_SIM 的状态机保真度边界写在哪里？ | 单独仿真器说明；默认不做跨计划竞争建模 | 否 |
| SM-Q5 | 影子建议若被运营“参考执行”，算不算影子写？ | 算线下人工作业；必须补人工 Decision 记录，否则禁止 | 是（治理） |
| SM-Q6 | 升权评审由谁签字？ | 项目负责人；重大动作另需 GA-DEC | 是（流程） |
| SM-Q7 | 抖音侧 shadow 是否复用同一 envelope？ | 是；扩展字段后置 | 否 |

---

## 12. 变更记录

| 日期 | 版本 | 变更 | 依据 |
|---|---|---|---|
| 2026-09-11 | v0.1 | 首次建立 Shadow Mode 设计：四运行模式、数据通路与 Shadow Gate、对照评估、环境标签与 Learning 过滤、京东最小任务、升权条件、风险与理论追踪 | GA2-T11；Architecture v0.2；GA-DEC-004；JD Adapter JD-Q10 |

---

**Document Status:** Draft  
**Next Review:** 项目负责人 / Research Architect  
**Explicit Non-claim:** 本文不代表已接入真实京东账户；所有阈值、门槛与指标均为 Proposed；影子运行不得产生真实投放副作用，也不得直接提升写权限 Trust Level。
