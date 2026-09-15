# GA-2：知识演化回路运行时编排（回路 C）

**文档编号：** GA-2-KERT-001  
**任务编号：** GA2-T37  
**版本：** v0.1  
**状态：** Draft  
**阶段：** GA-2 Engineering Design（下一轮运行时编排）  
**输入基线：** `Research/GA-1/GA-1_Theory_v1.0.md`（GA-1.0 / v1.0，Confirmed）  
**上游架构：** `Architecture_Overview_v0.2.md`（Confirmed，GA-DEC-004）  
**强关联：**  
- `Memory_Knowledge_Boundary_v0.1.md`（KE 治理边界、KnowledgeObject Schema、状态机）  
- `Learning_Reflection_Runtime_v0.1.md`（LE 出口、ExperienceCandidate、IF-LE-01 契约）  
- `Parameter_Genome_Templates_v0.1.md`（Genome 对象模型、状态机、calibration 引用）  
- `Threshold_Calibration_Method_v0.1.md`（calibration_version 约定、阈值 Proposed）  
- `Error_Reason_Code_Catalog_v0.1.md`（LR-*/KE-* 码段）  
- `Shadow_Mode_Design_v0.1.md`（env 标签、隔离池、P-01…P-05 防污染）  
**授权依据：** `GA-DEC-004`（主线冻结 + 下一轮含回路 C 运行时）；GA2-T37；关闭缺口 G-06  
**作者角色：** Research Engineer 子代理（工程派生，不新增理论主张）  
**约束：** 本文为运行时编排契约；**不含真实账户脚本、不可执行投放代码、无凭证**；所有阈值与默认值一律 **Proposed**；`env≠LIVE` 禁止自动晋升规则；与理论冲突时以 GA-1 为准并修订本文。

---

## 0. 安全边界与范围声明（强制阅读）

### 0.1 本轮明确不做

| 项 | 说明 |
|---|---|
| 真实平台写操作 | 不调用任何真实投放/改价/改预算接口；知识晋升不触发平台副作用 |
| 真实账户脚本 / 凭证 | 无可执行投放脚本、无密钥、无 AppKey 示例 |
| 修改 GA-1 / PROJECT_SPEC | 不修改理论基线与项目规格 |
| 阈值确认 | 所有 θ、N、λ、冷却参数均为 **Proposed**，须经 TCAL / PEAL 标定后替换 |
| GA-3 实验执行 | 只预留可观测钩子，不在本阶段做实验结论 |
| 存储选型 | 不绑定关系型/文档/向量库技术栈；逻辑分层先行 |

### 0.2 本轮明确要做

1. 定义 Knowledge Engine（KE）作为回路 C 治理核心的运行时角色、任务类型与状态机。  
2. 定义晋升任务队列（PromoteJob）：promote / observe / discard 三路径的入队、幂等、租约与重试。  
3. 定义知识对象版本治理规则：不可覆盖历史、supersede 语义、lineage 单向可追。  
4. 定义人工门禁点：Rule 及以上层级的默认人工确认流程与角色。  
5. 定义 `env≠LIVE` 禁晋升硬约束（对齐 Shadow P-02 / LR-1003）。  
6. 定义 `calibration_version` 与 Genome / Knowledge / Threshold 的引用绑定。  
7. 定义 KE 侧审计字段与新增错误码（KE-*）。  
8. 定义与 RE / CBA / OFG 的反哺接口（IF-KE-01/02 扩展）。  
9. 给出理论追踪与待决问题清单。

### 0.3 一句话定位

> 知识演化回路运行时是回路 C 的**治理与调度层**：把"何时晋升、谁批准、升到哪层、如何版本化、如何反哺决策"工程化；它不替代 Learning 的蒸馏、不替代 Memory 的事实、不替代 Self-review 的终审。

---

## 1. 回路 C 运行时角色

### 1.1 回路全景

对齐 Architecture v0.2 §4 回路 C：

```text
Experience → Rule → Strategy → Parameter Genome → Capability → 反哺 Reasoning / CBA
```

运行时展开：

```text
[LE 出口]                    [KE 治理]                         [资产层]              [反哺]
ExperienceCandidate  ──IF-LE-01──►  PromotionJob              KnowledgeObject       RE / CBA / OFG
  (proposal+Q+evidence)            (promote/observe/discard)   (Case/Exp/Rule/       (IF-KE-01/02)
  env=envelope                         │                         Strategy/Genome/
                                       │                         Capability)
                                       ▼
                                 State Machine:
                                 queued → running →
                                   ├─auto_gate (Case/Exp)
                                   ├─human_gate (Rule+)
                                   ├─observe_pool
                                   └─discard_audit
```

### 1.2 职责边界（相对上游详设）

对齐 `Memory_Knowledge_Boundary_v0.1.md` §1.2 / §2 与 Architecture §5：

