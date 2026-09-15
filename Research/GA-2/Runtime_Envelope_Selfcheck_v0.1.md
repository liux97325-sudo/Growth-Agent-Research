# GA-2：Runtime Envelope 启动/运行时自检设计稿

**文档编号：** GA-2-RESC-001  
**任务编号：** GA2-T21  
**版本：** v0.1  
**状态：** Draft  
**阶段：** GA-2 Engineering Design  
**输入基线：** `Research/GA-1/GA-1_Theory_v1.0.md`（GA-1.0 / v1.0，Confirmed）  
**主线架构：** `Architecture_Overview_v0.2.md`（Confirmed，GA-DEC-004）  
**强关联：** `Shadow_Mode_Design_v0.1.md`、`JD_Adapter_Interface_v0.2.md`、`Gate_Integration_Playbook_v0.2.md`、`Decision_Packet_Schema_v0.1.md`、`Risk_Trust_SelfReview_v0.1.md`  
**授权依据：** `GA-DEC-003` + `GA-DEC-004`（Accepted，主线冻结）  
**作者角色：** Research Engineer 子代理（工程派生，不新增理论主张）  
**约束：** 本文为运行时环境信封与自检契约；**不改 GA-1；不含真实写操作、无可执行投放脚本、无任何凭证**；所有阈值与默认值一律 **Proposed**。与理论冲突时以 GA-1 为准；与架构/主线冲突时以 Architecture v0.2 + GA-DEC-004 为准并修订本文。

---

## 0. 安全边界与范围声明（强制阅读）

### 0.1 本轮明确不做

| 项 | 说明 |
|---|---|
| 真实平台写操作 | 不调用任何真实投放/改价/改预算/建计划接口 |
| 凭证与密钥 | 不创建、不示例、不落盘任何 AppKey / Token / Secret |
| 可执行投放脚本 | 不提供任何可对真实广告账户产生副作用的脚本或命令 |
| 修改 GA-1 理论 | 本文为纯工程派生，不新增/修订理论主张 |
| LiveTransport 联调 | 只定义“未装配 / 硬失败”语义，不实现真实传输 |
| Trust 自动升权 | 自检通过**不得**把 Trust Level 升到可写档 |

### 0.2 本轮明确要做

1. 冻结 `RuntimeEnvelope` 字段定义与硬不变式（§1）。  
2. 给出四运行模式 × 组件能力矩阵（§2）。  
3. 定义启动自检清单：配置、Adapter 传输层、写路径硬失败、env 标签透传（§3）。  
4. 定义运行时断言与熔断：env 不一致时拒绝动作（§4）。  
5. 定义 `selfcheck_record` 最小审计字段（§5）。  
6. 对齐 G-07、Decision Packet `shadow_decision`、Trust T2/T8（§6）。  
7. 给出失败演练场景（误装配 / 混池 / 伪造回执）（§7）。  
8. 列出待决问题（§8）。

### 0.3 问题陈述

> Shadow Mode 要求 `RuntimeEnvelope(env/mode/trust_credit_allowed)` **强制透传**，防止 **LiveTransport 误装配**导致真实副作用。

对齐 `Shadow_Mode_Design` SM-R07 与 `JD_Adapter_Interface_v0.2` §7.1：

- 默认模式必须是 `MODE_READ` 或 `MODE_SHADOW_DECIDE`；  
- `MODE_LIVE_WRITE` 必须**未装配或硬失败**；  
- `CredentialProvider` 在非 LIVE 模式必须拒绝提供真实凭证；  
- 非 LIVE 强制 `dry_run=true`（G-07）；  
- 任何组件不得把 `env∈{SHADOW, SIMULATION, FIXTURE}` 改写为 `LIVE`。

本文把上述要求收成**可执行的启动自检 + 运行时熔断 + 审计记录**契约。

---

## 1. RuntimeEnvelope 字段定义与硬不变式

### 1.1 字段定义（与 Shadow_Mode_Design §3.4 对齐并展开）

```text
RuntimeEnvelope {
  // ── 身份与环境 ──
  env: enum { LIVE, SHADOW, SIMULATION, FIXTURE }
  mode: enum {
    MODE_READ,            // Live-Read：只读数据/状态/预测
    MODE_SHADOW_DECIDE,   // Shadow-Decide：完整决策记账，不外发
    MODE_SHADOW_EXEC_SIM, // Shadow-Sim：本地模拟推进，仍不触平台写
    MODE_LIVE_WRITE       // Live-Write：真实写路径（本轮禁止）
  }
  adapter_runtime: enum { FIXTURE_ONLY, SIMULATION, SANDBOX_LIVE, LIVE }
  dry_run: bool
  receipt_source: enum { PLATFORM, GATE_ONLY, LOCAL_SIM, FIXTURE }
  learning_pool: enum { LIVE_POOL, SHADOW_POOL, DROPPED }
  trust_credit_allowed: bool

  // ── 执行语义（对齐 Decision Packet / JD v0.2）──
  execution_mode: enum { LIVE, SHADOW_READ_ONLY }   // 本轮唯一允许 SHADOW_READ_ONLY
  packet_kind: enum { standard, shadow_decision }   // 影子包必须为 shadow_decision

  // ── 透传与审计 ──
  captured_at: timestamp
  envelope_id: string           // 全局唯一，建议前缀 ENV-
  session_id: string            // 运行会话；同一会话内 env/mode 不得静默漂移
  config_ref: string            // 启动配置引用（文件/哈希）
  selfcheck_ref?: string        // 启动自检记录 ID（见 §5）
  actor: string                 // 写入 envelope 的组件（如 BOOT / ADAPT / JDA）
  version: semver               // envelope 契约版本，建议 0.1.0
}
```

