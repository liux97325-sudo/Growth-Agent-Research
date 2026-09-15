# GA-2：模块边界与代码骨架设计

**文档编号：** GA-2-SKEL-001  
**任务编号：** GA2-T28  
**版本：** v0.1  
**状态：** Draft  
**阶段：** GA-2 Engineering Design（GA-DEC-005 后设计轮）  
**输入基线：** `Research/GA-1/GA-1_Theory_v1.0.md`（GA-1.0 / v1.0，Confirmed）  
**主线架构：** `Architecture_Overview_v0.2.md`（Confirmed，GA-DEC-004）  
**工程基线：** `GA-2.0_Baseline_Package.md`（**Confirmed**，GA-DEC-005）  
**强关联：**  
- `Decision_Packet_Schema_v0.1.md`（成长最小原子）  
- `Gate_Integration_Playbook_v0.2.md`（双字段可执行判定）  
- `JD_Adapter_Interface_v0.2.md`（RO/RW 契约、G-01–G-09）  
- `Runtime_Envelope_Selfcheck_v0.1.md`（envelope / 自检 / 熔断）  
- `Learning_Reflection_Runtime_v0.1.md`（回路 B 编排）  
- `Forecast_Engine_Interface_v0.1.md` / `Reasoning_Engine_Interface_v0.1.md`  
**授权依据：** GA-DEC-004 + GA-DEC-005  
**作者角色：** Research Engineer 子代理  
**约束：** 本文为**模块边界与代码骨架**设计（非完整实现）。不修改 GA-1 / PROJECT_SPEC；不写完整业务实现代码；不引入真实 SDK/凭证；默认技术选型一律 **Proposed**，不绑死框架；全部阈值与默认值一律 **Proposed**。

---

## 0. 范围声明

### 0.1 本轮要做

1. 给出逻辑模块图：`core` / `domain` / `edge` / `asset` / `gate` / `runtime`。  
2. 给出推荐 monorepo 目录树（骨架级，无业务实现）。  
3. 定义模块职责与**禁止依赖方向**（依赖规则）。  
4. 给出关键接口签名草案（Python/TypeScript 伪代码）：DecisionPacket、ForecastBundle、RiskEval、TrustEval、SRAReview、Adapter RO/RW。  
5. 定义配置与 `RuntimeEnvelope` 装配点。  
6. 给出测试分层建议（unit / contract / fixture / shadow-sim）。  
7. 明确不在本骨架范围的内容与待决问题。

### 0.2 本轮明确不做

- 不实现任何引擎的业务算法（预测模型、推理策略、Trust 公式、风险分档实现细节）。  
- 不接入真实京东/抖音 API、不创建凭证、不写可执行投放脚本。  
- 不选型并绑定数据库 / MQ / Web 框架 / ORM（只给逻辑边界与接口）。  
- 不修改 GA-1 理论、PROJECT_SPEC、Architecture v0.2 主线。  
- 不设计 GA-3 实验执行方案。

### 0.3 术语与图例约定

| 记号 | 含义 |
|---|---|
| **M-*** | 逻辑模块 ID（如 M-CORE-RE） |
| **Pkg-*** | 建议代码包/目录前缀 |
| `-->` | 允许依赖（编译期或运行期调用/注入） |
| `-.->` | 仅事件/审计/只读引用，不构成业务编排依赖 |
| `X` | **禁止**依赖（见 §3 依赖规则） |
| Proposed | 工程草案，非已验证真值 |

---

## 1. 逻辑模块图

> 对齐 Architecture_Overview_v0.2 §3 总体结构与 §5 组件边界；将“组件”收敛为可落代码的**六个逻辑层**。

```text
                          ┌─────────────────────────────────────┐
                          │            治理与配置（Config）         │
                          │  RuntimeEnvelope / Selfcheck / 阈值表   │
                          └──────────────────┬──────────────────┘
                                             │ 装配注入（Boot）
     ┌───────────────────────────────────────▼───────────────────────────────────────┐
     │                              runtime（M-RUNTIME）                                │
     │  Bootstrapper · Session · Orchestrator(RFE/LE) · CircuitBreaker · Selfcheck     │
     └───────────────┬───────────────────────────────┬───────────────────────────────┘
                     │ 编排/装配                        │ 编排（回路 B）
                     ▼                                 ▼
     ┌───────────────────────────────┐   ┌───────────────────────────────────────────┐
     │         core（M-CORE）          │   │              asset（M-ASSET）              │
     │  CBA · FE · RE · OFG           │   │  AuditLog/TRACE · Cases · Experiences      │
     │  ME · LE · KE · RFE            │   │  Rules · Strategies · Genomes · Capabilities│
     │  （纯逻辑引擎，无 I/O 副作用）     │   │  （版本化企业数字资产；只追加/治理晋升）        │
     └───────────────┬───────────────┘   └───────────────────▲───────────────────────┘
                     │ DecisionPacket Draft / 只读知识引用        │ 晋升候选（经 KE 治理）
                     ▼                                         │
     ┌───────────────────────────────┐                         │
     │         gate（M-GATE）          │  唯一写 review_result    │
     │  RKE · TE · SRA                │─────────────────────────┤
     │  （风险硬红线 + 信任门控 + 终审）  │  Trust 信号（仅 LIVE）    │
     └───────────────┬───────────────┘                         │
                     │ Self-reviewed 包                         │
                     ▼                                         │
     ┌───────────────────────────────┐                         │
     │        domain（M-DOMAIN）       │  已批准 Packet → 编排动作   │
     │  JDA（京东） · DYA（抖音占位）    │  -.-> Asset 审计写入        │
     └───────────────┬───────────────┘                         │
                     │ AbstractAction / ResourceQuery           │
                     ▼                                         │
     ┌───────────────────────────────┐                         │
     │         edge（M-EDGE）          │  平台 I/O 唯一边界          │
     │  ADAPT · BDV · STATE           │  Raw → Validated → Trusted│
     └───────────────┬───────────────┘                         │
                     │（本轮：Fixture / Mock only）              │
                     ▼                                         │
              [平台侧 / Fixture 存储] ───────────────────────────┘
```

