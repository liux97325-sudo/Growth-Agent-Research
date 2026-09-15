# GA-2：Shadow 试运行计划（无写）

**文档编号：** GA-2-TRIAL-001  
**任务编号：** GA2-T26  
**版本：** v0.1  
**状态：** Draft  
**阶段：** GA-2 Engineering Design  
**输入基线：** `Research/GA-1/GA-1_Theory_v1.0.md`（GA-1.0 / v1.0，Confirmed）  
**主线架构：** `Architecture_Overview_v0.2.md`（Confirmed，GA-DEC-004）  
**工程基线：** `GA-2.0_Baseline_Package.md`（Confirmed，GA-DEC-005）  
**授权依据：** `GA-DEC-005`（Accepted；授权 Shadow 试运行方案，不含真实写与只读连接）  
**权威契约（本文强制引用）：**  
- `Shadow_Mode_Design_v0.1.md`（GA2-T11）— 四模式、最小任务集、对照评估 SM-M*  
- `Runtime_Envelope_Selfcheck_v0.1.md`（GA2-T21）— SC-A–E 启动自检、RE-I* 不变式、RA-* 熔断  
- `Gate_Integration_Playbook_v0.2.md`（GA2-T19）— 双字段门禁、G-01–G-09、失败模式 B-*/F-*/P-*  
- `JD_Adapter_Interface_v0.2.md`（GA2-T18）— G-07 dry_run、FX-01…FX-10、`SHADOW_WRITE_FORBIDDEN`  
- `Decision_Packet_Schema_v0.1.md`（GA2-T10）— `packet_kind=shadow_decision`、DPK-I5  
- `Precalibration_Experiment_Design_v0.1.md`（GA2-T15）— PE-M* 指标、PE-S* 熔断  

**作者角色：** Research Engineer 子代理（工程派生，不新增理论主张）  
**约束：** 本文仅为影子试运行**计划契约**；**不改 GA-1；不含真实写操作、无可执行投放脚本、无任何凭证**；所有阈值与指标默认 `Proposed`。真实平台只读连接评估须单独授权（GA2-T25），本计划**不假设已授权**。

---

## 0. 安全边界与范围声明（强制阅读）

### 0.1 本轮明确不做

| 项 | 说明 |
|---|---|
| 真实平台写操作 | 不调用任何改价/改预算/建计划接口 |
| 凭证与密钥 | 不创建、不示例、不落盘任何 AppKey / Token / Secret |
| 可执行投放脚本 | 不提供任何可对真实广告账户产生副作用的脚本或命令 |
| 接入真实只读连接 | 本计划**不假设** GA2-T25 已授权；数据源限于 Fixture / 历史导出 |
| Trust 自动升权 | 试运行结果**不得**直接提升 live Trust Level |
| 修改 GA-1 / 架构主线 | 纯工程派生；不修改理论、PROJECT_SPEC、Architecture v0.2 |
| 启动 GA-3 | 本计划仅预留验证钩子，不执行 GA-3 实验 |

### 0.2 本轮明确要做

1. 将 Shadow Mode 设计转化为**可执行的试运行计划**（目标、范围、前置检查、数据、节奏、指标、产出物、退出条件）。  
2. 锁定京东种草/收割最小任务集（引用 Shadow §6.2）。  
3. 将 Runtime Envelope SC-A–E 自检与 GIP v0.2 双字段门禁作为**试运行前置硬门**。  
4. 定义三档数据输入方案与切换条件。  
5. 定义日切片执行节奏、评估窗口与停止条件。  
6. 给出 trial report 模板与升权/退出条件。

---

## 1. 试运行目标与非目标

### 1.1 一句话目标

> 在零真实写副作用的约束下，用 Fixture / 历史导出完整演练京东种草/收割决策闭环（感知→校验→预测→推理→门禁→记账），系统评估：**若该决策被执行，预测与决策质量会达到什么水平**。

### 1.2 目标拆解

| 目标 ID | 目标 | 非目标（明确排除） |
|---|---|---|
| TR-G1 | 验证**预测质量**：走势 / 预算寿命 / 稳定性 / 爆发概率（SM-M03/M04） | 不追求平台侧真实调参反馈 |
| TR-G2 | 验证**决策质量**：动作方向、幅度、时机、NO_ACTION 比例是否合理（SM-M01/M02/M08） | 不证明反事实必然成功 |
| TR-G3 | 验证**门禁闭环**：Risk / Trust / Self-review / G-01–G-09 可运行且可审计（SM-M06/M07） | 不解锁写权限 |
| TR-G4 | 验证**数据校验链**：BDV 偏差是否被正确识别并影响决策（SM-M09） | 不替代真实数据接入评审 |
| TR-G5 | 验证**环境隔离与学习防污染**：连续运行零 live 污染（SM-M10 / P-01…P-05） | 不把影子经验当作企业知识资产 |
| TR-G6 | 为升权评审与 GA-3 预留可测验证钩子（指标定义、对照窗口、样本组织） | 不在本阶段执行 GA-3 实验 |

### 1.3 判断准则（什么算试运行做成了）

1. **可重放：** 同一 `state_digest` + 同一知识/参数版本，影子决策可复现（或可解释地随机）。  
2. **可审计：** 每个影子决策都有完整 Decision/Shadow Packet 与门禁痕迹。  
3. **可对照：** 能回答"影子建议 vs 人工/既有投放结果，差在哪里"。  
4. **零副作用：** 对平台状态、真实账户、企业规则库均无可写变更。  
5. **零污染：** 影子回执不进入 live Trust 计分、不晋升 Rule/Strategy/Genome。  
6. **自检通过：** 每次启动均通过 SC-A–E 完整自检（PASS 或 PASS_READ_ONLY）。

---

## 2. 范围：京东种草/收割最小任务集