### 1.2 字段语义与写入责任

| 字段 | 语义 | 谁写入 | 谁只读透传 | 禁止 |
|---|---|---|---|---|
| `env` | 运行环境总标签 | 启动配置 / Bootstrapper | BDV/STATE/FE/RE/门禁/ME | 任意组件改写为 LIVE |
| `mode` | 四模式之一 | 启动配置 | 同上 | 运行中静默升级为 LIVE_WRITE |
| `adapter_runtime` | Adapter 传输能力档 | Adapter 装配点 | 上层只读 | 把 FIXTURE_ONLY 展示为 LIVE |
| `dry_run` | 是否允许平台副作用 | G-07 强制 | 写路径入口校验 | 非 LIVE 下为 false |
| `receipt_source` | 回执来源 | Adapter / Shadow Gate | Memory/Learning 过滤 | 把 LOCAL_SIM/GATE_ONLY 当 PLATFORM |
| `learning_pool` | 学习池归属 | Memory 写入口 | LE/KE 过滤 | 非 LIVE 写 LIVE_POOL |
| `trust_credit_allowed` | 是否可计 live Trust | Trust Engine 入口过滤 | 审计 | 影子样本写 true |
| `execution_mode` | 对齐 DP / JD | 组包时写入 | G-01 消费 | SHADOW 包标 LIVE |
| `packet_kind` | standard / shadow | 组包时写入 | 审计与隔离 | shadow 包标 standard 逃隔离 |
| `captured_at` / `envelope_id` | 审计锚点 | 写入方 | 全链路保留 | 缺失进入下游 |
| `session_id` / `config_ref` | 会话与配置溯源 | Bootstrapper | 自检与熔断 | 同会话 env 变更无记录 |
| `selfcheck_ref` | 自检记录指针 | Bootstrapper | 审计 | 自检未跑完仍启动写能力 |

### 1.3 硬不变式（Invariants）

> 以下任一违反，组件必须**拒绝动作**并写入熔断记录（§4），不得降级放行。

| ID | 不变式 | 依据 |
|---|---|---|
| **RE-I1** | `env != LIVE` ⇒ `learning_pool != LIVE_POOL` | Shadow §3.4 / §5 |
| **RE-I2** | `env != LIVE` ⇒ `trust_credit_allowed = false` | Shadow §3.4；Trust T2/T8 仅 live 样本 |
| **RE-I3** | `mode ∈ {MODE_SHADOW_DECIDE, MODE_SHADOW_EXEC_SIM}` ⇒ `dry_run = true` 且 `execution_mode = SHADOW_READ_ONLY` | Shadow §2.3；JD G-07 |
| **RE-I4** | `mode = MODE_LIVE_WRITE` ⇒ 必须有新 GA-DEC + Trust 达标 + `adapter_runtime=LIVE` 且 LiveTransport 已授权装配；**本轮默认恒不成立** | Shadow §2.3 / §7；JD §7 |
| **RE-I5** | `adapter_runtime ∈ {FIXTURE_ONLY, SIMULATION}` ⇒ 任何 `write(dry_run=false)` 或真实平台副作用路径必须**硬失败**（未装配或显式 throw/REJECT） | Shadow SM-R07；JD §7.1 |
| **RE-I6** | 中游组件（BDV/STATE/FE/RE/Risk/Trust/SRA/JDA）**原样透传** `env` / `mode` / `trust_credit_allowed` / `execution_mode`，禁止清洗或改写 | Shadow §5.1 |
| **RE-I7** | 出口（Memory / ActionReceipt / Episode / CausalRecord）必须携带完整 envelope；缺失或 `env` 被改写为 LIVE 的对象一律拒收 | Shadow §5.1；GIP P-01 |
| **RE-I8** | `packet_kind = shadow_decision` ⇔ `execution_mode = SHADOW_READ_ONLY`；且 ADAPT 写路径硬拒绝（可生成 `SIMULATED` / `GATE_ONLY` 回执） | DPK-I5；JD G-01 |
| **RE-I9** | `receipt_source ≠ PLATFORM` ⇒ 禁止表述为“平台已执行/成功投放”；禁止计入 live Trust（T2/T8） | GIP F-01 / P-03；Shadow §3.3 |
| **RE-I10** | 同一 `session_id` 内 `env` / `mode` / `adapter_runtime` 不得静默变更；变更必须新开会话或写 `envelope_rebind` 审计事件 | 本文自检扩展 |
| **RE-I11** | `mode = MODE_READ` ⇒ 不产出候选动作包、不触发 SRA 审批、不产生写回执 | Shadow §2.2 |
| **RE-I12** | 自检未通过（`selfcheck.status != PASS`）时，系统只能以只读或拒绝一切外发动作的方式存在 | 本文 §3 |

### 1.4 与 Shadow Gate 输出的对齐