### 1.1 六层一览

| 层 | 模块 ID | 含义 | 对应架构组件（节选） |
|---|---|---|---|
| **core** | M-CORE | Growth OS 核心能力引擎：协调、预测、推理、目标函数、记忆/学习/知识/反思 | CBA, FE, RE, OFG, ME, LE, KE, RFE |
| **gate** | M-GATE | 门禁与信任：风险、信任、自审批终审 | RKE, TE, SRA |
| **domain** | M-DOMAIN | 场景执行体：计划类型语义、动作编排 | JD Agent, Douyin Agent（占位） |
| **edge** | M-EDGE | 边缘接入：平台适配、数据校验、状态组装 | ADAPT, BDV, STATE |
| **asset** | M-ASSET | 企业数字资产：审计、案例、经验、规则、策略、基因、能力 | Audit/Decision Log, Cases, … Capabilities |
| **runtime** | M-RUNTIME | 运行时：启动装配、会话、编排器、自检、熔断 | Bootstrapper, Selfcheck, CircuitBreaker, RFE/LE Orchestrator |

### 1.2 与四条主回路的映射

| 回路 | 骨架主路径（模块序列） |
|---|---|
| A 经营决策 | edge(RO→BDV→STATE) → core(FE→RE) → gate(RKE→TE→SRA) → core(CBA) → domain(JDA) → edge(ADAPT) → asset(Audit) |
| B 经验蒸馏 | asset(Audit) → core(ME→RFE→LE) → core(KE 提交通道) |
| C 知识演化 | core(LE→KE) → asset(Rule/Strategy/Genome/Capability) → 反哺 core(RE/CBA) |
| D 信任与自治 | gate(TE) 消费 asset(Audit)/RFE 信号 → 回写 Trust Level → 约束 gate(SRA)/domain 动作半径 |

---

## 2. 推荐仓库目录结构（monorepo 风格）

> **Proposed**：语言中立 monorepo；以下以 Python 包布局示意（TypeScript 等价见 §2.2）。目录名即逻辑边界；**骨架阶段允许大量 `# TODO: interface only` 与 Protocol/ABC 占位，禁止填入真实业务算法与凭证。**

### 2.1 Python 主布局（Proposed）

```text
garp/
├── README.md
├── pyproject.toml                 # workspace 根；工具链 Proposed（uv/ruff/pytest）
├── Makefile                       # lint / test / selfcheck 入口（无真实网络）
│
├── docs/                          # 仅工程注释与 ADR 链接；不替代 Research/GA-2 文档
│   └── adr/                       # Architecture Decision Records（可选）
│
├── configs/                       # 配置与阈值表（全部 Proposed）
│   ├── default.yaml               # 默认 runtime：MODE_SHADOW_DECIDE / FIXTURE_ONLY
│   ├── envelopes/                 # RuntimeEnvelope 样例（无 LIVE）
│   ├── risk_baselines/            # 风险基线占位（符号化，待 GA2-T07）
│   ├── trust_thresholds/          # Trust 门限占位
│   └── objective_templates/       # OFG 目标模板（T-MHB-* 等）
│
├── schemas/                       # 与文档 Schema 对齐的 JSON Schema / 类型源
│   ├── decision_packet/
│   │   └── 0.1.0.json             # 对齐 Decision_Packet_Schema_v0.1 §9
│   ├── forecast_bundle/
│   ├── risk_assessment/
│   ├── trust_snapshot/
│   ├── review_event/
│   ├── action_receipt/
│   ├── runtime_envelope/
│   └── selfcheck_record/
│
├── packages/
│   ├── garp_contracts/            # ★ 纯类型/协议/枚举；零业务逻辑；零 I/O
│   │   ├── __init__.py
│   │   ├── ids.py                 # DecisionId, ActionId, ... 强类型别名
│   │   ├── enums.py               # LifecycleStatus, ReviewResult, RiskLevel, ...
│   │   ├── packet.py              # DecisionPacket 及子对象
│   │   ├── forecast.py            # ForecastBundle / ForecastObject
│   │   ├── gate.py                # RiskEval / TrustEval / SRAReview
│   │   ├── adapter.py             # ResourceQuery / AbstractAction / Receipt
│   │   ├── memory.py              # CausalRecord / Episode / WorkingContext
│   │   ├── knowledge.py           # ExperienceCandidate / Rule/Strategy ref
│   │   ├── envelope.py            # RuntimeEnvelope / SelfcheckRecord
│   │   ├── cba.py                 # CBAPort / DecisionTask / CBAContext
│   │   └── objective.py           # OFGPort / ObjectiveSnapshot
│   │
│   ├── garp_core/                 # M-CORE：能力引擎（无平台 I/O）
│   │   ├── cba/                   # 唯一最高协调者
│   │   ├── forecast/              # FE
│   │   ├── reasoning/             # RE
│   │   ├── objective/             # OFG
│   │   ├── memory/                # ME
│   │   ├── reflection/            # RFE
│   │   ├── learning/              # LE
│   │   └── knowledge/             # KE（治理与索引，不含平台）
│   │
│   ├── garp_gate/                 # M-GATE
│   │   ├── risk/                  # RKE
│   │   ├── trust/                 # TE
│   │   └── self_review/           # SRA（唯一写 review_result）
│   │
│   ├── garp_domain/               # M-DOMAIN
│   │   ├── jd_ad/                 # 京东 Domain Agent
│   │   └── douyin_ops/            # 占位包（仅接口桩）
│   │
│   ├── garp_edge/                 # M-EDGE
│   │   ├── adapter/               # ADAPT：RO/RW 门禁壳 + FixtureTransport
│   │   ├── validation/            # BDV
│   │   └── state/                 # STATE Assembler
│   │
│   ├── garp_asset/                # M-ASSET：资产端口 + 内存/Fixture 实现
│   │   ├── ports/                 # 存储/检索 Protocol
│   │   ├── audit/                 # TRACE / Decision Log
│   │   └── fixtures/              # 本地资产样例（非企业真值）
│   │
│   └── garp_runtime/              # M-RUNTIME
│       ├── bootstrap/             # Bootstrapper + 装配
│       ├── selfcheck/             # SC-* 检查器
│       ├── circuit/               # RA-* 断言与熔断
│       ├── orchestrator/          # RFE/LE 任务编排（逻辑独立）
│       └── session/               # Session / envelope 绑定
│
├── apps/                          # 可运行入口（仍禁止真实平台副作用）
│   ├── cli/                       # 本地演练：selfcheck / shadow-decide / fixture-replay
│   └── worker/                    # RFE/LE worker 进程入口（Proposed）
│
├── adapters/                      # 边界适配实现（与 packages 分离，便于替换）
│   ├── transport/
│   │   ├── fixture/               # 默认：本地 Fixture 只读
│   │   ├── simulation/            # 可选：本地状态机
│   │   └── live/                  # ★ 仅接口占位；默认未装配 / Fail-Closed stub
│   └── providers/                 # 订单/库存/活动等可插拔 Provider 桩
│
├── fixtures/                      # FX-01…FX-10 等设计 Fixture（JD §2.4）
│   ├── fx01_seeding_intraday_drop/
│   ├── fx02_harvest_no_action/
│   └── ...
│
├── tests/
│   ├── unit/                      # 纯函数与状态机
│   ├── contract/                  # Schema / 接口契约
│   ├── fixture/                   # Fixture 回放与 BDV 规则
│   └── shadow_sim/                # 影子闭环集成（无写）
│
└── tools/
    ├── schema_codegen.py          # schemas/ → 类型（可选，Proposed）
    └── lint_deps.py               # 依赖方向静态检查（见 §3.4）
```