> 引用 `Shadow_Mode_Design_v0.1.md` §6.2 最小可运行子集。  
> 第一验证场 = 京东广告；任务均可在 Fixture / 历史导出 / 只读状态下完成。

### 2.1 最小任务集（首期只做这些）

| 任务 ID | 名称 | 计划类型 | 主能力链路 | 依赖 Fixture | 试运行成功判据（Proposed） |
|---|---|---|---|---|---|
| SM-JD-01 | 种草获量下滑干预 | SEEDING | RO-MET-01/03 → BDV → FE → RE → 门禁 | FX-01 | 能在下滑拐点前给出"干预 or HOLD"，方向事后可核 |
| SM-JD-02 | 预算寿命与续量 | 双方 | RO-BUD-01 → FE.BudgetLifetime → RE | FX-09 | `projected_exhaust_at` 误差可量化；续量建议可审计 |
| SM-JD-03 | 收割稳定性优先 | HARVEST | 日序列 + 稳定性预测 → NO_ACTION 候选 | FX-02 | 高比例正确 HOLD；避免"为动而动" |
| SM-JD-04 | 待付款/退款致 ROI 虚高 | 双方 | BDV V-PAY/V-REF → 决策降级或改窗口 | FX-03, FX-04 | 平台 ROI vs trusted ROI 偏差被解释；决策不被虚高带偏 |
| SM-JD-10 | 门禁全链路演练 | 双方 | Risk×Trust×SRA×G-01..G-09 | 组合 | 每个影子动作均有完整门禁痕迹；REJECT 可解释 |
| SM-JD-12 | 隔离与防污染审计 | — | §5 检查 P-01..P-05 | 运行日志 | 连续运行零 live 污染 |

**扩展任务（最小集稳定后）：** SM-JD-05（跨计划重复归因）、SM-JD-06（自然与推广耦合）、SM-JD-07（低库存+放量意向）、SM-JD-08（活动日节奏）、SM-JD-09（高客单长转化窗口）、SM-JD-11（NO_ACTION 价值评估）。

### 2.2 任务 × 运行模式映射

| 阶段 | 运行模式 | 说明 |
|---|---|---|
| Phase-0 | MODE_READ | 只跑 BDV / STATE / FE，验证数据与预测链路可用 |
| Phase-1 | MODE_SHADOW_DECIDE（默认影子档） | 完整决策闭环 + 门禁 + Shadow Packet 记账 |
| Phase-2 | MODE_SHADOW_EXEC_SIM（需显式开启） | 局部反事实推演；隔离加强 |

> 任何阶段均**不**进入 MODE_LIVE_WRITE。LiveTransport 必须未装配或硬失败（RE-I5）。

### 2.3 每任务执行骨架（SM-JD-01 示例，其余同构）

```text
1. 启动自检：SC-A…SC-E 全绿 → selfcheck_ref 写入 RuntimeEnvelope
2. MODE_READ：拉取种草计划日内曲线（RO-MET-01/03）
3. BDV：校验是否存在延迟/异常/归因问题 → ValidatedMetricSet
4. STATE：组装，确认 gap_flags 不阻断
5. FE：预测未来 1–6h 展现/点击/加购走势
6. RE：若预测下滑超阈 → 候选动作（提价/溢价/预算）或 HOLD
7. Risk/Trust/Self-review：门禁原样执行（GIP §2.1）
8. Shadow Gate：envelope 一致性校验 → 记账，不外发（allow_platform_write=false）
9. 生成 Shadow Packet（packet_kind=shadow_decision，execution_mode=SHADOW_READ_ONLY）
10. T+window：只读复盘，计算 SM-M01/M03/M05/M02
11. 产物进 Shadow Pool；更新 trial report（不更新 live Trust）
```

---

## 3. 前置检查清单

> 引用 `Runtime_Envelope_Selfcheck_v0.1.md` §3（SC-A–E）与 `Gate_Integration_Playbook_v0.2.md`（双字段门禁 + G-07）。  
> **每次启动必须通过完整自检；自检 FAIL/ABORT 不得通过"跳过自检"参数绕过。**

### 3.1 SC-A 配置自检

| 检查 ID | 检查项 | 通过条件 | 失败动作 |
|---|---|---|---|
| SC-A1 | 默认运行模式 | 配置默认 `mode ∈ {MODE_READ, MODE_SHADOW_DECIDE}` | 拒绝启动写能力；强制 MODE_READ 或 abort |
| SC-A2 | LIVE 显式授权 | `mode=MODE_LIVE_WRITE` 仅当存在有效 GA-DEC 引用 | 无授权则降级为 MODE_SHADOW_DECIDE 或 abort |
| SC-A3 | env 与 mode 合法组合 | 满足 RE-I1..I4 静态组合表 | abort |
| SC-A4 | execution_mode 唯一允许值 | 本轮只允许 `SHADOW_READ_ONLY` | abort |
| SC-A5 | 凭证源 | 非 LIVE：CredentialProvider 返回拒绝；进程环境无真实密钥加载 | abort |
| SC-A6 | 配置可溯源 | `config_ref` 非空；含 mode/env/adapter_runtime | abort |

### 3.2 SC-B Adapter 传输层自检

| 检查 ID | 检查项 | 通过条件 | 失败动作 |
|---|---|---|---|
| SC-B1 | LiveTransport 装配状态 | `adapter_runtime ∈ {FIXTURE_ONLY, SIMULATION}` 时 LiveTransport 未注入或 Fail-Closed stub | abort |
| SC-B2 | SANDBOX_LIVE / LIVE 装配 | 本轮不存在；DI 容器中无 live 客户端/端点配置 | abort + 告警 |
| SC-B3 | 网络出口策略 | 无真实广告域名白名单；出站拦截器 FAIL-CLOSED | abort |
| SC-B4 | 只读能力面 | 仅暴露 RO-*；写接口注册为硬失败包装器 | 注册失败则 abort |
| SC-B5 | dry_run 强制点（G-07） | Adapter.write 入口存在 G-07 守卫：非 LIVE 强制 `dry_run=true` | 守卫缺失则 abort |