Shadow Gate（Shadow §3.3）每次评估应**携带并校验**当前 envelope，输出建议值必须与 envelope 一致：

```text
ShadowGate.evaluate(decision, runtime_envelope) -> {
  env, mode,
  allow_platform_write,     // 非 LIVE 恒 false（RE-I3/I4/I5）
  accounting_required,      // shadow 必须 true
  receipt_policy,           // SIM_ONLY | PLATFORM
  learning_pool,
  trust_update_allowed,     // shadow 恒 false（RE-I2）
  envelope_consistent: bool // 与传入 RuntimeEnvelope 是否一致
}
```

`envelope_consistent=false` 时：记账 `RE-TRIP-*` 并**拒绝动作**（§4）。

---

## 2. 运行模式与组件能力矩阵

### 2.1 四模式总览（对齐 Shadow Mode 与 JD Runtime）

| 展示名 | `mode` | `env` 典型 | `adapter_runtime` 典型 | `execution_mode` | 本轮允许？ |
|---|---|---|---|---|---|
| Live-Read | `MODE_READ` | SHADOW / FIXTURE / SIMULATION | FIXTURE_ONLY / SIMULATION | （无包或只读） | ✅ 默认可 |
| Shadow-Decide | `MODE_SHADOW_DECIDE` | SHADOW | FIXTURE_ONLY / SIMULATION | SHADOW_READ_ONLY | ✅ **默认影子档** |
| Shadow-Sim | `MODE_SHADOW_EXEC_SIM` | SIMULATION / SHADOW | SIMULATION | SHADOW_READ_ONLY | ⚠️ 需显式开启 |
| Live-Write | `MODE_LIVE_WRITE` | LIVE | LIVE（未装配） | LIVE（本轮禁止） | ❌ 须硬失败/未装配 |

### 2.2 组件能力矩阵

| 能力 / 组件行为 | Live-Read | Shadow-Decide | Shadow-Sim | Live-Write（本轮） |
|---|:---:|:---:|:---:|:---:|
| 平台只读资源 RO-* | ✅ | ✅ | ✅ | —（禁止进入） |
| Fixture / 历史导出读取 | ✅ | ✅ | ✅ | — |
| BDV 校验（与 live 同规则） | ✅ | ✅ | ✅ | — |
| STATE 组装 / FE 预测 | ✅ | ✅ | ✅ | — |
| Reasoning 产出候选动作 | ❌ | ✅ | ✅ | — |
| Risk / Trust / SRA 门禁跑通 | ❌ | ✅ | ✅ | — |
| 组装 Decision Packet（`shadow_decision`） | ❌ | ✅ | ✅ | — |
| Adapter `write(dry_run=true)` 记账 | ❌ | ✅（强制） | ✅（强制） | — |
| 本地模拟状态推进 / 反事实 rollout | ❌ | ❌ | ✅ | — |
| 真实平台 `write(dry_run=false)` | ❌ | ❌ | ❌ | **未装配 / 硬失败** |
| LiveTransport 可实例化 | ❌ | ❌ | ❌ | **未装配** |
| CredentialProvider 提供真实凭证 | ❌ | ❌ | ❌ | **拒绝** |
| 样本写入 Shadow Pool | — | ✅ | ✅ | — |
| 样本写入 live Memory 主链 | — | ❌ | ❌ | — |
| Trust T2/T8 live 计分 | ❌ | ❌ | ❌ | 仅 LIVE 样本 |
| 影子经验晋升 Rule/Strategy/Genome | ❌ | ❌ | ❌ | 须特批（Shadow §5.4） |
| 触发网络出站到真实广告域名 | ❌ | ❌ | ❌ | **禁止** |

### 2.3 组件侧 envelope 义务（透传检查点）

| 组件 | 进入时必须校验 | 离开时必须携带 |
|---|---|---|
| Bootstrapper / Config Loader | 默认 mode ∈ {READ, SHADOW_DECIDE}；LIVE 配置需显式 GA-DEC 标记 | 写入完整 RuntimeEnvelope |
| Platform Adapter | `adapter_runtime` 与装配传输一致；非 LIVE 禁止 LiveTransport | payload / receipt 带 envelope 摘要 |
| BDV | 不伪造 PASS；透传 env | ValidationReport 带 env |
| STATE | gap_flag 显式；ready_for_forecast 语义 | BusinessState 带 env |
| FE | 仅引用 validated_id | ForecastBundle 带 env |
| RE | MODE_READ 不产动作；shadow 产完整候选 | Decision 候选带 env |
| Risk / Trust / SRA | **原样执行**，不因 shadow 放宽 | ReviewEvent / RiskAssessment 带 env |
| Shadow Gate | envelope 一致性；非 LIVE `allow_platform_write=false` | 决策分流结果 + selfcheck 关联 |
| JDA | 只消费已成包对象；不改写 env | AbstractActionRequest 带 env |
| Memory Engine | 非 LIVE → SHADOW_POOL；`trust_credit_allowed` 过滤 | Episode/CR/Receipt 保留 envelope |
| Learning / Knowledge | 按 learning_pool 分池；禁止自动晋升 | 产物带 `origin_env` |

---

## 3. 启动自检清单（Boot Self-Check）