### 2.2 TypeScript 等价要点（Proposed，不绑定 monorepo 工具）

若选择 TS 前端/全栈演练界面，仅建议并行包：

```text
packages/contracts/     → 对齐 garp_contracts（zod / typebox 任选，Proposed）
packages/simulator/     → 浏览器内 shadow-sim UI（只消费 Fixture）
```

**硬约束：** TS 包不得成为门禁或写路径权威；权威判定始终在 Python `garp_gate` / `garp_edge`（或未来单一权威实现），避免双实现漂移（见 §8 SK-Q03）。

### 2.3 目录级归属速查

| 逻辑层 | 主要目录 |
|---|---|
| core | `packages/garp_core/**` |
| gate | `packages/garp_gate/**` |
| domain | `packages/garp_domain/**` |
| edge | `packages/garp_edge/**`, `adapters/**` |
| asset | `packages/garp_asset/**`, `fixtures/**` |
| runtime | `packages/garp_runtime/**`, `apps/**`, `configs/**` |
| 契约 | `packages/garp_contracts/**`, `schemas/**` |

---

## 3. 模块职责与禁止依赖方向

### 3.1 职责表（骨架级）

| 模块 | 主责（做什么） | 禁止（不做什么） |
|---|---|---|
| **garp_contracts** | 类型、枚举、Schema 对齐、纯校验函数 | 任何 I/O、任何业务策略、任何框架绑定 |
| **garp_core.cba** | 唯一最高协调者：组包、下发 domain、推进生命周期 | 直接调平台；写 `review_result` |
| **garp_core.forecast** | Trusted State → ForecastBundle；置信度与降级 | 拍板动作；消费 Raw 指标 |
| **garp_core.reasoning** | State+Forecast+Objective+Knowledge → 候选/NO_ACTION | 绕过门禁；写审批字段；执行 |
| **garp_core.objective** | 动态目标权重生成 | 固定全局 ROI |
| **garp_core.memory** | Audit 流 → CausalRecord / Episode | 直接晋升企业规则 |
| **garp_core.reflection** | 复盘编排产物：Report / Finding | 直接改 Rule/Trust 本体 |
| **garp_core.learning** | 蒸馏 ExperienceCandidate；提案 | 跳过质量门禁入库 |
| **garp_core.knowledge** | 版本化治理、索引、晋升/观察/丢弃 | 无版本覆盖历史 |
| **garp_gate.risk** | 分档、hard_block、constraints | 生成动作；放宽 Trust |
| **garp_gate.trust** | Trust Score/Level、能力门控 | 替代审批；无证据升权 |
| **garp_gate.self_review** | 多维谓词终审；**唯一写 `review_result`** | 执行写操作；静默改动作 |
| **garp_domain.jd_ad** | plan_mode 语义、动作编排、三阶段记录触发 | 自建旁路凭证；改双字段 |
| **garp_edge.adapter** | RO 读取 / RW 硬闸 G-01–G-09；字段映射壳 | 经营判断；伪造 ValidationReport |
| **garp_edge.validation** | BDV：Raw → Validated | 把未校验数据标 PASS |
| **garp_edge.state** | 组装 BusinessState；gap_flags | 静默补缺失 |
| **garp_asset** | 审计与知识资产端口 | 业务决策 |
| **garp_runtime** | 装配、自检、熔断、RFE/LE 编排 | 生成业务结论；开 LIVE 写 |