| 引擎 | 主责 | 本文新增（运行时） | 绝不做 |
|---|---|---|---|
| **Knowledge Engine (KE)** | 治理 Case→Experience→Rule→Strategy→Capability 结晶、索引、版本、降权 | 晋升任务队列、门禁调度、版本 supersede、反哺触发 | 改写 Memory 原文；执行平台动作；绕过人工门禁 |
| **Learning Engine (LE)** | 蒸馏 ExperienceCandidate；给出 promote/observe/discard 提案 | （已由 LRR 定义） | 跳过 KE 直接入库 |
| **编排器 Orchestrator（KE 侧）** | 晋升队列、触发源、租约、重试、门禁分流 | 本文主体 | 生成业务结论；改 Trust Score |

**编排器逻辑角色：**  
实现上可位于 KE 旁或独立 worker；本文只要求对外暴露与 Architecture 回路 C 一致的契约，不新增 Confirmed 组件名。

### 1.3 触发源（Trigger Sources）

| 触发器 ID | 名称 | 来源 | 默认优先级 | 说明 |
|---|---|---|---|---|
| TRG-CAND | 候选提交 | IF-LE-01 `submit_experience_candidate` | P1 | LE 出口标准路径 |
| TRG-PROMO | 自动晋升检查 | Q 达标 + evidence 完备 + env=LIVE | P1 | Case/Experience 层 |
| TRG-HUMAN | 人工审批触发 | Rule+ 层候选进入门禁队列 | P0 | 见 §4 |
| TRG-OBSV | 观察池到期 | observing 对象时间衰减或复现计数更新 | P2 | 触发 re-evaluate |
| TRG-DOWN | 降权/归档 | RFE Finding（exp_downweight_suggest）或 FQ 规则命中 | P1 | 走 governance 路径 |
| TRG-EVOL | 运行演化 | Strategy/Genome 运行反馈 + calibration patch | P2 | 生成 Evolved 版本候选 |
| TRG-MAN | 人工直接操作 | 负责人/治理角色 | P0 | 必须记录操作者与原因 |

---

## 2. 晋升任务队列（PromotionJob）

### 2.1 队列模型

```text
                    ┌─────────────────────────────────────────┐
  TRG-* ──────────► │         Knowledge Promotion Queue        │
                    │  priority + lease + idempotency_key      │
                    └──────────────────┬──────────────────────┘
                                       │ claim(worker)
                                       ▼
                              ┌────────────────┐
                              │  KE Job Runner  │
                              │  (promote worker)│
                              └───────┬────────┘
                                      │ emit
              ┌───────────────┬───────┴────────┬────────────────┐
              ▼               ▼                ▼                ▼
        KnowledgeObject   Governance       Audit Events     Re-notify
        (version+1)       (approve/reject  (TRACE)          (RE/CBA/OFG
         or observing)     /discard)                        IF-KE-02)
```

**队列语义（逻辑契约，不绑定 MQ 选型）：**

| 属性 | 约定 |
|---|---|
| 至少一次投递 | 触发与投递采用 at-least-once；**幂等由消费端保证** |
| 租约 lease | worker claim 后持有 `lease_until`；过期可被其他 worker 重取 |
| 优先级 | P0 人工/治理事件 > P1 晋升/降权 > P2 观察池到期/运行演化 |
| 背压 | 同 tenant 同 scope 的 promote job 默认串行（Proposed `max_parallel_per_scope=1`）；跨 scope 可并行 |
| 去重窗口 | 见 §2.2 幂等键 |

### 2.2 幂等（Idempotency）

| 场景 | 幂等键（建议） | 冲突行为 |
|---|---|---|
| 候选提交 | `KE:CAND:{candidate_id}` | 已有对应 knowledge_id → 返回既有对象，不重复创建 |
| 自动晋升 | `KE:AUTO:{candidate_id}:{target_level}` | 已完成 → 返回既有 knowledge_id |
| 人工审批 | `KE:HUMAN:{candidate_id}:{target_level}` | 已有审批记录 → 返回既有 decision |
| 观察池 re-evaluate | `KE:OBSV:{knowledge_id}:{seq}` | 同 seq 已完成 → 跳过 |
| 降权/归档 | `KE:DOWN:{knowledge_id}:{trigger_ref}` | 同 trigger 已处理 → 跳过 |
| supersede | `KE:SUPER:{old_id}:{new_id}` | 已 supersede → 返回既有 lineage |
| calibration 绑定 | `KE:CAL:{knowledge_id}:{calibration_version}` | 已绑定 → 返回既有引用 |

**硬规则：** 任何 completed job 不得静默重写 KnowledgeObject payload；若需修订，创建 `version+1` 并保留 lineage（对齐 MKB I4 / DPK-I7 追加原则）。