### 3.3 SC-C 写路径硬失败自检

| 检查 ID | 检查项 | 通过条件 | 失败动作 |
|---|---|---|---|
| SC-C1 | 写路径探针 | 主动调用 `write` 干跑：期望 `REJECTED_BY_GATE` / `SIMULATED` / 硬异常，**绝不**触达网络 | 出现平台样式 ACK 或网络侧写 → **熔断并 abort** |
| SC-C2 | Shadow 写拒绝 | 构造 `execution_mode=SHADOW_READ_ONLY` 假包，期望 G-01 返回 `SHADOW_WRITE_FORBIDDEN` | 失败则 abort |
| SC-C3 | 幂等与门禁存在性 | G-01..G-09 守卫已挂载（至少 G-01/G-03/G-07） | 缺失则 abort |
| SC-C4 | 拒绝回执形态 | 拒绝时 status ∈ {REJECTED_BY_GATE, SIMULATED, NOT_APPLICABLE_NO_ACTION}；禁止 ACCEPTED@非 LIVE | 失败则熔断 |

### 3.4 SC-D env 标签透传自检

| 检查 ID | 检查项 | 通过条件 | 失败动作 |
|---|---|---|---|
| SC-D1 | 入口写入 | Adapter/Fixture 在首条 payload 写入 RuntimeEnvelope | abort |
| SC-D2 | 中游透传探针 | 注入带唯一 `envelope_id` 的测试对象，穿过 BDV→STATE→FE→RE，出口 envelope 关键字段一致 | 不一致 → abort |
| SC-D3 | 出口拒收 | Memory 写入口对缺失 envelope 或 `env` 被改为 LIVE 的 shadow 对象拒收 | 拒收逻辑缺失 → abort |
| SC-D4 | Trust 过滤 | Trust 更新接口拒绝 `trust_credit_allowed=false` 的样本 | 失败 → abort |
| SC-D5 | KE 晋升过滤 | KE 晋升接口拒绝 `env!=LIVE` 且无特批单号的候选 | 失败 → abort |

### 3.5 SC-E 防污染验收自检

| 检查 ID | 检查项 | 通过条件 | 失败动作 |
|---|---|---|---|
| SC-E1 | 池隔离可配置 | Shadow Pool 与 live Memory 逻辑/物理隔离可开关且默认隔离 | 失败 → 不得进入 Shadow-Decide |
| SC-E2 | 文案审计 | 模拟回执日志中不得出现 "platform accepted / 成功投放" | 失败 → 阻断启动或清日志后重跑 |
| SC-E3 | 抽样审计钩子 | 提供 0 条 live 规则引用 shadow-only 证据的检查器（可空实现但接口存在） | 接口缺失 → 不得宣称防污染达标 |

### 3.6 双字段门禁前置确认（GIP v0.2）

| 确认项 | 要求 | 依据 |
|---|---|---|
| G-01 双字段语义 | `lifecycle_status ∈ {Self-reviewed, Executed}` **且** `review_result ∈ {APPROVE, NO_ACTION_APPROVE}` | GIP v0.2 §1.1；JD v0.2 §3.4 |
| G-01 Shadow 硬拒绝 | `execution_mode=SHADOW_READ_ONLY` 时写路径硬拒绝（`SHADOW_WRITE_FORBIDDEN`） | GIP v0.2 C4；DPK-I5 |
| G-07 dry_run 强制 | 非 LIVE 环境或 `execution_mode=SHADOW_READ_ONLY` 强制 `dry_run=true` | GIP v0.2 C8；JD v0.2 G-07 |
| review_result 写入权 | **仅 SRA 可写**；其他组件只读 | GIP v0.2 C5；DPK §2.6 |
| NO_ACTION 成包 | `NO_ACTION` 必须完整走过 Draft→Self-reviewed→Observed→Reflected | GIP v0.2 C3；DPK-I2 |
| 组合裁决表 | 按 GIP v0.2 §4.2 双字段轴执行；#18 Shadow 包硬拒绝 | GIP v0.2 §4.2 |

### 3.7 自检结果门控

```text
selfcheck.status:
  PASS          → 允许以配置 mode 运行（仍受运行时断言约束）
  PASS_READ_ONLY→ 仅允许 MODE_READ；Shadow-Decide 能力卸载
  FAIL          → 拒绝一切决策外发；仅允许人工排障路径
  ABORT         → 进程退出或会话冻结
```

**规则：**

1. `FAIL`/`ABORT` 不得通过"跳过自检"参数绕过（除非负责人显式 break-glass，且该 break-glass 本身写入审计，不得开启 LIVE 写）。  
2. 自检探针（SC-C1/C2/D2）必须使用 Fixture/内存，**不得**依赖真实平台。  
3. 自检通过 ≠ 升权；不改变 Trust Level，不授权 MODE_LIVE_WRITE。

---

## 4. 数据输入方案（三档）

> 本计划**不假设** GA2-T25 真实只读连接已授权。数据源按三档递进，每档有明确准入条件。

### 4.1 三档定义