### 3.2 依赖方向图（允许边）

```text
                    configs / schemas
                           │
                           ▼
                    garp_runtime  ──────────────┐
                     │        │                │
          ┌──────────┘        └──────────┐     │
          ▼                              ▼     │
     garp_core  ──(只读 Knowledge 端口)──► garp_asset
          │                              ▲     │
          │ DecisionPacket Draft         │     │
          ▼                              │     │
     garp_gate  ──审计事件-.───────────────┤     │
          │ Self-reviewed Packet         │     │
          ▼                              │     │
     garp_domain ──AbstractAction──► garp_edge ──► adapters/transport
          │                              │           (fixture|sim|live-stub)
          └──────── Audit/Receipt -.─────┘
                                     
     garp_contracts ◄── 被以上所有包 import（仅类型/协议，无反向依赖）
```

### 3.3 禁止依赖（硬规则）

| ID | 禁止边 | 理由 / 依据 |
|---|---|---|
| **D-01** | `garp_contracts` → 任何业务包 | 契约必须零依赖，防循环 |
| **D-02** | `garp_core.*` → `garp_edge.adapter` 写句柄 | GIP B-04；L2 不得持有写能力 |
| **D-03** | `garp_edge.adapter` → `garp_core.memory` / `garp_core.knowledge` 直写 | 须经 Trace/ME 既定路径（JD §1.5） |
| **D-04** | `garp_domain` → 绕过 `garp_gate` 修改 `review_result` | GIP C5：仅 SRA 可写 |
| **D-05** | 任何包 → 伪造 ValidationReport=PASS | JD §5；GIP F-03 |
| **D-06** | `garp_core.learning` → `garp_asset` 知识库直写 | 须经 KE IF-LE-01（LRR §5） |
| **D-07** | `adapters/transport/live` 在非 LIVE envelope 下被装配 | RE-I5；LiveTransport Fail-Closed |
| **D-08** | `garp_runtime` → 生成候选动作 / 改审批结果 | 编排不是决策 |
| **D-09** | `garp_gate.trust` ← Shadow 样本直接改 live 分 | RE-I2 / RA-06 |
| **D-10** | 业务包 → `configs` 中硬编码密钥 | 无凭证（硬约束） |
| **D-11** | domain 互调（JDA ↔ DYA） | 均由 CBA 协调；场景可插拔（架构 P8） |
| **D-12** | 测试/工具 → 真实广告域名出站 | SC-B3；本轮禁止 |

### 3.4 依赖检查（骨架工具位）

`tools/lint_deps.py`（Proposed）：基于 import 图校验 §3.3；CI 必跑。语义等价于“编译期架构测试”。

---

## 4. 关键接口签名草案

> 伪代码：以 Python `Protocol` / `TypedDict` 风格表达；TS 可用 `interface` 一一映射。  
> **非实现**：方法体仅注释说明前置/后置条件与不变式。  
> 枚举与字段名对齐 Decision_Packet_Schema / GIP v0.2 / JD v0.2 / RE Selfcheck。

### 4.0 公共基础（garp_contracts）

```python
# packages/garp_contracts/enums.py  (interface only)
class LifecycleStatus(Enum):
    DRAFT = "Draft"
    SELF_REVIEWED = "Self-reviewed"
    EXECUTED = "Executed"
    OBSERVED = "Observed"
    REFLECTED = "Reflected"
    ARCHIVED = "Archived"
    SUPERSEDED = "Superseded"

class ReviewResult(Enum):
    APPROVE = "APPROVE"
    NO_ACTION_APPROVE = "NO_ACTION_APPROVE"
    REVISE = "REVISE"
    HOLD = "HOLD"
    REJECT = "REJECT"
    ESCALATE_HUMAN = "ESCALATE_HUMAN"

class ExecutionMode(Enum):
    LIVE = "LIVE"
    SHADOW_READ_ONLY = "SHADOW_READ_ONLY"   # 本轮唯一允许

class PacketKind(Enum):
    STANDARD = "standard"           # canonical（DPK/JD）；勿用 live_decision
    SHADOW_DECISION = "shadow_decision"

class RiskLevel(Enum):
    R0, R1, R2, R3, R4 = "R0", "R1", "R2", "R3", "R4"

class ReceiptStatus(Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED_BY_PLATFORM = "REJECTED_BY_PLATFORM"
    REJECTED_BY_GATE = "REJECTED_BY_GATE"
    TIMEOUT = "TIMEOUT"
    UNKNOWN = "UNKNOWN"
    SIMULATED = "SIMULATED"
    NOT_APPLICABLE_NO_ACTION = "NOT_APPLICABLE_NO_ACTION"

class EnvLabel(Enum):
    LIVE = "LIVE"
    SHADOW = "SHADOW"
    SIMULATION = "SIMULATION"
    FIXTURE = "FIXTURE"
    HUMAN = "HUMAN"   # GA-DEC-006 canonical 含 HUMAN
```

### 4.0.1 CBAPort / OFGPort（对齐 CBA_OFG_Interface_v0.1）

```python
# packages/garp_contracts/cba.py
class CBAPort(Protocol):
    def orchestrate(self, ctx: CBAContext) -> DecisionTaskResult:
        """唯一最高协调者：OFG→FE→RE→Gate→Domain 时序；不直写 review_result。"""

# packages/garp_contracts/objective.py
class OFGPort(Protocol):
    def build_snapshot(self, req: ObjectiveRequest) -> ObjectiveSnapshot:
        """动态目标函数；只产权重/偏置/解释，不产动作。"""
```

依据：`CBA_OFG_Interface_v0.1.md`（GA-DEC-005 后扩展）。

### 4.1 DecisionPacket