### 2.3 PromotionJob 对象（新建逻辑对象）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| job_id | string | Y | 前缀 `KJOB-` |
| job_type | enum | Y | `promote` / `observe` / `discard` / `downweight` / `supersede` / `evolve` |
| trigger_type | enum | Y | §1.3 枚举 |
| trigger_ref | string | Y | candidate_id / knowledge_id / finding_id / calibration_id |
| target_level | enum | N | 晋升目标层：`business_case` / `experience` / `operational_rule` / `strategy` / `capability` |
| source_candidate_id | string | N | 来自 LE 的 ExperienceCandidate |
| priority | int | Y | P0–P2 |
| idempotency_key | string | Y | §2.2 |
| scope | object | Y | tenant/shop/domain/entity |
| envelope | object | Y | RuntimeEnvelope 快照（env/mode/learning_pool） |
| status | enum | Y | §3.1 |
| worker_id / lease_until | string / ts | N | running 时 |
| attempts / max_retry | int | Y | Proposed max_retry=3 |
| error_code | string | N | failed 时（KE-* 码） |
| quarantine_reason | string | N | quarantined 时 |
| gate_path | enum | Y | `auto` / `human` / `blocked_env` |
| human_reviewer_id | string | N | human gate 时 |
| human_decision | enum | N | `approve` / `reject` / `defer` + 理由 |
| calibration_ref | object | N | calibration_version + patch_id |
| created_at / updated_at / finished_at | ts | Y / Y / N | |
| output_refs | object | N | knowledge_id, version, governance_event_id |

---

## 3. 状态机与版本治理

### 3.1 PromotionJob 状态机

| 状态 | 含义 | 进入条件 | 允许写入者 |
|---|---|---|---|
| `queued` | 已入队，未被 worker 认领 | 触发校验通过；幂等键不冲突 | Orchestrator |
| `running` | worker 持有租约执行中 | claim 成功；写 `lease_until`、`worker_id` | Job Runner |
| `awaiting_human` | 等待人工审批（Rule+ 层） | auto 校验通过但需人工门禁 | Job Runner |
| `completed` | 正常完成且产物齐全 | KnowledgeObject 已写入/更新；governance 已记录 | Job Runner |
| `failed` | 执行失败，可重试 | 异常/超时/依赖不可用；记录 `error_code` | Job Runner / Orchestrator |
| `quarantined` | 隔离，禁止进入主知识链 | env 非法、污染检测、硬约束拒绝 | Orchestrator / 污染检测器 |
| `rejected` | 人工或自动拒绝 | human_decision=reject 或 auto 校验失败 | Job Runner / 人工 |

### 3.2 状态迁移图

```text
                 trigger
                    │
                    ▼
               ┌─────────┐
               │ queued  │◄────────────┐
               └────┬────┘             │ retry (attempts < max)
                    │ claim            │
                    ▼                  │
               ┌─────────┐        ┌────┴────┐
               │ running │───────►│ failed  │
               └────┬────┘  error └────┬────┘
        ┌───────────┼───────────┐      │ attempts ≥ max
        │           │           │      ▼
        │           │           │  ┌──────────────┐
        │           │           │  │ quarantined  │◄── 污染/env 非法/越权
        │           │           │  └──────────────┘
        ▼           ▼           ▼
  completed   awaiting_human  rejected
  (auto gate) (Rule+ gate)    (auto fail / human reject)
                  │
                  │ human_decision
                  ▼
            ┌───────────┐
            │ completed │ (approve)
            │ rejected  │ (reject)
            │ queued    │ (defer → 重新入队)
            └───────────┘
```

### 3.3 迁移规则表

| 从 → 到 | 条件 | 审计 |
|---|---|---|
| （无）→ queued | 触发器通过前置校验；幂等插入成功 | trigger_id, idempotency_key |
| queued → running | worker claim；lease 成功 | worker_id, lease_until |
| running → completed | auto gate 通过（Case/Exp 层）；payload 校验通过 | knowledge_id, version |
| running → awaiting_human | target_level ∈ {operational_rule, strategy, capability} 且 auto 校验通过 | gate_path=human |
| awaiting_human → completed | human_decision=approve | human_reviewer_id, decision_at |
| awaiting_human → rejected | human_decision=reject | human_reviewer_id, reject_reason |
| awaiting_human → queued | human_decision=defer | defer_reason, requeue_at |
| running → failed | 可恢复错误（超时、依赖 5xx、锁冲突） | error_code, stack_digest |
| failed → queued | attempts < max_retry 且退避到期 | retry_seq |
| failed → quarantined | attempts ≥ max_retry **或** 不可恢复错误 | quarantine_reason |
| running → quarantined | 污染检测：env 伪造、越权晋升尝试、shadow 证据当 LIVE | policy_id |
| running → rejected | auto 校验失败（Q 不达标、evidence 缺失、FQ 阻断） | reject_reason |
| quarantined → queued | 人工解除隔离（须记录操作者） | operator, unquarantine_ticket |