| 档位 | 代码 | 数据来源 | 准入条件 | 适用任务 | 硬约束 |
|---|---|---|---|---|---|
| **档一：Fixture** | `SRC-FIXTURE` | 设计 Fixture 库（FX-01…FX-10） | 无需外部授权；开发/测试环境 | 全部最小任务集；管道自检 | **不得**用于"证明 live 最优"（TCAL §6.4）；env=FIXTURE |
| **档二：历史导出** | `SRC-EXPORT` | 匿名化/脱敏历史导出 | 负责人批准数据导出与脱敏方案 | E1 离线回放；对照评估 L1/L2；SM-M* 计算 | 字段映射须经 BDV 语义对齐；不含写接口；env=SHADOW |
| **档三：授权后只读** | `SRC-LIVE-RO` | 平台只读连接（Live-Read） | **需单独 GA-DEC**（GA2-T25）+ Trust 门控配置 | 真实轨迹对照；扩大样本覆盖 | dry_run 恒 true；禁止 write；LiveTransport 仅在 adapter_runtime=LIVE 且有授权时可实例化 |

### 4.2 档位切换条件

```text
档一（Fixture）稳定 → 可评估是否进入档二
  条件：SC-A–E 全绿；SM-JD-01/02/03/04 在 Fixture 上完成 ≥1 轮完整闭环；
        SM-M10=1.0（零污染）；trial report 模板验证通过

档二（历史导出）稳定 → 可评估是否进入档三
  条件：档二运行 ≥14 日连续零污染；SM-M01 ≥ 0.7、SM-M02 ≥ 0.8（Proposed）；
        负责人评审 + 新 GA-DEC 授权只读连接（GA2-T25）

档三（授权后只读）→ 仍为 MODE_READ / MODE_SHADOW_DECIDE
  条件：GA2-T25 完成只读连接评估；SC-B1/B2/B3 针对 SRC-LIVE-RO 通过；
        LiveTransport 仅注入只读能力；写路径仍硬失败
```

**本计划只覆盖档一与档二的执行契约；档三须在 GA2-T25 授权后另行补充。**

### 4.3 数据源字段需求（引用权威）

| 字段类别 | 引用来源 | 说明 |
|---|---|---|
| 资源与指标 | JD v0.2 §2.1 RO-* 能力清单 | RO-MET-01/03、RO-BUD-01 等 |
| BDV 规则 | JD v0.2 §5.2 V-PAY/V-REF/V-ATTR/V-ORG | 待付款、退款、跨计划归因、自然耦合 |
| 阈值清单 | TCAL（T14）§3.2 字段字典 | 不重复枚举 |
| 运行时标签 | Runtime Envelope §1.1 | env/mode/dry_run/learning_pool 等 |
| 决策包字段 | Decision Packet Schema §2 | 双字段、shadow_decision 附加字段 |

### 4.4 数据纳入/排除规则（对齐 TCAL §3.3）

| 规则 | 条件 | 处置 |
|---|---|---|
| env 隔离 | `origin_env != LIVE` | 不进 live 主集；进 Shadow Pool |
| BDV FAIL | `ValidationReport.blocking_for_decision=true` | 排除出主集；关键决策 0 次使用 FAIL 数据 |
| 活动窗 | 活动爆发窗 / 平台异常窗 | 不进主阈值 train；单独分层 |
| 标签缺失 | 关键结果标签缺失率过高 | 仅观察集；不进敏感性主结论 |
| 排除计数 | 任何排除 | 必须写入 trial report `excluded_summary`；禁止静默丢样本 |

---

## 5. 执行节奏

### 5.1 试运行阶段划分

```text
T0  启动准备（1–2 日）
      → SC-A–E 自检；Fixture 就绪；trial report 模板就绪
        │
T1  日切片试运行（Proposed: ≥14 连续日）
      → 每日：MODE_READ → MODE_SHADOW_DECIDE → 记账 → 对照
        │
T2  评估窗口（每日 / 每周）
      → T+window 回看；计算 SM-M*；更新 trial report
        │
T3  周复盘（Proposed: 每 7 日）
      → 门禁一致性抽检；NO_ACTION 价值评估；SM-JD-12 防污染审计
        │
T4  升权评审准备（T1 满足门槛后）
      → 汇总 trial report；判断是否进入下一阶段
```

### 5.2 日切片执行规范

| 时段 | 活动 | 产物 |
|---|---|---|
| 启动 | 运行 SC-A–E 完整自检；确认 selfcheck_record.status=PASS | selfcheck_record；envelope.selfcheck_ref |
| 主时段 | 对锁定任务集执行完整决策闭环（Mode-B） | Shadow Packet；SimulatedActionReceipt；TRACE |
| 回看时段 | 按 `expected_response_window` 到期拉取 RO-MET-* + BDV；计算对照指标 | ShadowEvalReport |
| 日终 | 隔离审计（P-01…P-05）；写入日切片报告 | 日切片审计记录 |

**Proposed 节奏参数：**

| 参数 | Proposed 默认值 | 说明 |
|---|---|---|
| 试运行总天数 | ≥14 连续日 | 对齐 SM §7.2 "连续 14 日零污染" |
| 日切片任务数 | 每任务每切片 1–3 个决策场景 | 避免单日过密导致样本非独立 |
| 评估窗口 | 随 `plan_mode`：种草短、收割长（GIP-Q4） | 1h / 6h / 24h / 7d |
| 周复盘日 | 每 7 日 | 门禁抽检 + 防污染审计 |

### 5.3 评估窗口（对齐 SM §4.2 / FE 接口）

| 层级 | 方法 | 输出指标 | 置信度 |
|---|---|---|---|
| L1 决策合理性 | 人工对照集 + 专家抽检 + 门禁一致性 | SM-M01/M02/M06/M07 | 最高（无需反事实） |
| L2 预测一致性 | 事后校准：T+1…T+n 真实只读指标回看 Forecast | SM-M03/M04/M05 | 中（利用 FE 本身） |
| L3 轨迹相似 | 带约束 rollout / 邻近计划对照（仅 MODE_SHADOW_EXEC_SIM） | 相对基线带状改善估计 | 最弱；**L3 结论不得单独作为升权证据** |