```python
# packages/garp_contracts/packet.py
@dataclass(frozen=True)  # 逻辑不可变；状态迁移返回新实例或受控变更 API
class DecisionPacket:
    decision_id: str
    schema_version: str          # semver, e.g. "0.1.0"
    revision: int
    status: LifecycleStatus      # 生命周期（不是审批结果）
    packet_kind: PacketKind
    execution_mode: ExecutionMode
    tenant_id: str
    shop_id: str
    domain: str                  # "JD_AD" | "DOUYIN_OPS"
    episode_id: str
    created_at: datetime
    updated_at: datetime
    # 决策输入快照（冻结后不可改）
    objective_snapshot: ObjectiveSnapshot
    state_digest: StateDigest
    forecast_ref: ForecastRef
    hypothesis: Hypothesis
    proposed_actions: list[ProposedAction]     # minItems=1
    expected_response_window: ResponseWindow
    # 门禁子对象
    risk: RiskEval                 # §4.3
    trust: TrustEval               # §4.4
    review: SRAReview | None       # §4.5；Self-reviewed 起必填
    # 回填槽
    action_receipts: list[ActionReceipt]
    outcome_ref: OutcomeRef | None
    reflection_ref: ReflectionRef | None
    causal_ids: list[str]
    tags: list[str]

class DecisionPacketPort(Protocol):
    """包状态机端口：唯一推进生命周期的入口。"""

    def create_draft(self, draft: DecisionPacketDraft) -> DecisionPacket:
        """前置：字段校验通过。后置：status=DRAFT；写入 Audit。"""

    def attach_risk(self, decision_id: str, risk: RiskEval) -> DecisionPacket:
        """RKE 写入；进入后 risk 冻结。"""

    def attach_trust(self, decision_id: str, trust: TrustEval) -> DecisionPacket:
        """TE 写入；trust 冻结。"""

    def apply_review(self, decision_id: str, review: SRAReview) -> DecisionPacket:
        """仅 SRA 可调用。后置：status→SELF_REVIEWED；review_result 写入且只读。"""

    def mark_executed(self, decision_id: str, receipts: list[ActionReceipt]) -> DecisionPacket:
        """执行链推进；hypothesis/actions/objective 不可原地覆盖（DPK-I7）。"""

    def mark_observed(self, decision_id: str, outcome: OutcomeRef) -> DecisionPacket: ...

    def mark_reflected(self, decision_id: str, reflection: ReflectionRef) -> DecisionPacket: ...

    def archive(self, decision_id: str, reason: str) -> DecisionPacket: ...

    def supersede(self, old_id: str, new_id: str) -> DecisionPacket:
        """禁止对 EXECUTED 包做“无痕取代”。"""

def is_writable(packet: DecisionPacket) -> bool:
    """GIP v0.2 §1.1 双字段可执行判定（写路径准入）。"""
    # return (
    #     packet.status in {SELF_REVIEWED, EXECUTED}
    #     and packet.review is not None
    #     and packet.review.review_result in {APPROVE, NO_ACTION_APPROVE}
    #     and packet.execution_mode != SHADOW_READ_ONLY
    #     and packet.risk.hard_block == []
    # )
```

**不变式钩子（实现层断言，骨架仅声明）：**

| ID | 断言 |
|---|---|
| DPK-I1 | 非 NO_ACTION 写动作 ⇒ `is_writable` |
| DPK-I2 | NO_ACTION 仍必须成包并过 SRA |
| DPK-I3 | `state_digest` / `forecast_ref` 仅引用 Trusted/Validated |
| DPK-I4 | `proposed_actions` 空数组仅允许 NO_ACTION 整包 |
| DPK-I5 | SHADOW ⇒ Adapter 写硬拒绝 |
| DPK-I6 | 失败包不可物理删除 |
| DPK-I7 | Executed 后核心字段只追加 `corrections[]` |
| DPK-I8 | 最终可追溯 ≥1 条 CausalRecord |

### 4.2 ForecastBundle

```python
# packages/garp_contracts/forecast.py
@dataclass(frozen=True)
class ForecastObject:
    object_id: str              # FC-CURVE-* / FC-ETA-BUDGET / FC-STAB-PLAN / ...
    horizon: str                # "2h" | "to_day_end" | "7d" | ...
    payload: dict               # 对象专属结构（见 FE 接口 §3）
    confidence: float           # [0,1]
    based_on_validated_ids: list[str]

@dataclass(frozen=True)
class ForecastBundle:
    bundle_id: str
    state_id: str
    as_of: datetime
    status: str                 # OK | DEGRADED | BLOCKED
    objects: list[ForecastObject]
    summary: dict               # 含 overall_confidence；对齐 forecast_ref.summary
    overall_confidence: float
    degraded_targets: list[str]
    gap_flags: list[str]
    based_on_validated_ids: list[str]
    envelope: RuntimeEnvelope   # 强制透传

class ForecastEnginePort(Protocol):
    def precheck(self, req: ForecastRequest, state: BusinessState) -> PrecheckResult:
        """READY | DEGRADED | BLOCKED；confidence=LOW 时封顶。"""

    def predict(self, req: ForecastRequest) -> ForecastBundle:
        """前置：precheck != BLOCKED。禁止消费 Raw MetricSnapshot（FE-P2）。"""
```

### 4.3 RiskEval（RiskAssessment 对齐）