### 3.4 知识对象版本治理（不可覆盖历史）

#### 3.4.1 版本规则

| 规则 ID | 规则 | 说明 |
|---|---|---|
| KV-01 | **不可覆盖历史** | 任何 payload 变更必须 `version+1`；旧版本只读保留 |
| KV-02 | **lineage 单向可追** | 新版本 lineage.parent 指向旧版本；不可反向 |
| KV-03 | **supersede 语义** | 新版本 active 时，旧版本自动 status=deprecated（非删除） |
| KV-04 | **软删默认** | 删除 = status=archived + governance 记录；物理清理由治理策略单独授权 |
| KV-05 | **enterprise_asset 不可降级** | 一旦 enterprise_asset=true，降级须人工 + 版本评审 |
| KV-06 | **跨层引用锁定** | Strategy 引用 Rule 时锁定 rule_id@version；Rule 升版不影响已锁定 Strategy |

#### 3.4.2 supersede 规则

```text
KnowledgeObject vN (active)
        │
        │  触发：Q 衰减 / 反例命中 / calibration patch / 人工修订 / Evolved
        │
        ▼
PromotionJob (job_type=supersede 或 promote)
        │
        ├─ 生成 vN+1 (draft → active)
        │     lineage: { parent: vN, reason: "..." }
        │
        └─ vN 自动 status=deprecated
              governance: { superseded_by: vN+1, superseded_at, operator }
```

**硬不变式：**

| ID | 不变式 | 依据 |
|---|---|---|
| KERT-I1 | 无 CausalRecord 支撑的 Knowledge 不得 `active` | MKB I1 |
| KERT-I2 | 任何降权/归档/丢弃/修订必须可审计（governance 或 discard_reason） | MKB I4 |
| KERT-I3 | `env≠LIVE` 不得自动晋升任何层级 | Shadow P-02；LR-1003 |
| KERT-I4 | Rule 及以上层级晋升必须经过人工门禁（默认） | MKB-Q01；LRR §5.3 |
| KERT-I5 | supersede 不物理删除旧版本 | KV-01/03/04 |
| KERT-I6 | KE 不执行平台写操作；反哺 RE/CBA 只经 IF-KE-01/02 | 架构 I6 |
| KERT-I7 | 理论指标序关系不可被晋升/演化打乱 | Genome C7；TCAL C7 |
| KERT-I8 | calibration_version 非 APPROVED 的 patch 不得作为 live 约束加载 | TCAL §8.3 |

---

## 4. 人工门禁点（Rule 及以上默认人工）

### 4.1 门禁层级表

| 目标层级 | 自动化程度（Proposed） | 门禁角色 | 审批材料 | 依据 |
|---|---|---|---|---|
| `business_case` | 可自动（LIVE + Q 达标） | KE 校验 | evidence 可打开、无 FQ 阻断 | LRR §5.3 |
| `experience` | 可自动（LIVE + Q 达标） | KE 校验 | 同上 + scope 可机读 | LRR §5.3 |
| `operational_rule` | **默认人工** | 负责人 / Research Architect | 规则测试记录（离线回放）、反例率、guardrail 表达 | MKB-Q01；KERT-I4 |
| `strategy` | **必须人工 + 版本评审** | 负责人 + Research Architect | 多规则组合可行性、目标函数一致性、风险包络 | MKB-Q01 |
| `capability` | **必须人工 + 版本评审 + Trust 门槛确认** | 负责人 + TE 确认 | Trust 门槛可配置、触发条件稳定、评价指标闭环 | MKB-Q01；LRR §5.3 |
| `env≠LIVE` 任意层 | **禁止自动** | — | Shadow §5.4 特批通道（须新 GA-DEC） | Shadow P-02；KERT-I3 |

### 4.2 人工审批流程

```text
PromotionJob (target_level ∈ {Rule, Strategy, Capability})
        │
        │ auto 校验通过（Q、evidence、FQ、env=LIVE）
        ▼
   status = awaiting_human
        │
        │ 通知审批人（角色见 §4.1）
        ▼
   审批人查看材料：
     - evidence_causal_ids 可打开的 CausalRecord 链
     - draft_quality / Q 分维度
     - 反例率（若已有）
     - calibration_ref（若有）
     - scope 适用边界
     - 风险声明
        │
        ├─ approve → status=completed；写 governance
        ├─ reject  → status=rejected；写 reject_reason
        └─ defer   → status=queued；写 defer_reason + requeue_at
```

**审批硬规则：**

1. 审批人不得修改 candidate payload；只能 approve / reject / defer。  
2. 审批事件必须写审计（actor、decision、reason、timestamp）。  
3. 同一 candidate 的 Rule+ 晋升若被 reject，重新提交须补充新 evidence 或新 calibration。  
4. 审批超时（Proposed `T_hold_max=72h`）自动 requeue 至 P0 优先级并通知。

---