> 目标：进程/会话在允许任何决策或写路径之前，证明 env 装配正确、传输层无误装配、写路径硬失败、标签可透传。  
> 执行者：Bootstrapper（或等价 Runtime 初始化器）。  
> 产出：一条 `selfcheck_record`（§5），写入审计，并将 `selfcheck_ref` 写入 RuntimeEnvelope。

### 3.1 自检阶段与通过条件

| 阶段 | 检查 ID | 检查项 | 通过条件 | 失败动作 |
|---|---|---|---|---|
| **S-A 配置** | SC-A1 | 默认运行模式 | 配置默认 `mode ∈ {MODE_READ, MODE_SHADOW_DECIDE}` | 拒绝启动写能力；强制 MODE_READ 或 abort |
| | SC-A2 | LIVE 显式授权 | `mode=MODE_LIVE_WRITE` 仅当存在有效 `GA-DEC-*` 引用 + Trust 门控配置 | 无授权则降级为 MODE_SHADOW_DECIDE 或 abort |
| | SC-A3 | env 与 mode 合法组合 | 满足 §1.3 RE-I1..I4 的静态组合表 | abort |
| | SC-A4 | execution_mode 唯一允许值 | 本轮配置只允许 `SHADOW_READ_ONLY` | abort |
| | SC-A5 | 凭证源 | 非 LIVE：CredentialProvider 实现为空对象且 `get()` 返回拒绝；进程环境无真实密钥加载 | abort |
| | SC-A6 | 配置可溯源 | `config_ref` 非空；含 mode/env/adapter_runtime | abort |
| **S-B Adapter 传输层** | SC-B1 | LiveTransport 装配状态 | `adapter_runtime ∈ {FIXTURE_ONLY, SIMULATION}` 时 LiveTransport **未注入**或注入为 Fail-Closed stub | abort |
| | SC-B2 | SANDBOX_LIVE / LIVE 装配 | 本轮不存在；若 DI 容器中出现 live 客户端/端点配置 → 失败 | abort + 告警 |
| | SC-B3 | 网络出口策略 | 无真实广告域名白名单；出站拦截器对非白名单/真实域 FAIL-CLOSED | abort |
| | SC-B4 | 只读能力面 | 仅暴露 RO-*；写接口在非 LIVE 下注册为硬失败包装器 | 注册失败则 abort |
| | SC-B5 | dry_run 强制点 | Adapter.write 入口存在 G-07 守卫：非 LIVE 强制改写/校验 `dry_run=true` | 守卫缺失则 abort |
| **S-C 写路径硬失败** | SC-C1 | 写路径探针 | 主动调用 `write` 干跑（Fixture/内存探针）：期望返回 `REJECTED_BY_GATE` / `SIMULATED` / 硬异常，**绝不**触达网络 | 若出现平台样式 ACK 或网络侧写 → **熔断并 abort** |
| | SC-C2 | Shadow 写拒绝 | 构造 `execution_mode=SHADOW_READ_ONLY` 的假包，期望 G-01 返回 `SHADOW_WRITE_FORBIDDEN` | 失败则 abort |
| | SC-C3 | 幂等与门禁存在性 | G-01..G-09 守卫已挂载（至少 G-01/G-03/G-07） | 缺失则 abort |
| | SC-C4 | 拒绝回执形态 | 拒绝时 status ∈ {REJECTED_BY_GATE, SIMULATED, NOT_APPLICABLE_NO_ACTION}；禁止 ACCEPTED@非 LIVE | 失败则熔断 |
| **S-D env 标签透传** | SC-D1 | 入口写入 | Adapter/Fixture 在首条 payload 写入 RuntimeEnvelope | abort |
| | SC-D2 | 中游透传探针 | 注入带唯一 `envelope_id` 的测试对象，穿过 BDV→STATE→FE→RE（或等价管道桩），出口 envelope 关键字段一致 | 不一致 → abort |
| | SC-D3 | 出口拒收 | Memory 写入口对缺失 envelope 或 `env` 被改为 LIVE 的 shadow 对象拒收 | 拒收逻辑缺失 → abort |
| | SC-D4 | Trust 过滤 | Trust 更新接口拒绝 `trust_credit_allowed=false` 的样本 | 失败 → abort |
| | SC-D5 | KE 晋升过滤 | KE 晋升接口拒绝 `env!=LIVE` 且无特批单号的候选 | 失败 → abort |
| **S-E 防污染验收（对齐 Shadow P-01..P-05）** | SC-E1 | 池隔离可配置 | Shadow Pool 与 live Memory 逻辑/物理隔离可开关且默认隔离 | 失败 → 不得进入 Shadow-Decide |
| | SC-E2 | 文案审计 | 模拟回执日志中不得出现 “platform accepted / 成功投放” | 失败 → 阻断启动或清日志后重跑 |
| | SC-E3 | 抽样审计钩子 | 提供 0 条 live 规则引用 shadow-only 证据的检查器（可空实现但接口存在） | 接口缺失 → 不得宣称防污染达标 |

### 3.2 自检结果门控

```text
selfcheck.status:
  PASS          → 允许以配置 mode 运行（仍受运行时断言约束）
  PASS_READ_ONLY→ 仅允许 MODE_READ；Shadow-Decide 能力卸载
  FAIL          → 拒绝一切决策外发；仅允许人工排障路径
  ABORT         → 进程退出或会话冻结
```