```python
# packages/garp_contracts/gate.py
@dataclass(frozen=True)
class RiskConstraints:
    max_bid_delta_pct: float | None
    max_budget_delta_pct: float | None
    max_daily_adjust_count: int | None
    min_response_window_minutes: int | None
    allow_new_plan: bool
    exploration_budget_cap: float | None
    require_higher_trust: int | None
    review_mode: str            # LITE | STANDARD | STRICT | HUMAN

@dataclass(frozen=True)
class RiskEval:
    risk_level: RiskLevel
    hard_block: list[str]       # 非空 ⇒ 禁止 APPROVE
    constraints: RiskConstraints
    reason_codes: list[str]
    baseline_version: str
    dimensions: dict            # price_band / plan_type / lifecycle / inventory / campaign

class RiskEnginePort(Protocol):
    def evaluate(
        self,
        packet_draft: DecisionPacket,
        state: BusinessState,
        context: RiskContext,
    ) -> RiskEval:
        """分档取最高；hard_block 布尔优先于一切放宽。不生成动作。"""
```

### 4.4 TrustEval

```python
@dataclass(frozen=True)
class TrustEval:
    trust_required: int         # 0–5，动作最低档
    trust_actual: int           # 0–5，决策时实际档
    trust_score_snapshot: float | None   # 0–100
    version: str | None

class TrustEnginePort(Protocol):
    def gate_action(self, action_class: str, actual_level: int) -> TrustEval:
        """能力门控；不替代 SRA。"""

    def ingest_signal(self, signal: TrustSignal) -> None:
        """仅 trust_credit_allowed 且 env=LIVE 可计入 live TS（RE-I2 / RA-06）。"""

    def current_level(self, tenant_id: str) -> int: ...
```

### 4.5 SRAReview（Self-review）

```python
@dataclass(frozen=True)
class PredicateResult:
    id: str                     # CHK_MODEL / CHK_RISK / ... / CHK_STAB
    result: str                 # pass | fail | unknown
    detail: str | None

@dataclass(frozen=True)
class SRAReview:
    review_result: ReviewResult
    approved_by: str            # AGENT | HUMAN
    predicate_trace: list[PredicateResult]
    reason_codes: list[str]
    revise_round: int | None
    human_ticket_id: str | None
    review_event_id: str

class SelfReviewPort(Protocol):
    def review(self, packet: DecisionPacket, risk: RiskEval, trust: TrustEval) -> SRAReview:
        """
        唯一写入 review_result 的组件。
        不变式：
          - risk.hard_block 非空 ⇒ 不得 APPROVE
          - NO_ACTION ⇒ NO_ACTION_APPROVE 路径
          - ESCALATE_HUMAN 须 human_ticket_id
          - 全量 predicate_trace 写 Audit/ReviewEvent
        """

    def map_human_decision(self, ticket_id: str, human_result: str) -> SRAReview:
        """HUMAN_* 经 SRA 映射回写；禁止其他组件直写包字段。"""
```

### 4.6 Adapter：RO / RW

```python
# packages/garp_contracts/adapter.py
@dataclass(frozen=True)
class ResourceQuery:
    query_id: str
    resource: str               # CAMPAIGN_LIST | METRIC_SNAPSHOT | INTRADAY_CURVE | ...
    scope: ResourceScope
    fields: list[str] | None
    dry_run: bool               # 只读恒为 True
    envelope: RuntimeEnvelope

@dataclass(frozen=True)
class ReadResult:
    payload_ref: str
    raw: dict                   # PlatformPayload | FixturePayload（不可直信）
    fetched_at: datetime
    validation_state: str       # UNVALIDATED | VALIDATING | VALIDATED | REJECTED
    rate_limit_meta: dict | None
    warnings: list[str]

@dataclass(frozen=True)
class AbstractActionRequest:
    action_id: str
    action_type: str            # WA-BID-01 | ... | WA-CLS-01
    action_class: str
    decision_package_id: str    # G-01 校验
    plan_mode: str
    target: dict
    change: dict | None         # NO_ACTION 省略
    constraints: ActionConstraints   # idempotency_key 必填
    rationale_ref: str
    dry_run: bool               # 非 LIVE 强制 True
    envelope: RuntimeEnvelope

@dataclass(frozen=True)
class ActionReceipt:
    receipt_id: str
    action_id: str
    status: ReceiptStatus
    platform_ack_ref: str | None
    idempotency_key: str
    submitted_at: datetime
    audit: ReceiptAudit         # decision_id / source_env / response_window_due_at

class PlatformAdapterReadPort(Protocol):
    def read(self, query: ResourceQuery) -> ReadResult:
        """只读；不改变平台状态。"""

class PlatformAdapterWritePort(Protocol):
    def write(self, req: AbstractActionRequest) -> ActionReceipt:
        """
        硬闸顺序（不可绕过）：G-01 → G-02 → G-03 → G-04 → G-05 → G-06 → G-07 → G-08 → G-09。
        G-01 双字段 + Shadow 写硬拒绝（SHADOW_WRITE_FORBIDDEN）。
        NO_ACTION：不调平台写；返回 NOT_APPLICABLE_NO_ACTION。
        本轮 LiveTransport 未装配；任何 dry_run=false 请求必须硬失败。
        """

class GateCheckerPort(Protocol):
    """Adapter 内硬闸集合；实现为可组合检查器列表。"""
    def check_g01(self, req: AbstractActionRequest) -> GateResult: ...
    def check_g02(self, req: AbstractActionRequest, trust: TrustEval) -> GateResult: ...
    def check_g03(self, req: AbstractActionRequest, risk: RiskEval) -> GateResult: ...
    # ... G-04 … G-09 同构
```

### 4.7 RuntimeEnvelope 与自检（runtime）