## 5. env≠LIVE 禁晋升（对齐 LR-P / ENV）

### 5.1 硬约束

对齐 `Shadow_Mode_Design_v0.1.md` §5 / P-02 与 `Learning_Reflection_Runtime_v0.1.md` LRR-I4：

```text
if promotion_job.envelope.env != LIVE:
    promotion_job.gate_path = blocked_env
    promotion_job.enterprise_rule_eligible = false
    # KE 正式晋升接口硬拒绝
    raise KE-1003 (PROMOTE_BLOCKED_ENV)
```

### 5.2 过滤矩阵

| 产物 / 动作 | env=LIVE | env≠LIVE |
|---|---|---|
| ExperienceCandidate → Case/Exp 晋升 | 可自动（Q 达标） | **禁止** |
| Case/Exp → Rule 晋升 | 人工门禁 | **禁止** |
| Rule → Strategy / Capability | 人工 + 版本评审 | **禁止** |
| Genome 演化（Evolved） | 可（绑定 calibration_version） | **禁止** |
| supersede / 降权 / 归档 | 可（governance 记录） | 可（governance 记录） |
| 观察池 re-evaluate | 可 | 可（但不可晋升） |
| 反哺 RE / CBA（IF-KE-02） | 可 | 不可（shadow-only 产物不进主链） |

### 5.3 防污染检查（继承 Shadow P-01…P-05，KE 侧）

| 检查 | 通过条件 | 错误码 |
|---|---|---|
| KERT-P01 | PromotionJob / KnowledgeObject 均带 envelope | KE-1001 |
| KERT-P02 | KE 晋升接口拒绝 `env≠LIVE` 且无特批单号 | KE-1003 |
| KERT-P03 | 抽样 0 条 live 规则引用 shadow-only 证据 | KE-1004 |
| KERT-P04 | quarantined job 不得静默转入 completed | KE-1005 |
| KERT-P05 | calibration_ref 非 APPROVED 不得作为 live 约束 | KE-1006 |

---

## 6. calibration_version 与 Genome 引用

### 6.1 版本标识约定

对齐 `Threshold_Calibration_Method_v0.1.md` §8.1：

| 字段 | 约定 | 示例（Example-Only） |
|---|---|---|
| `calibration_version` | `CAL-{target_class}-{yyyyMM}[-{seq}]` | `CAL-EXPQ-202609-01` |
| `calibration_status` | `PROPOSED` / `APPROVED` / `ACTIVE` / `SUPERSEDED` / `REJECTED` | 评审前恒 PROPOSED |
| `genome_ref` | 受影响 genome_id + version | `JD-LFM-HARVEST-MATURE@0.1.0` |
| `knowledge_ref` | 相关 KO id/version | `KO-experience-12@v2` |
| `quality_threshold_version` | Q 权重与 θ 版本 | `QT-0.1.0` |

### 6.2 引用绑定矩阵

| 知识对象 | 必须引用 | 可选引用 |
|---|---|---|
| Experience / Case 晋升 | quality_threshold_version | shadow eval_id |
| Rule 晋升 | quality_threshold_version + calibration_ref（若有） | genome_ref |
| Strategy 晋升 | quality_threshold_version + calibration_ref | risk_baseline version |
| Capability 晋升 | quality_threshold_version + trust_config_version | calibration_ref |
| Genome Evolved | calibration_version（最近一次） | lineage.calibration_ref |
| Genome Calibrated | calibration_version + quality_score | 样本摘要 |

### 6.3 与 Genome 状态机对齐

对齐 `Parameter_Genome_Templates_v0.1.md` §3.4：

```text
Genome (Expert_Prior / Proposed)
    │  预标定 + 审核
    ▼
Genome (Calibrated / Active)
    │  运行反馈 + Weekly Reflection + calibration patch
    ▼
Genome (Evolved / Active vN+1)  ← 可并行保留旧版本
    │  质量分过低 / 平台规则变更 / 企业策略变更
    ▼
Genome (Deprecated)
    │  无引用且观察期满
    ▼
Genome (Retired)（保留审计，不物理删除）
```

**Genome 演化运行时规则：**

1. `source=Evolved` 的 Genome 必须指向最近 `calibration_version`（TCAL §8.4）。  
2. Genome 字段变更必须 bump `version` 并写 `lineage.change_log`（Genome §3.5 规则 7）。  
3. calibration patch 的 `status≠ACTIVE` 时，Genome 不得加载该 patch 作为 live 约束（KERT-I8）。  
4. Campaign Overlay 的 calibration_version 独立于常态 patch（TCAL-Q5）。

---

## 7. 审计字段与错误码

### 7.1 审计事件（TRACE）

每次状态迁移与关键动作写审计事件：