**规则：**

1. `FAIL`/`ABORT` 不得通过“跳过自检”参数绕过（除非负责人显式 break-glass，且该 break-glass 本身写入审计，不得开启 LIVE 写）。  
2. 自检探针（SC-C1/C2/D2）必须使用 Fixture/内存，**不得**依赖真实平台。  
3. 自检通过 ≠ 升权；不改变 Trust Level，不授权 MODE_LIVE_WRITE。

### 3.3 启动自检伪流程（非实现代码）

```text
boot():
  cfg = load_config()
  env_envelope = bootstrap_envelope(cfg)          # SC-A*
  record = start_selfcheck(env_envelope)

  record += check_adapter_transport(env_envelope) # SC-B*
  record += probe_write_hard_fail(env_envelope)   # SC-C*  (fixture-only probes)
  record += probe_envelope_passthrough(env_envelope) # SC-D*
  record += check_isolation_gates(env_envelope)   # SC-E*

  record.status = aggregate(record)
  persist(record)
  env_envelope.selfcheck_ref = record.id

  if record.status == PASS:
      allow(mode = env_envelope.mode)
  elif record.status == PASS_READ_ONLY:
      allow(mode = MODE_READ only)
  else:
      freeze_writes(); alert()
```

---

## 4. 运行时断言与熔断（Circuit Break）

启动自检只保证“开机时刻正确”。运行中仍可能发生配置热更新、依赖替换、bug 导致的 env 漂移。因此每个关键边界设置**断言**；断言失败即**熔断**：拒绝当前及后续写路径动作，直到人工/自动恢复并重新自检。

### 4.1 断言点

| 断言 ID | 位置 | 条件（必须为真） | 失败原因码（Proposed） |
|---|---|---|---|
| RA-01 | Adapter.write 入口 | `envelope.dry_run=true` 或（`env=LIVE` 且有授权） | `DRY_RUN_REQUIRED` / `ENVELOPE_INVALID` |
| RA-02 | Adapter.write 入口 | `execution_mode=SHADOW_READ_ONLY` ⇒ 拒绝真实写 | `SHADOW_WRITE_FORBIDDEN` |
| RA-03 | Adapter.write 入口 | LiveTransport 仅在 `adapter_runtime=LIVE` 且有 GA-DEC 时可提交 | `TRANSPORT_NOT_AUTHORIZED` |
| RA-04 | Shadow Gate | `allow_platform_write == (env==LIVE && mode==MODE_LIVE_WRITE)` | `GATE_ENVELOPE_MISMATCH` |
| RA-05 | Memory 写入口 | `learning_pool` 与 `env` 一致（RE-I1） | `POOL_MISMATCH` |
| RA-06 | Trust 更新入口 | `env!=LIVE` ⇒ 拒绝 live 计分（RE-I2） | `TRUST_CREDIT_FORBIDDEN` |
| RA-07 | KE 晋升入口 | `env!=LIVE` 且无特批 ⇒ 拒绝 | `KNOWLEDGE_PROMOTION_FORBIDDEN` |
| RA-08 | Receipt 落库 | `receipt_source` 与 `status` 兼容（PLATFORM vs SIMULATED 等） | `RECEIPT_SOURCE_MISMATCH` |
| RA-09 | 会话边界 | `env/mode/adapter_runtime` 与会话绑定值一致（RE-I10） | `ENVELOPE_DRIFT` |
| RA-10 | Decision 组包 | `packet_kind=shadow_decision` ⇔ `execution_mode=SHADOW_READ_ONLY`（RE-I8） | `PACKET_KIND_MISMATCH` |
| RA-11 | 日志/对外文案 | 非 PLATFORM 回执不得出现平台已执行语义 | `FALSE_PLATFORM_CLAIM` |
| RA-12 | 网络出口 | 非 LIVE 到真实广告域名的出站被拦截 | `EGRESS_FORBIDDEN` |

### 4.2 熔断行为

| 级别 | 触发示例 | 行为 |
|---|---|---|
| **Trip-Reject** | 单次 RA-01/02/08/10 失败 | 拒绝该动作；写 REJECTED_BY_GATE / 熔断事件；会话可继续只读 |
| **Trip-Freeze** | RA-04/05/06/07/09 重复失败，或 RA-03/12 | 冻结一切写路径与 Shadow-Decide 外发；保留只读与审计 |
| **Trip-Abort** | 启动自检 FAIL，或确认 LiveTransport 误装配已触达网络 | 冻结会话；要求重新 boot + 完整自检；告警负责人 |

```text
on_assertion_fail(a):
  log(selfcheck/circuit record)
  if a.level == Trip-Reject:
      return REJECT(current_action)
  if a.level == Trip-Freeze:
      freeze_write_paths(session)
  if a.level == Trip-Abort:
      freeze_session(); require_reboot_selfcheck()
```

### 4.3 恢复条件

1. 定位根因（配置、DI 装配、代码路径）。  
2. 修复后**重新执行完整启动自检**（§3），不得只重试断言。  
3. 新 `selfcheck_record` 为 PASS 才能解冻；解冻事件写入审计。  
4. 若曾发生疑似真实副作用（RA-12/Trip-Abort），必须人工确认无平台写后，方可回到 Shadow 档。