### 5.4 停止条件（对齐 PE-S* 与 SM §7.4）

| 停止 ID | 触发条件 | 动作 | 依据 |
|---|---|---|---|
| TR-S01 | SM-M10 < 1.0（隔离失败 / live 污染事件） | **立即停试运行**；修复防污染 | PE-S01；SM §7.4(1) |
| TR-S02 | 启动自检 FAIL/ABORT | 冻结会话；人工排障；重新自检 | RE-I12；RESC §3.2 |
| TR-S03 | RA-01/02/08/10 重复失败 | Trip-Freeze：冻结一切写路径与 Shadow-Decide 外发 | RESC §4.2 |
| TR-S04 | RA-03/12 触发（LiveTransport 误装配 / 网络出站） | Trip-Abort：冻结会话；告警负责人；人工确认无平台写后方可回到 Shadow 档 | RESC §4.2 |
| TR-S05 | 关键决策使用 BDV FAIL 数据 | 熔断该任务组；回退修复 BDV | PE-S03 |
| TR-S06 | 影子决策系统性触发硬红线建议 | 冻结升权；排查门禁/推理是否失效 | SM §7.4(2) |
| TR-S07 | 对照评估显示方向一致率显著低于门槛（Proposed SM-M01 < 0.5） | 冻结升权；回退评审 | SM §7.4(3) |
| TR-S08 | 数据校验被绕过或伪造 PASS | 熔断；审计 | SM §7.4(4)；GIP F-03 |
| TR-S09 | 负责人主动冻结 | 全面停止 | SM §7.4(5) |
| TR-S10 | DR-01/DR-07/DR-06 演练任一失败 | 一票否决：不得宣称 Shadow Mode 可用 | RESC §7.2 |

---

## 6. 成功指标与失败熔断

### 6.1 成功指标（引用 SM-M* / PE-M*，全部 Proposed）

| 指标 ID | 名称 | 定义 | 默认观察窗 | 试运行成功门槛（Proposed） |
|---|---|---|---|---|
| SM-M01 | 动作方向一致率 | shadow 方向（↑/↓/HOLD）与人工/事后合理方向一致占比 | 事件级 | ≥ 0.7 |
| SM-M02 | NO_ACTION 正确率 | HOLD 后窗口内指标未破阈的比例 | 随 plan_mode | ≥ 0.8 |
| SM-M03 | 预测命中率 | 事后落在预测分位带的比例 | 1h / 6h / 24h / 7d | ≥ 0.6（24h） |
| SM-M04 | 预测 MAPE | 分 horizon 误差 | 同上 | 进入可接受带（待标定） |
| SM-M05 | 干预提前量 | 相对事后确认拐点的 lead time | 事件级 | 可量化 |
| SM-M06 | 门禁通过率 | APPROVE / 总候选 | 周 | 无"硬红线仍 APPROVE" |
| SM-M07 | 门禁误拒代理 | 人工认为应做但 shadow REJECT/HOLD | 周抽检 | 可解释 |
| SM-M08 | 幅度校准误差 | \|shadow Δ − 合理 Δ\| / 合理 Δ | 动作级 | 可报告 |
| SM-M09 | 数据校验影响率 | 因 BDV 降级导致决策改变的比例 | 周 | 关键决策 0 次使用 FAIL 数据 |
| SM-M10 | 隔离完整率 | 零 live 污染事件 | 连续日 | **= 1.0（硬门槛）** |
| PE-M11 | 门禁拒绝率（分 R 档） | 被约束/拒绝动作 / 候选动作 | 周 | 可报告 |
| PE-M12 | NO_ACTION 率 | HOLD/NO_ACTION / 全部决策 | 周 | 与 PE-M02 联合解读；禁止只报单指标 |

**有效样本量门槛（Proposed）：** 可判定影子决策样本量 `n ≥ 50`；覆盖 ≥3 个最小任务。

### 6.2 失败熔断矩阵

| 熔断级别 | 触发条件 | 行为 | 依据 |
|---|---|---|---|
| **Trip-Reject** | 单次 RA-01/02/08/10 失败 | 拒绝该动作；写 REJECTED_BY_GATE / 熔断事件；会话可继续只读 | RESC §4.2 |
| **Trip-Freeze** | RA-04/05/06/07/09 重复失败，或 RA-03/12 | 冻结一切写路径与 Shadow-Decide 外发；保留只读与审计 | RESC §4.2 |
| **Trip-Abort** | 启动自检 FAIL，或确认 LiveTransport 误装配已触达网络 | 冻结会话；要求重新 boot + 完整自检；告警负责人 | RESC §4.2 |
| **试运行熔断** | TR-S01 / TR-S04 / TR-S10 | 立即停止试运行；不得进入升权评审 | 本文 §5.4 |

### 6.3 防污染验收检查（SM §5.5 + RESC SC-E）

| 检查 | 通过条件 | 试运行期间要求 |
|---|---|---|
| P-01 | Shadow Packet 存储与 live Memory 存储物理/逻辑隔离可配置 | 默认隔离 |
| P-02 | Trust 更新接口拒绝 `trust_credit_allowed=false` 的样本 | 每日验证 |
| P-03 | KE 晋升接口拒绝 `env!=LIVE` 且无特批单号的候选 | 每日验证 |
| P-04 | 日志中 `simulated` 回执不得出现 "platform accepted/成功投放" 文案 | 每日验证 |
| P-05 | 抽样审计 0 条 live 规则引用 shadow-only 证据（无特批） | 周抽检 |

### 6.4 失败演练场景（引用 RESC §7）