| 字段 | 说明 |
|---|---|
| audit_id | 唯一 |
| job_id / knowledge_id / candidate_id | 关联 |
| causal_ids / episode_ids / calibration_ref | 业务锚点 |
| event_type | `enqueue` / `claim` / `heartbeat` / `complete` / `fail` / `quarantine` / `await_human` / `human_approve` / `human_reject` / `human_defer` / `supersede` / `downweight` / `archive` / `evolve` / `re_notify` |
| actor | `orchestrator` / `ke_worker` / `human:{id}` / `system` |
| envelope | env/mode 快照 |
| before_status / after_status | 状态机 |
| before_version / after_version | 版本变更 |
| reason_codes | 可空（KE-* / LR-* 码） |
| payload_digest | 产物哈希，不整对象拷贝 |
| occurred_at | 时间戳 |

**规则：** 审计事件只追加；不得物理删除失败记录（架构 P6 / MKB I4 同源）。

### 7.2 失败与重试策略（Proposed）

| 参数 | 占位 | 说明 |
|---|---|---|
| max_retry | 3 | 含首次共 3 次尝试后 quarantined |
| backoff | 指数：1m, 5m, 30m | 可配置 |
| heartbeat | 60s | running 需续约 lease |
| lease_timeout | 5m | 过期可被重新 claim |
| T_hold_max | 72h | awaiting_human 超时自动 requeue |
| 不可恢复错误 | 直接 quarantined | schema 非法、env 伪造、越权晋升尝试 |
| 部分失败 | degraded completed | 依赖缺失但主结论可出；必须 degraded_flags |

### 7.3 错误码（KE-* 建议新增）

对齐 `Error_Reason_Code_Catalog_v0.1.md` 码段划分，新增 `KE-*` 码段：

| error_code | 类型 | 处置 | 对应 Catalog |
|---|---|---|---|
| KE-1001 | ENVELOPE_MISSING | 重试 1 次后 quarantine | 新增 |
| KE-1002 | CANDIDATE_NOT_FOUND | 拒绝 | 新增 |
| KE-1003 | PROMOTE_BLOCKED_ENV | quarantine + 告警 | 对齐 LR-1003 |
| KE-1004 | SHADOW_EVIDENCE_IN_LIVE | quarantine 该对象 | 新增 |
| KE-1005 | QUARANTINE_BYPASS_ATTEMPT | quarantine + 告警 | 新增 |
| KE-1006 | CALIBRATION_NOT_APPROVED | 拒绝加载 | 新增 |
| KE-1007 | EVIDENCE_CHAIN_BROKEN | 拒绝 | 新增 |
| KE-1008 | QUALITY_BELOW_THRESHOLD | 拒绝（auto gate） | 新增 |
| KE-1009 | FQ_RULE_BLOCKED | 拒绝 + 记 FQ 规则号 | 新增 |
| KE-1010 | HUMAN_GATE_TIMEOUT | requeue + 通知 | 新增 |
| KE-1011 | SUPERSEDE_CONFLICT | 拒绝（版本冲突） | 新增 |
| KE-1012 | SCHEMA_VALIDATION_FAILED | 重试 1 次后 quarantine | 对齐 DP-1001 |
| KE-1013 | DEPENDENCY_UNAVAILABLE | 重试 | 对齐 SYS-1003 |
| KE-1014 | LEASE_LOST | 回 queued | 新增 |
| KE-1015 | THEORETICAL_ORDER_VIOLATION | 拒绝（违反理论序） | 新增 |

**复用现有码：**

| 现有码 | 场景 |
|---|---|
| LR-1001 (NON_LIVE_POOL_ISOLATED) | env≠LIVE 候选进隔离池 |
| LR-1003 (PROMOTE_BLOCKED_ENV) | 与 KE-1003 同义，审计时可并存 |
| SYS-1001 (TIMEOUT) | 通用超时 |
| SYS-1002 (UNKNOWN) | 未知错误 |

---

## 8. 与 RE / CBA / OFG 的反哺接口

### 8.1 接口契约（逻辑 API）

| 接口 ID | 方向 | 语义 | 幂等 / 约束 |
|---|---|---|---|
| IF-KE-01 | RE/CBA/SRA → KE | `retrieve_knowledge(scope, intent, min_level)` | 返回 active 优先；含 effective Q；版本锁定 |
| IF-KE-02 | KE → CBA/OFG | `export_strategy_bundle(strategy_ids)` | 版本锁定；含 genome_ref + calibration_ref |
| IF-KE-04 | KE → RE | `notify_knowledge_update(knowledge_id, version, change_type)` | 变更通知；RE 可选择重新加载 |
| IF-KE-05 | KE → CBA | `notify_capability_change(capability_id, version, trust_required)` | Capability 升降通知 |
| IF-LE-01 | LE → KE | `submit_experience_candidate(candidate)` | candidate_id 去重；必带 proposal + evidence + envelope |
| IF-KE-03 | KE → LE | `resolve_candidate(candidate_id, decision, knowledge_id?)` | decision ∈ accept_promote / accept_observe / reject |