---

## 5. 审计：selfcheck_record 最小字段

> 每次启动自检、每次熔断、每次 envelope 重绑都应产出可检索记录。字段为**最小集**，可扩展但不得删减。

### 5.1 selfcheck_record

```text
SelfcheckRecord {
  selfcheck_id*          : string          // 前缀建议 SC-
  session_id*            : string
  envelope_id*           : string          // 关联 RuntimeEnvelope
  kind*                  : enum { BOOT, PROBE, CIRCUIT_TRIP, REBIND, AUDIT_SAMPLE }
  status*                : enum { PASS, PASS_READ_ONLY, FAIL, ABORT }
  started_at*            : timestamp
  finished_at*           : timestamp

  // ── 装配快照（自检时）──
  config_ref*            : string
  env*                   : enum
  mode*                  : enum
  adapter_runtime*       : enum
  dry_run*               : bool
  execution_mode*        : enum
  live_transport_state*  : enum { NOT_ASSEMBLED, FAIL_CLOSED_STUB, ASSEMBLED_UNAUTHORIZED, ASSEMBLED_AUTHORIZED }
  credential_state*      : enum { ABSENT, EMPTY_PROVIDER, REFUSED, PRESENT_FORBIDDEN }

  // ── 检查明细 ──
  checks*                : [{
    check_id,            // SC-*/RA-*
    phase,               // CONFIG | TRANSPORT | WRITE_PROBE | PASSTHROUGH | ISOLATION | RUNTIME
    result: PASS | FAIL | SKIPPED | WARN,
    detail,
    reason_codes[]
  }]
  failed_check_ids*      : string[]
  reason_codes*          : string[]        // 聚合原因，如 LIVE_TRANSPORT_MISASSEMBLED

  // ── 熔断与恢复 ──
  circuit_level?         : enum { NONE, TRIP_REJECT, TRIP_FREEZE, TRIP_ABORT }
  affected_actions?      : string[]        // 被拒绝的 action_id / decision_id
  recovery_selfcheck_id? : string          // 解冻所依赖的新自检
  operator_ticket_id?    : string          // 人工 break-glass / 排障单

  // ── 证据 ──
  evidence_refs*         : string[]        // 日志/探针输出引用；不含密钥
  schema_version*        : semver          // 0.1.0
  actor*                 : string          // BOOT / GATE / TE / ME / ...
}
```

### 5.2 与其他审计对象的衔接

| 对象 | 关系 |
|---|---|
| `RuntimeEnvelope.selfcheck_ref` | 指向最近一次决定当前 mode 是否放行的 BOOT 记录 |
| `ActionReceipt.audit.source_env` | 与 envelope.env 对齐；receipt 侧冗余便于过滤 |
| Decision Packet `tags` | 影子包含 `shadow`；可追加 `selfcheck:<id>` 便于溯源 |
| TRACE / ReviewEvent | 熔断事件必须写 TRACE，reason_codes 进入失败模式候选 |
| Failure Pattern | 误装配/混池/伪回执若重复出现，进入 Failure Pattern（隔离池单独标注） |

### 5.3 保留与检索要求（Proposed）

1. BOOT 记录与会话同生命周期保留；熔断记录保留至对应 Failure Pattern 归档策略（GIP-Q7 / Risk Q-R7）。  
2. 不得写入密钥、完整账户标识、买家隐私（对齐 JD §7.1）。  
3. 检索维度至少支持：`session_id`、`envelope_id`、`status`、`failed_check_ids`、`circuit_level`。

---

## 6. 与 G-07、Decision Packet、Trust T2/T8 的衔接

### 6.1 与 Adapter 门禁 G-07（及 G-01）

| 门禁 | 本文关系 |
|---|---|
| **G-07 dry_run / 环境政策** | 自检 SC-B5 证明守卫存在；运行时 RA-01 每次写入口强制。非 LIVE 或 `execution_mode=SHADOW_READ_ONLY` ⇒ `dry_run` 必须 true，否则 `DRY_RUN_REQUIRED`。 |
| **G-01 决策包有效** | `execution_mode=SHADOW_READ_ONLY` 时写路径硬拒绝（`SHADOW_WRITE_FORBIDDEN`）；与 RA-02、SC-C2 一致。双字段（lifecycle_status + review_result）仍按 JD v0.2 执行，本文不弱化。 |
| **G-03 Risk 约束** | 熔断不替代 Risk；即使 envelope 正确，hard_block 仍拒绝。 |
| **G-02 Trust** | 非 LIVE 下影子可在较低 Trust 运行以演练，但 **不得** 因影子表现提升 live Trust Level（见 6.3）。 |

### 6.2 与 Decision Packet `shadow_decision`

| 检查点 | 规则 |
|---|---|
| 成包 | Shadow-Decide 仍必须完整 Decision Packet（DPK-I1/I2 语义），`packet_kind=shadow_decision`。 |
| 执行语义 | `execution_mode=SHADOW_READ_ONLY`；与 RuntimeEnvelope.execution_mode **必须一致**（RA-10）。 |
| 回执 | 仅允许 `SIMULATED` / `NOT_APPLICABLE_NO_ACTION` / `REJECTED_BY_GATE`；`receipt_source ∈ {GATE_ONLY, LOCAL_SIM, FIXTURE}`。 |
| 对照 | `shadow.compare_to_live_decision_id` 可选；对照评估产物仍标 shadow-eval，不写 live Trust。 |
| 学习 | `shadow.learning_pool` 默认 `isolated`；与 envelope.learning_pool 一致。 |