```python
# packages/garp_contracts/envelope.py
@dataclass(frozen=True)
class RuntimeEnvelope:
    env: EnvLabel
    mode: str                   # MODE_READ | MODE_SHADOW_DECIDE | MODE_SHADOW_EXEC_SIM | MODE_LIVE_WRITE
    adapter_runtime: str        # FIXTURE_ONLY | SIMULATION | SANDBOX_LIVE | LIVE
    dry_run: bool
    receipt_source: str
    learning_pool: str          # LIVE_POOL | SHADOW_POOL | DROPPED
    trust_credit_allowed: bool
    execution_mode: ExecutionMode
    packet_kind: PacketKind
    envelope_id: str
    session_id: str
    config_ref: str
    selfcheck_ref: str | None
    captured_at: datetime
    actor: str
    version: str

class BootstrapperPort(Protocol):
    def bootstrap(self, config_path: str) -> RuntimeEnvelope:
        """默认 MODE_SHADOW_DECIDE + FIXTURE_ONLY + SHADOW_READ_ONLY。"""

class SelfcheckPort(Protocol):
    def run_boot_selfcheck(self, envelope: RuntimeEnvelope) -> SelfcheckRecord:
        """SC-A…SC-E；探针仅 Fixture/内存，禁止真实网络。"""

class CircuitBreakerPort(Protocol):
    def assert_and_trip(self, assertion_id: str, ctx: dict) -> CircuitOutcome:
        """RA-01…RA-12；Trip-Reject / Trip-Freeze / Trip-Abort。"""
```

---

## 5. 配置与 RuntimeEnvelope 装配点

### 5.1 装配时序（Boot）

```text
apps/cli|worker
    → garp_runtime.bootstrap.load_config(configs/default.yaml)
    → 覆盖：envs / CLI 仅允许收紧（禁止把非 LIVE 改 LIVE）
    → Bootstrap 构造 RuntimeEnvelope（envelope_id, session_id, config_ref）
    → Selfcheck.run_boot_selfcheck(envelope)
         PASS            → 按 envelope.mode 开放能力面
         PASS_READ_ONLY  → 卸载 Shadow-Decide，仅 MODE_READ
         FAIL / ABORT    → freeze_writes / 进程退出（RE-I12）
    → DI 装配：
         transport = FixtureTransport | SimulationTransport
         LiveTransport = NOT_ASSEMBLED | FailClosedStub
         CredentialProvider = EmptyProvider（get() 拒绝）
    → 将 envelope 注入所有 Port 构造函数（只读字段，禁止中途改写）
    → Session 绑定 envelope（RE-I10：同 session 禁止 env 漂移）
```

### 5.2 配置分层（Proposed）

| 层 | 位置 | 内容 | 谁可读 | 谁可写 |
|---|---|---|---|---|
| L0 契约版本 | `schemas/**` | 字段与枚举 | 全部 | 评审变更 |
| L1 默认运行时 | `configs/default.yaml` | mode/env/adapter_runtime/dry_run | Boot | 负责人（禁止静默 LIVE） |
| L2 阈值与基线 | `configs/risk_baselines/**`, `trust_thresholds/**`, `objective_templates/**` | 全部 Proposed 数值 | RKE/TE/OFG | 仅 GA2-T07 标定流程 / 治理 |
| L3 Fixture | `fixtures/**` | FX-01… | edge/tests | 设计维护 |
| L4 会话覆盖 | 环境变量 / CLI | 仅收紧安全相关 | Boot | 人工 |

### 5.3 装配点清单（代码锚点）

| 装配点 | 模块 | 必须注入 | 断言 |
|---|---|---|---|
| BP-01 Config Loader | runtime | `config_ref` | SC-A6 |
| BP-02 Envelope Factory | runtime | envelope 全字段 | SC-A3/A4 |
| BP-03 Transport DI | edge.adapter | fixture/sim；live=stub | SC-B1/B2；D-07 |
| BP-04 Credential | edge.adapter | EmptyProvider | SC-A5 |
| BP-05 Gate Chain | edge.adapter | G-01…G-09 检查器 | SC-C3 |
| BP-06 SRA Writer Lock | gate.self_review | 唯一 `apply_review` 写权 | GIP C5 |
| BP-07 ME Pool Router | core.memory | learning_pool 由 envelope 推导 | RA-05 |
| BP-08 TE Signal Filter | gate.trust | `trust_credit_allowed` | RA-06 |
| BP-09 KE Promotion Gate | core.knowledge | env≠LIVE 拒自动晋升 | RA-07 |
| BP-10 Egress Guard | runtime/edge | 真实广告域 FAIL-CLOSED | SC-B3；RA-12 |

### 5.4 与 Decision Packet 的衔接

组包时（CBA/RE）必须：

```text
packet.execution_mode = envelope.execution_mode
packet.packet_kind    = envelope.packet_kind
# RE-I8: shadow_decision ⇔ SHADOW_READ_ONLY
```

Adapter `write` 入口再次校验 packet 与 envelope 一致性（RA-02 / RA-10），**不信任**仅内存对象。

---

## 6. 测试分层建议

> 原则：骨架阶段即可建立分层与 CI 门禁；业务算法测试后置。  
> **所有测试零真实网络、零真实凭证**（SC-B3 / D-12）。

| 层 | 目录 | 测什么 | 不测什么 | 建议工具（Proposed） |
|---|---|---|---|---|
| **unit** | `tests/unit/**` | 纯函数：枚举/校验、状态机合法迁移、`is_writable`、门禁谓词、envelope 不变式 | 端到端业务 | pytest；无 I/O |
| **contract** | `tests/contract/**` | JSON Schema 样例序列化；跨包接口字段齐套；双字段语义；依赖方向 lint | 性能 | jsonschema + `tools/lint_deps.py` |
| **fixture** | `tests/fixture/**` | FX-01…FX-10 回放；BDV 规则表；STATE gap_flags；NO_ACTION 合成回执 | 真实平台 | 本地 Fixture 加载器 |
| **shadow-sim** | `tests/shadow_sim/**` | MODE_SHADOW_DECIDE 闭环：STATE→FE→RE→gate→packet→Adapter(硬拒绝/SIMULATED)→Audit；DR-01…DR-12 演练 | 真实反事实成功主张 | 进程内集成；SelfcheckRecord 断言 |