### 8.2 反哺时序

```text
PromotionJob completed (env=LIVE)
    │
    ├─ KnowledgeObject version+1 已写入
    │
    ├─ IF-KE-04: notify_knowledge_update → RE
    │     RE 可选择在下次推理时加载新版本
    │
    ├─ IF-KE-02: export_strategy_bundle → CBA/OFG
    │     若 Strategy/Genome 变更，CBA 可触发 LEARNING_FEEDBACK 重规划
    │
    └─ IF-KE-05: notify_capability_change → CBA
          若 Capability trust_required 变更，CBA 更新权限检查
```

### 8.3 反哺硬约束

1. 反哺通知不直接触发 RE/CBA 的即时动作；由 RE/CBA 在下一次决策周期消费。  
2. 版本锁定：RE/CBA 引用的知识对象必须记录 `knowledge_id@version`。  
3. `env≠LIVE` 的知识对象不进 IF-KE-02/04/05 主链。  
4. calibration_version 非 ACTIVE 的知识对象，反哺时必须标注 `provisional=true`。

---

## 9. 观察池与降权运行时

### 9.1 观察池行为

| 触发 | 动作 | 审计 |
|---|---|---|
| 时间衰减到期（λ·Δt_hit） | re-evaluate Q_effective；若 < θ_forget → 降权建议 | governance |
| 新 evidence 补充 | 同 candidate 追加 evidence；Q 重算 | lineage |
| 反例命中 | FQ-04 触发强制降权 + Reflection Finding | governance + finding_id |
| 复现计数达 N_min | 触发晋升检查（TRG-PROMO） | job_id |

### 9.2 降权 / 归档路径

```text
KnowledgeObject (active)
    │
    │ 触发：FQ-01…07 / RFE Finding / Q 衰减 / 人工
    ▼
PromotionJob (job_type=downweight)
    │
    ├─ status=observing → 可回 active（若复现）
    ├─ status=downweighted → 可回 observing（若新 evidence）
    └─ status=archived → 终态（保留审计）
```

**硬规则：**

1. 降权不物理删除（KERT-I5 / MKB I4）。  
2. RFE 不直接改 status；只产生 Finding → KE 执行（LRR-I1）。  
3. Capability 退役须版本化 + Trust 门槛确认（MKB FQ-06）。

---

## 10. 最小运行时时序（端到端）

```text
[LE 蒸馏完成]
    │ IF-LE-01: submit_experience_candidate
    ▼
PromotionJob queued (KE:CAND:{candidate_id})
    │ claim
    ▼
running: auto 校验
    │
    ├─ env≠LIVE → quarantined (KE-1003)
    ├─ Q < θ_promote 且 Q < θ_observe → rejected (KE-1008)
    ├─ FQ 阻断 → rejected (KE-1009)
    │
    ├─ target_level ∈ {Case, Exp} + Q 达标 + env=LIVE
    │     → completed (auto gate)
    │     → KnowledgeObject version+1
    │     → IF-KE-04: notify RE
    │
    ├─ target_level ∈ {Rule, Strategy, Capability} + auto 校验通过
    │     → awaiting_human
    │     → 人工审批
    │     ├─ approve → completed → IF-KE-02/04/05 反哺
    │     ├─ reject  → rejected
    │     └─ defer   → queued (requeue_at)
    │
    └─ target_level 观察池
          → KnowledgeObject status=observing
          → 等待 TRG-OBSV re-evaluate

[TRG-DOWN: RFE Finding]
    → PromotionJob (downweight)
    → KnowledgeObject status 变更
    → governance 记录

[TRG-EVOL: calibration patch APPROVED]
    → PromotionJob (evolve)
    → Genome version+1 (source=Evolved)
    → lineage.calibration_ref 绑定
    → IF-KE-02: export_strategy_bundle
```

---

## 11. 理论追踪与待决问题

### 11.1 理论 → 工程追踪

| 理论主张 | GA-1 锚点 | 本文落点 | 覆盖 |
|---|---|---|---|
| Knowledge Evolution | §6.5, §10.3；GA-INNOV-005 | §1 全景；§3 状态机；§6 Genome 对齐 | Mapped |
| Knowledge Compounding | §6.6, §10；GA-INNOV-006 | §3.4 版本治理；KV-01…06 | Mapped |
| Experience Distillation | §6.4, §9；GA-INNOV-004 | §1.2 LE 出口；IF-LE-01 | Mapped（依赖 LRR） |
| Cross-plan Learning | §10.1 | §1.3 TRG-CAND 跨计划批处理入口 | Mapped |
| Experience Quality Score | §9.3 | §2.2 幂等；§4.2 审批材料；θ 阈值 | Mapped（阈值 Proposed） |
| Experience Selection / Forgetting | §9.4 | §9 观察池与降权；FQ 规则 | Mapped |
| Promotion Parameter Genome | §10.2；GA-INNOV-009 | §6 Genome 引用与演化 | Mapped |
| Trust-based Autonomous Growth | §11.3；GA-INNOV-007 | §4.1 Capability Trust 门槛 | Partial（本体在 GA2-T05/T38） |
| Causal Memory | §9.2；GA-INNOV-008 | KERT-I1 证据链要求 | Mapped |
| 稳定性优先 / NO_ACTION | §8.5 | §4.2 审批超时 requeue；不自动晋升 | Mapped |
| 失败即学习事件 | §9.4；架构 P6 | §9.2 降权不删除；Failure Pattern 同权 | Mapped |
| 理论指标序不可打乱 | §7.2–7.3；Genome C7 | KERT-I7；KE-1015 | Mapped |