### 6.3 与 Trust T2 / T8

| 维度 | 含义（Risk 文档） | 本文约束 |
|---|---|---|
| **T2 调整后达成率** | 已批准动作在响应窗口内达成预期方向/幅度的比例 | **仅 LIVE 样本**可计入 live T2；影子/模拟/fixture 回执一律隔离（RE-I2/I9，RA-06）。影子可维护 `shadow_trust_proxy`，**不映射** live Level。 |
| **T8 自审批准确性** | APPROVE 后成功 vs 误放行；REJECT/HOLD 后的误杀/应放行 | 影子 SRA 结果用于**校准反事实 APPROVE 率**与误拒代理（Shadow SM-M06/M07），默认**不计入** live T8。若运营“参考执行”影子建议，须补人工 Decision 记录（Shadow SM-Q5），否则不得当作 live 达成。 |

**过滤伪逻辑（对齐 Shadow §5.3，便于实现对齐）：**

```text
on_trust_update(signal):
  if signal.envelope.trust_credit_allowed == false:
      record(signal, pool=SHADOW_POOL)
      return   # 不更新 live TS / Level

on_t2_t8_sample(packet):
  if packet.envelope.env != LIVE:
      shadow_only_pool.add(packet)
      return
  live_trust_pool.add(packet)
```

### 6.4 端到端一致性链（摘要）

```text
Config(mode/env)
  → RuntimeEnvelope (boot)
  → SelfcheckRecord (PASS)
  → Shadow Gate (envelope_consistent)
  → Decision Packet (shadow_decision + SHADOW_READ_ONLY)
  → Adapter G-07/G-01 (dry_run / write reject)
  → ActionReceipt (SIMULATED | GATE_ONLY, source_env)
  → Memory (SHADOW_POOL)
  → Trust (reject live credit)
  → KE (no auto-promotion)
```

任一环不一致 → 对应 RA-* 熔断 → selfcheck/circuit 审计。

---

## 7. 失败演练场景（Drill Scenarios）

> 演练必须在 Fixture/内存中进行，禁止触达真实平台。目的：证明断言与自检能抓住 SM-R07 及相关失败模式。

### 7.1 场景总表

| 场景 ID | 名称 | 注入方式 | 期望检测点 | 期望结果 | 对齐失败模式 |
|---|---|---|---|---|---|
| **DR-01** | LiveTransport 误装配 | DI 错误注入 live 客户端，但 mode=SHADOW | SC-B1/B2、RA-03、RA-12 | 启动 FAIL 或 Trip-Abort；写路径硬失败；审计 `LIVE_TRANSPORT_MISASSEMBLED` | SM-R07；GIP B-03 |
| **DR-02** | dry_run 被绕过 | 调用 `write(dry_run=false)` | SC-B5、RA-01、G-07 | `DRY_RUN_REQUIRED` / REJECTED_BY_GATE | GIP #17 |
| **DR-03** | Shadow 包被标 LIVE | 篡改 packet.execution_mode | RA-10、G-01 | `PACKET_KIND_MISMATCH` / `SHADOW_WRITE_FORBIDDEN` | DPK-I5 |
| **DR-04** | envelope 中游清洗 | 组件把 env 改为 LIVE | SC-D2、RA-09 | 熔断；出口拒收；不一致日志 | Shadow §5.1；RE-I6 |
| **DR-05** | 学习混池 | shadow 回执写入 LIVE_POOL | SC-D3/E1、RA-05 | `POOL_MISMATCH`；样本回退 SHADOW_POOL | SM-R01；JD-Q10 |
| **DR-06** | Trust 偷计分 | 影子达成率写入 live T2/T8 | SC-D4、RA-06 | `TRUST_CREDIT_FORBIDDEN`；分数不变 | RE-I2；GIP P-02/P-03 |
| **DR-07** | 伪造 ACCEPTED 回执 | 非 PLATFORM 来源写 status=ACCEPTED | RA-08、RA-11 | 拒收或改判 SIMULATED；禁平台文案 | GIP F-01 |
| **DR-08** | 伪造 ValidationReport=PASS | 非 BDV 组件写 PASS | BDV 边界 + 门禁 | 拒收；审计异常 | GIP F-03 |
| **DR-09** | 自检跳过参数 | 尝试 `--skip-selfcheck` 写路径 | §3.2 规则 | 仍 freeze_writes；break-glass 需 ticket | RE-I12 |
| **DR-10** | 会话中途升 mode | 热更新 mode→LIVE_WRITE | RA-09、RE-I10 | `ENVELOPE_DRIFT`；需新会话+新自检+授权 | RE-I10 |
| **DR-11** | 凭证误挂载 | 环境注入平台 secret | SC-A5 | credential_state=PRESENT_FORBIDDEN → abort | JD §7.1 |
| **DR-12** | 影子建议被外传执行 | 无 Decision 记录的口头改价 | 治理流程（非代码） | 审计缺失；不得计 T2/T8；补人工包或禁止 | SM-R09；SM-Q5 |