| 场景 ID | 名称 | 期望检测点 | 期望结果 | 试运行期间要求 |
|---|---|---|---|---|
| DR-01 | LiveTransport 误装配 | SC-B1/B2、RA-03、RA-12 | 启动 FAIL 或 Trip-Abort | **一票否决级** |
| DR-02 | dry_run 被绕过 | SC-B5、RA-01、G-07 | `DRY_RUN_REQUIRED` | 必须在 T0 前演练 |
| DR-03 | Shadow 包被标 LIVE | RA-10、G-01 | `PACKET_KIND_MISMATCH` | 必须在 T0 前演练 |
| DR-05 | 学习混池 | SC-D3/E1、RA-05 | `POOL_MISMATCH` | 必须在 T0 前演练 |
| DR-06 | Trust 偷计分 | SC-D4、RA-06 | `TRUST_CREDIT_FORBIDDEN` | **一票否决级** |
| DR-07 | 伪造 ACCEPTED 回执 | RA-08、RA-11 | 拒收或改判 SIMULATED | **一票否决级** |

> DR-01/DR-07/DR-06 为**一票否决级**：任一失败不得宣称 Shadow Mode 可用（RESC §7.2）。

---

## 7. 产出物：Trial Report 模板

> 文件名建议：`enterprise/{tenant}/shadow_trial_reports/{yyyymmdd}_shadow_trial_{batch_id}.md`  
> 研究仓库仅保留**空白模板**与 Example-Only 骨架，不提交真实租户结果。

### 7.1 报告模板结构

```markdown
# Shadow 试运行报告（模板）

- report_id: TRIAL-RPT-{tenant}-{yyyymmdd}-{seq}
- trial_batch_id: TR-BATCH-…
- runtime_envelope_root: { env, mode, dry_run: true, execution_mode: SHADOW_READ_ONLY }
- selfcheck_refs: [SC-…]
- data_source_tier: SRC-FIXTURE | SRC-EXPORT | SRC-LIVE-RO
- status: DRAFT_TRIAL_RESULT | PROPOSED_FOR_REVIEW
- explicit_non_claim: 一切数值为影子估计；非 Confirmed；未触达真实写；未提升 live Trust

## 1. 范围与预注册摘要
- 任务集：SM-JD-01 / 02 / 03 / 04 / 10 / 12
- 运行模式：MODE_READ → MODE_SHADOW_DECIDE →（可选）MODE_SHADOW_EXEC_SIM
- 试运行日期范围：____ 至 ____
- 预注册时间：____；偏离预注册的项：____（必须披露）

## 2. 启动自检记录
- 每日 selfcheck_record 摘要（selfcheck_id、status、failed_check_ids、circuit_level）
- 失败演练结果（DR-01…DR-12 通过情况）
- 自检通过率；任何 FAIL/ABORT 的处置记录

## 3. 数据源与切分
- 数据源类型与 origin_env 比例
- 字段齐套率；BDV 通过率
- excluded_summary: { bdv_reject, activity, anomaly, env_filter, label_missing }
- 分层覆盖：plan_mode × 任务 × n_eff

## 4. 决策样本统计
- 总决策数；按任务/plan_mode/动作类分布
- review_result 分布（APPROVE / NO_ACTION_APPROVE / REVISE / HOLD / REJECT / ESCALATE_HUMAN）
- risk_level 分布；hard_block 触发次数
- Shadow Packet 完整性：DPK-I1..I8 违反计数（应为 0）

## 5. 成功指标结果
### 5.1 SM-M01…M10 汇总
| 指标 | 点估计 | CI | n | 门槛（Proposed） | 判定 |
|---|---|---|---|---|---|
| SM-M01 方向一致率 | | | | ≥0.7 | |
| SM-M02 NO_ACTION 正确率 | | | | ≥0.8 | |
| SM-M03 预测命中率(24h) | | | | ≥0.6 | |
| SM-M06 门禁通过率 | | | | 无硬红线APPROVE | |
| SM-M10 隔离完整率 | | | | =1.0 | |

### 5.2 分任务结果
- SM-JD-01 / 02 / 03 / 04 各自样本量、主要指标、定性结论

### 5.3 门禁行为
- G-01…G-09 拒绝率（分原因码）
- 双字段门禁一致性抽检结果
- NO_ACTION 率 + SM-M02 联合解读（禁止只报单指标）

### 5.4 防污染审计
- P-01…P-05 每日/每周验证结果
- 零污染事件计数；SM-M10 判定

## 6. 对照评估详情
### 6.1 L1 决策合理性
- 人工对照集覆盖；一致率；专家抽检合理率
### 6.2 L2 预测一致性
- 分 horizon within_band / MAPE；触发精度/召回；提前量分布
### 6.3 L3 轨迹相似（若执行）
- 局部反事实推演结果；**L3 结论不得单独作为升权证据**声明

## 7. 风险与局限
- 选择偏差声明；覆盖偏差；Fixture≠真实分布
- 反事实不可识别固有局限
- 已知问题与待修复项

## 8. 建议决策
- Continue | Escalate-to-Review | Freeze | Abort
- 是否满足升权评审必要条件（§8.2）
- 需人工评审队列：Research Architect / 负责人
- 是否触发重跑自检/演练

## 9. 附件
- selfcheck_record 引用；Shadow Packet 抽样；envelope 配置快照
- 失败演练记录；排除计数明细；CHANGELOG
```

### 7.2 报告验收检查

| 检查 | 通过条件 |
|---|---|
| R-01 | 无 live 写痕迹；`dry_run`/env 声明完整 |
| R-02 | SM-M10 = 1.0；P-01…P-05 全绿 |
| R-03 | 所有指标带 n_eff 与 CI（或声明样本不足） |
| R-04 | 未把 shadow 证据写成 live 终值或 Confirmed |
| R-05 | 偏离预注册部分已披露 |
| R-06 | 自检与演练记录完整；一票否决级场景全过 |
| R-07 | 未决槽位/不足样本未被编造估计 |