### 11.2 与上游不变式对齐声明

1. 未修改 GA-1 / PROJECT_SPEC。  
2. 与 Memory_Knowledge_Boundary：LE 提案、KE 治理；observing/downweighted/deprecated 路径一致；KERT-I1/I2 = MKB I1/I4。  
3. 与 Learning_Reflection_Runtime：IF-LE-01/IF-KE-03 契约一致；env≠LIVE 禁晋升 = LRR-I4。  
4. 与 Shadow_Mode：env 标签、隔离池、禁自动晋升 = Shadow P-02/P-03。  
5. 与 Threshold_Calibration：calibration_version 约定一致；非 APPROVED 不加载 = KERT-I8。  
6. 与 Parameter_Genome：Genome 状态机对齐；Evolved 指向 calibration_version。  
7. 与 Error_Reason_Code_Catalog：KE-* 码段新增；复用 LR-1001/1003、SYS-1001/1002/1003。  
8. 无真实账户脚本与写路径。

### 11.3 待决问题

| ID | 问题 | 影响 | 建议（Draft） | 归属 |
|---|---|---|---|---|
| KERT-Q01 | Rule+ 人工审批的具体角色与代理机制？ | 治理效率 | 负责人 + Research Architect 双签；代理须记录 | 负责人 |
| KERT-Q02 | awaiting_human 超时（T_hold_max）是否分层级？ | 治理节奏 | Rule 48h / Strategy 72h / Capability 120h（Proposed） | 治理 |
| KERT-Q03 | 观察池 re-evaluate 的频率与批量策略？ | 资源 | 周批（对齐周反思）；事件驱动即时 | 实现 |
| KERT-Q04 | 跨层引用锁定（KV-06）的实现粒度？ | 一致性 | 先整版本锁定；字段级后置 | 实现 |
| KERT-Q05 | KE 编排器是否独立服务还是 KE 旁 worker？ | 实现拓扑 | 逻辑独立、物理后置 | 技术栈后置 |
| KERT-Q06 | capability 晋升是否需要 TE 确认 Trust 门槛？ | 权限耦合 | 是；TE 提供 trust_required_level 校验 | GA2-T05/T38 |
| KERT-Q07 | 多租户知识隔离与共享粒度？ | 知识复利边界 | scope 增加 org_id；共享默认同租户同品类 | 负责人（MKB-Q07 联动） |
| KERT-Q08 | calibration patch 与 KE 阈值配置的加载时序？ | 一致性 | 装载窗口统一；热加载须版本校验 | 实现 |
| KERT-Q09 | 降权传播规则（同一 CausalRecord 被多条 Knowledge 引用）？ | 一致性 | 证据降权联动 effective Q；策略层不自动废弃 | KE 详设（MKB-Q06 联动） |
| KERT-Q10 | 反哺通知的投递语义（至少一次 vs 最多一次）？ | 可靠性 | 至少一次；消费端幂等 | 实现 |

---

## 12. 变更记录

| 日期 | 版本 | 变更 | 依据 |
|---|---|---|---|
| 2026-09-14 | v0.1 | 首次建立回路 C 运行时：角色与触发器、晋升队列幂等租约、状态机与版本治理、人工门禁、env≠LIVE 禁晋升、calibration_version 引用、审计与 KE-* 错误码、反哺接口、理论追踪与待决 | GA2-T37；Architecture v0.2；GA-DEC-004；MKB/LRR/Genome/TCAL/ERR/Shadow v0.1 |

---

**Document Status:** Draft  
**Next Stage:** 架构/负责人评审 → 修订 v0.2；阈值与 Trust 耦合并入 GA2-T05 / GA2-T14 / GA2-T38  
**Owner Review:** 待评审  
**Explicit Non-claim:** 本文不代表已接入真实京东账户；所有阈值、重试与调度参数均为 Proposed；知识演化运行时不得产生真实投放副作用，也不得在非 LIVE 环境自动晋升企业规则或写入 live Trust Score。  
**Closes Gap:** G-06（回路 C 缺 KE 晋升治理运行时）