### 7.2 演练通过准则

1. 每个场景至少触发**一个**预定检测点，且写路径**零**真实副作用。  
2. 每次演练产生 `SelfcheckRecord`（`kind=PROBE` 或 `CIRCUIT_TRIP`）。  
3. 演练结果进入影子评估报告；**不**自动修改生产阈值。  
4. DR-01/DR-07/DR-06 为**一票否决级**：任一失败不得宣称 Shadow Mode 可用。

### 7.3 演练与 SM-M10

连续演练与运行日应统计：`隔离完整率 SM-M10 = 零 live 污染事件`。失败演练若造成污染尝试，必须记录为“已拦截的污染事件”，与“未拦截污染”区分——前者不降低 SM-M10 前提是拦截成功。

---

## 8. 待决问题

| ID | 问题 | 建议 | 阻塞 |
|---|---|---|---|
| RE-Q1 | Shadow Pool 与 live Memory 是逻辑库还是物理库？（承接 SM-Q1） | 先逻辑隔离 + 硬查询视图；自检 SC-E1 按逻辑隔离验收 | 否 |
| RE-Q2 | envelope 是否需要签名/防篡改？（承接 GIP-Q5） | 本轮不需要；LIVE 阶段评估 | 否 |
| RE-Q3 | break-glass 跳过自检的审批人与票据格式？ | 项目负责人；必须 `operator_ticket_id`；仍禁止开启 LIVE 写 | 是（治理） |
| RE-Q4 | `shadow_trust_proxy` 公式是否纳入本文？ | 不纳入；仅约定不得映射 live T2/T8（见 SM-Q2） | 否 |
| RE-Q5 | 多租户下 envelope 是否强制含 tenant_id？ | 建议 boot 时注入；与 DP tenant_id 对齐 | 否 |
| RE-Q6 | 抖音侧是否复用同一 envelope 与 selfcheck？ | 是；扩展字段后置（承接 SM-Q7 / JD-Q9） | 否 |
| RE-Q7 | 自检探针是否允许在 CI 中默认跑？ | 是，必须 CI 跑 SC-B/C/D；生产 boot 再跑一遍 | 否 |
| RE-Q8 | Gate Playbook 中 G-07/失败模式表是否需引用本文 RA/SC ID？ | 建议 GIP v0.2（GA2-T19）反向引用，避免两套编号漂移 | 否（文档同步） |

---

## 9. 理论追踪（工程派生，不新增理论）

| 本文章节 | GA-1 / 主线锚点 | 相关详设 | 覆盖 |
|---|---|---|---|
| §1 envelope 不变式 | GA-DEC-004 红线；架构 P3/P7 | Shadow §3.4；JD §7 | Mapped |
| §2 模式矩阵 | Shadow 四模式；权限随信任生长 | Shadow §2；Risk §5 | Mapped |
| §3 启动自检 | Shadow SM-R07 缓解 | JD §7.1 LiveTransport 硬失败 | Mapped |
| §4 熔断 | 自审批前置；失败即学习 | Gate §6 失败模式；Risk §6.6 TRACE | Mapped |
| §5 审计字段 | 架构 §6 决策包/TRACE | Gate §7 审计最小集 | Mapped |
| §6 G-07 / shadow_decision / T2 T8 | 门禁顺序；Trust 真实经营验证 | JD G-07；DPK-I5；Risk §4.2 | Mapped |
| §7 失败演练 | 防污染验收 P-01..P-05 | Shadow §5.5；Gate §6.2/6.3 | Mapped |

**明确不声称：** 本文不提供真实平台接入、不证明反事实决策必然成功、不授权写权限、不修改 GA-1。

---

## 10. 与后续任务的接口

| 下游 | 本文供给 |
|---|---|
| GA2-T19 Gate Playbook v0.2 | RA-*/SC-* 与 G-07、失败模式表的交叉引用 |
| GA2-T20 DP/JD 样例迁移 | envelope 在 Fixture 样例中的落点与 receipt.source_env |
| GA2-T15 参数预标定 | 自检通过后的 mode 选择；不直接提供阈值 |
| 实现（Adapter/SRA/ME） | 启动自检清单、断言表、selfcheck_record schema |
| GA-3 / 升权评审 | SM-M10 与 DR 演练证据可作为 S4 防污染审计材料（仍须负责人评审） |

---

## 11. 变更记录

| 日期 | 版本 | 变更 | 依据 |
|---|---|---|---|
| 2026-09-11 | v0.1 | 首次建立 Runtime Envelope 自检设计：字段与不变式、四模式能力矩阵、启动自检、运行时熔断、selfcheck_record、G-07/DP/Trust 衔接、失败演练、待决问题 | GA2-T21；Shadow_Mode_Design；JD_Adapter v0.2；Gate_Integration_Playbook；Decision_Packet_Schema；Risk_Trust_SelfReview；Architecture v0.2；GA-DEC-004 |

---

**Document Status:** Draft  
**Next Review:** 项目负责人 / Research Architect  
**Explicit Non-claim:** 本文不代表已接入真实京东账户；未提供任何凭证或可执行投放脚本；未修改 GA-1；自检与熔断通过**不**授予 Live-Write 权限，也**不**提升 live Trust Level。