---

## 8. 升权/退出到下一阶段的条件

> 引用 `Shadow_Mode_Design_v0.1.md` §7 升级阶梯。  
> **本计划只覆盖到 S4 的条件定义；S5 起均需单独授权决策，不在本文授权范围内。**

### 8.1 升级阶梯

```text
S0  设计与 Fixture 自检（本文档 + 接口契约）        ← 本计划起点
S1  MODE_READ 稳定：BDV/STATE/FE 可用
S2  MODE_SHADOW_DECIDE 稳定：完整决策 + 门禁 + Shadow Packet
S3  对照评估达标：L1/L2 指标满足 Proposed 门槛，样本量达标
S4  防污染审计通过：P-01..P-05 全绿                ← 本计划终点
S5  负责人评审：是否允许进入 SANDBOX_LIVE（只读沙箱） ← 需新 GA-DEC
S6  沙箱只读联调通过                                ← 需 GA2-T25 授权
S7  沙箱写（仍 dry_run / 仿真）验证                 ← 需新 GA-DEC
S8  生产 Live-Write：需新 GA-DEC + Trust 达标 + 人工否决权保留
```

### 8.2 进入"可评审升权"的必要条件（Proposed，须同时满足）

| 类别 | 条件 | 门槛草案（Proposed） |
|---|---|---|
| 样本 | 可判定影子决策样本量 | n ≥ 50；覆盖 ≥3 个最小任务 |
| 预测 | SM-M03（24h） / SM-M04 | 命中率 ≥ 0.6；MAPE 进入可接受带（待标定） |
| 决策 | SM-M01 / SM-M02 / SM-M08 | 方向一致 ≥ 0.7；NO_ACTION 正确 ≥ 0.8 |
| 门禁 | SM-M06 / SM-M07 | 无"硬红线仍 APPROVE"；误拒可解释 |
| 数据 | SM-M09 / BDV FAIL 阻断有效 | 关键决策 0 次使用 FAIL 数据 |
| 隔离 | SM-M10 / P-01..05 | 连续 14 日零污染 |
| 治理 | Shadow 经验未非法晋升 | 审计通过 |
| 授权 | 新 GA-DEC / 负责人签字 | 显式记录 |

### 8.3 Trust 映射说明

| 问题 | 约定 |
|---|---|
| 影子表现能否提高 Trust Score？ | **不能直接提高 live Trust Score**（`trust_credit_allowed=false`） |
| 影子表现有什么用？ | 作为**升权评审材料**与 FE/门禁校准输入；可建立 `shadow_trust_proxy`（仅影子域） |
| Live-Write 最低条件 | 新授权决策 + live 只读验证 + Trust Level 满足动作类 + 人工否决保留 |
| 升权后是否丢掉影子？ | 否。LIVE 与 SHADOW 可并行 |

### 8.4 退出到下一阶段（不含真实写）

| 出口 | 条件 | 后续动作 |
|---|---|---|
| 升权评审 | §8.2 全部满足 | 提交 trial report；负责人评审；决定是否授权 GA2-T25（只读连接）或进入 S5 |
| 继续影子 | 指标边缘或样本不足 | 维持当前档位；扩大样本；修订 Proposed 阈值 |
| 冻结 | TR-S01/S04/S06/S07/S08 任一触发 | 修复根因；重新自检；重新演练；不得跳过 |
| 退出（Abort） | 一票否决级失败（TR-S10）或负责人决定 | 全面停止；回归设计；须新 GA-DEC 才能重启 |

### 8.5 降级/回退条件（引用 SM §7.4）

1. 发现 live Memory/Rule 被 shadow 污染（P-05 失败）；  
2. 影子决策系统性触发硬红线建议；  
3. 对照评估显示方向一致率显著低于门槛；  
4. 数据校验被绕过或伪造 PASS；  
5. 负责人主动冻结。

---

## 9. 风险与伦理边界

### 9.1 风险登记（引用 SM §8 + 本文扩展）

| 风险 ID | 风险 | 影响 | 缓解 | 试运行期间特别关注 |
|---|---|---|---|---|
| SM-R01 | **学习污染**：SIMULATION/SHADOW 回执被当成真实经验 | 学到假规律，错误升规则 | §3.5 SC-E + §6.3 P-01..05 + SM §5 标签强制 | **每日验证** P-02/P-03 |
| SM-R02 | **反事实不可识别**：影子"若执行"无法被同一世界验证 | 高估决策能力 | 只主张代理指标；L3 结论降权；升权需 L1/L2+负责人 | 报告必须声明固有局限 |
| SM-R03 | **选择偏差**：影子只在可读/有 Fixture 的窗口运行 | 指标乐观 | 样本覆盖多样化；报告中声明覆盖偏差 | 披露 excluded_summary |
| SM-R04 | **与人工动作互相干扰** | 对照失真 | 优先用历史窗口；并行时标注 concurrent_action | 档一/档二优先历史 |
| SM-R05 | **NO_ACTION 被误判为系统无能/或过度自信** | 误停或误放 | SM-M02 专项；人工抽检 | 周复盘联合解读 |
| SM-R06 | **BDV 规则在 shadow 被放宽** | 决策建立在脏数据上 | 禁止伪造 PASS；SM-M09 监控 | 每日验证 |
| SM-R07 | **模式误配**：以为在 shadow 实际装配了 live transport | 真实副作用 | SC-B1/B2；LiveTransport 硬失败；启动自检 | **一票否决级** |
| SM-R08 | **指标阈值过早固化** | 为了刷分优化错误目标 | 全部 Proposed；首期后由负责人修订 | 首期后修订 |
| SM-R09 | **影子建议被外传给运营执行却无审计** | 形成"影子外的影子写" | 任何外传建议必须仍走 Decision Packet + 人类记录 | 治理流程约束 |
| SM-R10 | **Fixture 场景过少导致过拟合演示** | 高估闭环成熟度 | 最小任务集扩展计划；明确 Fixture≠真实分布 | 报告声明 |
| TR-R01 | **档二数据脱敏不充分** | 隐私/合规风险 | 负责人批准脱敏方案；不提交企业明细到研究仓库 | 档二准入前审查 |
| TR-R02 | **日切片过密导致样本非独立** | 统计结论失效 | 日切片任务数限制；聚类稳健 SE | 报告披露相关性 |