### 6.1 分层出口准则（骨架阶段）

| 层 | 出口准则 |
|---|---|
| unit | 状态机与 DPK-I* 断言全绿；无网络 mock |
| contract | DPK Schema 样例（§8.1/8.2 文档样例）可校验通过；依赖图无 D-01…D-12 违规 |
| fixture | FX-01 产出 shadow packet；FX-02 产出 NO_ACTION_APPROVE 合成回执 |
| shadow-sim | DR-01（LiveTransport 误装配）/ DR-06（Trust 偷计分）/ DR-07（伪 ACCEPTED）为一票否决级：任一失败不得宣称 Shadow 可用 |

### 6.2 CI 建议顺序（Proposed）

```text
lint_deps → unit → contract → fixture → shadow_sim(selfcheck)
```

生产/演练 boot 再跑一遍 SC-B/C/D（RE-Q7）。

---

## 7. 不在本骨架范围

| 项 | 说明 | 归属 |
|---|---|---|
| 预测/推理/Trust/风险**算法实现** | 仅 Port 与对象 | 各引擎详设 + GA2-T07 标定 |
| 真实京东/抖音连接与 SDK | LiveTransport 未装配 | GA2-T25（须单独授权） |
| 凭证、OAuth、签名 | EmptyProvider | 授权后另文 |
| 数据库 / MQ / ORM / Web 框架选型 | 逻辑端口已预留 | 实现评审 |
| 抖音 Domain 详设 | 仅占位包 | GA2-T16 |
| GA-3 验证协议与实验执行 | 预留钩子 | GA2-T29 |
| 论文正文与 GA-1 理论修订 | — | 禁止本任务修改 |
| LIVE 写权限与 Trust 自动升权 | 硬失败 | 新 GA-DEC |
| 性能/容量/SLO 终局 | — | 实现阶段 |

---

## 8. 待决问题

| ID | 问题 | 建议（Draft） | 阻塞实现？ |
|---|---|---|---|
| **SK-Q01** | 权威实现语言/运行时（Python vs 其他）是否在骨架评审时冻结？ | Proposed：Python 作门禁与编排权威；TS 仅可选 UI | 否（可后置，但避免双权威） |
| **SK-Q02** | `DecisionPacketPort` 状态迁移用不可变新实例还是受控 mutator？ | Proposed：不可变 + 事件溯源友好；与 Audit 只追加一致 | 否 |
| **SK-Q03** | contracts 多语言生成（schemas→py/ts）是否纳入骨架工具？ | Proposed：先手工对齐 + contract 测试；codegen 后置 | 否 |
| **SK-Q04** | Asset 存储端口最小能力集（append / version / query）如何与 MKB 对齐？ | 对齐 Memory_Knowledge_Boundary；实现评审确认 | 部分 |
| **SK-Q05** | Orchestrator 物理位置（独立 worker vs ME 旁）？ | 逻辑独立、物理后置（LRR-Q01） | 否 |
| **SK-Q06** | Fixture 格式（JSON / JSONL / 目录 manifest）是否冻结以便 contract 测试？ | Proposed：每 FX 一目录 + manifest.json | 否 |
| **SK-Q07** | 依赖 lint 规则粒度（包级 vs 模块级）？ | 先包级（§3.3 D-01…D-12），模块级后补 | 否 |
| **SK-Q08** | 骨架是否包含 `apps/cli` 的最小 shadow-decide 演练命令？ | 是，便于 shadow-sim 验收；仍无写 | 否 |
| **SK-Q09** | 与 GA2-T27（跨文档接口一致性终审）的先后？ | 建议 T27 先行或并行；骨架冲突以 Architecture v0.2 + DPK + GIP v0.2 + JD v0.2 为准 | 建议 |
| **SK-Q10** | 阈值表热更新是否允许在 session 中途生效？ | Proposed：否；需新 session + 重新 selfcheck（RE-I10 同源） | 否 |

---

## 9. 理论与基线追踪（摘要）

| 骨架章节 | 锚点 |
|---|---|
| §1 逻辑模块 | Architecture v0.2 §3–5；四回路 §4 |
| §3 依赖规则 | JD v0.2 §1.5；GIP B-04/C5；架构 P8 |
| §4 接口 | Decision_Packet_Schema；GIP v0.2 §1.1；JD v0.2 §3–4；FE/RE 接口；RE Selfcheck §1 |
| §5 装配 | Runtime_Envelope_Selfcheck §3–4 |
| §6 测试 | Shadow_Mode_Design §7 演练；RE Selfcheck §7 |

**明确不声称：** 本文不提供真实平台接入；不证明算法有效；所有目录名、工具链与阈值均为 Proposed；不修改 GA-1 / PROJECT_SPEC。

---

## 10. 变更记录

| 日期 | 版本 | 变更 | 依据 |
|---|---|---|---|
| 2026-09-14 | v0.1 | 首次建立模块边界与代码骨架：六层逻辑模块、monorepo 目录、依赖禁止规则、关键接口签名、envelope 装配点、测试分层、范围外与待决 | GA2-T28；Architecture v0.2；GA-DEC-004/005；DPK；GIP v0.2；JD v0.2；RE Selfcheck；LRR Runtime |

---

**Document Status:** Draft  
**Next Stage:** 跨文档一致性（GA2-T27）并行评审 → 负责人确认后可进入实现排期  
**Explicit Non-claim:** 本文仅为骨架与边界设计；不含完整业务实现；不含真实 SDK/凭证/投放脚本；默认参数与工具链一律 Proposed。