### 9.2 伦理 / 合规边界（引用 PE §6）

| ID | 边界 | 试运行要求 |
|---|---|---|
| PE-E01 | 不触碰真实投放 | 无 write API、无可执行改参脚本、无 dry_run=false 路径 |
| PE-E02 | 不伪造企业真值 | SIM/Fixture 结果必须标 `origin_env`；不得写入"企业已验证"表述 |
| PE-E03 | 不把影子当 live 证据 | Shadow/SIM 不进 live Trust、不晋升 Rule/Genome（特批除外且需负责人） |
| PE-E04 | 数据最小化与脱敏 | 历史导出优先脱敏；企业明细不提交研究仓库默认树 |
| PE-E05 | 可审计 | 每个试运行日有 selfcheck_id、决策样本、排除计数；报告可复现 |
| PE-E06 | 人工否决保留 | 试运行产物不得表述为"已授权自动执行" |
| PE-E07 | 理论优先 | 任何与 GA-1 冲突的"更优"实验结论 → 改工程文档或否决，不改理论 |
| PE-E08 | 租户隔离 | 默认租户内试运行；不合并跨租户数值 |

### 9.3 固有局限（接受，不假装解决）

1. 影子试运行**不能**提供平台系统学习/竞争环境被干预后的真实因果效应。  
2. 影子试运行**不能**替代真实写权限下的 Trust 证据。  
3. 在无真实订单/库存源时，BDV 与决策变量可能不完整（`gap_flag` 必须显式）。  
4. Fixture 场景是设计的，**不是**企业真实分布；SM-M* 在 Fixture 上的表现**不能**外推为 live 表现。

---

## 10. 与既有文档的接口

| 上游/下游 | 本文关系 |
|---|---|
| Shadow Mode（T11） | 消费最小任务集、对照评估方法、升权阶梯、SM-M*；不重复定义 |
| Runtime Envelope（T21） | 强制引用 SC-A–E、RE-I*、RA-*；每次启动必须通过自检 |
| Gate Playbook v0.2（T19） | 强制引用双字段门禁、G-01–G-09、组合裁决表、失败模式 |
| JD Adapter v0.2（T18） | 强制引用 G-07、FX-01…FX-10、`SHADOW_WRITE_FORBIDDEN` |
| Decision Packet（T10） | 消费 `shadow_decision` 变体、DPK-I5、NO_ACTION 成包 |
| Precalibration（T15） | 消费 PE-M* 指标与 PE-S* 熔断；试运行结果可作为预标定输入 |
| GA2-T25 真实只读连接评估 | 本文档三（SRC-LIVE-RO）条件；需单独 GA-DEC |
| GA-3 验证 | 本文不执行 GA-3；只预留对照指标与样本组织 |

---

## 11. 待决问题

| ID | 问题 | 建议 | 阻塞 |
|---|---|---|---|
| TR-Q1 | 档二历史导出的最小可用时间跨度？ | 优先覆盖常态 + ≥1 次大促；否则只做管道与 Prior 稳定性 | 档二准入 |
| TR-Q2 | 日切片任务数上限如何按槽位功效调整？ | 先统一保守占位 + 披露 CI；E0 盘点后修订 | 否 |
| TR-Q3 | 档三（授权后只读）的评估是否纳入本计划？ | 否；GA2-T25 授权后另文补充 | 否 |
| TR-Q4 | `shadow_trust_proxy` 公式是否纳入本文？ | 不纳入；仅约定不得映射 live T2/T8 | 否 |
| TR-Q5 | 人工对照集如何抽样避免泄露与偏差？ | 分层抽样（计划类型×生命周期）；报告披露覆盖 | 否 |
| TR-Q6 | 试运行期间是否允许 MODE_SHADOW_EXEC_SIM？ | 允许但需显式开启；L3 结论不得单独作为升权证据 | 否 |
| TR-Q7 | 试运行负责人是谁？ | 项目负责人；升权评审需新 GA-DEC | 是（治理） |
| TR-Q8 | 档一→档二切换的具体审批流程？ | 负责人批准脱敏方案 + trial report 档一结论 | 否 |

---

## 12. 变更记录

| 日期 | 版本 | 变更 | 依据 |
|---|---|---|---|
| 2026-09-11 | v0.1 | 首次建立 Shadow 试运行计划：目标与非目标、京东种草/收割最小任务集、SC-A–E 前置检查、三档数据输入、日切片执行节奏、SM-M*/PE-M* 成功指标与失败熔断、trial report 模板、升权/退出条件、风险与伦理边界 | GA2-T26；GA-DEC-005；Shadow_Mode_Design；Runtime_Envelope_Selfcheck；Gate_Integration_Playbook v0.2；JD_Adapter_Interface v0.2；Decision_Packet_Schema；Precalibration_Experiment_Design |

---

**Document Status:** Draft  
**Next Review:** 项目负责人 / Research Architect  
**Explicit Non-claim:** 本文不代表已接入真实京东账户；未提供任何凭证或可执行投放脚本；未修改 GA-1；试运行通过**不**授予 Live-Write 权限，也**不**提升 live Trust Level；所有阈值与指标均为 Proposed；真实平台只读连接评估须单独授权（GA2-T25），本计划不假设已授权。
