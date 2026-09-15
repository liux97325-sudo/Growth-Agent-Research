# GA-2：Learning / Reflection 运行时编排

**文档编号：** GA-2-LRRT-001  
**任务编号：** GA2-T24  
**版本：** v0.1  
**状态：** Draft  
**阶段：** GA-2 Engineering Design（下一轮运行时编排）  
**输入基线：** `Research/GA-1/GA-1_Theory_v1.0.md`（GA-1.0 / v1.0，Confirmed）  
**上游架构：** `Architecture_Overview_v0.2.md`（Confirmed，GA-DEC-004）  
**强关联：**  
- `Memory_Knowledge_Boundary_v0.1.md`（LE/KE/RFE 职责与 Schema）  
- `Decision_Packet_Schema_v0.1.md`（Reflected 回填与 Causal 映射）  
- `Shadow_Mode_Design_v0.1.md`（env 标签、隔离池、Learning 过滤）  
- `Threshold_Calibration_Method_v0.1.md`（阈值一律 Proposed）  
- `Risk_Trust_SelfReview_v0.1.md`（Trust 信号仅建议）  
**授权依据：** `GA-DEC-004`（主线冻结 + 下一轮含 Learning/Reflection 运行时）；GA2-T24  
**作者角色：** Research Engineer 子代理（工程派生，不新增理论主张）  
**约束：** 本文为运行时编排契约；**不含真实账户脚本、不可执行投放代码、无凭证**；所有阈值与默认值一律 **Proposed**；`env≠LIVE` 不得自动晋升规则；与理论冲突时以 GA-1 为准并修订本文。

---

## 0. 安全边界与范围声明（强制阅读）

### 0.1 本轮明确不做

| 项 | 说明 |
|---|---|
| 真实平台写操作 | 不调用任何真实投放/改价/改预算接口；编排不触发平台副作用 |
| 真实账户脚本 / 凭证 | 无可执行投放脚本、无密钥、无 AppKey 示例 |
| 自动晋升企业规则 | `env≠LIVE` 的经验/规则晋升一律禁止自动发生；LIVE 亦须 KE 治理门禁 |
| 直接改生产策略 | RFE/LE 不得直接写 Rule/Strategy/Genome；只产生候选与信号 |
| 修改 GA-1 / PROJECT_SPEC | 不修改理论基线与项目规格 |
| 阈值确认 | 所有 θ、N、λ、重试上限均为 **Proposed**，须经 GA2-T14/T15 标定后替换 |
| GA-3 实验执行 | 只预留可观测钩子，不在本阶段做实验结论 |

### 0.2 本轮明确要做

1. 定义 Reflection Engine（RFE）与 Learning Engine（LE）的运行时角色、触发器、任务队列与幂等键。  
2. 定义四类触发：单包复盘、窗口复盘、周反思、失败计划批处理。  
3. 定义编排状态机 `queued → running → completed / failed / quarantined`。  
4. 定义输入输出对象：`ReflectionJob`、`ReflectionReport`、`ExperienceCandidate`、信号载荷。  
5. 定义与 Knowledge Engine 的升级 / 观察 / 丢弃接口（禁止越权写库）。  
6. 定义 Shadow / 隔离池处理规则与防污染硬约束。  
7. 定义 Trust Score 更新信号衔接（**仅 live**）。  
8. 定义审计字段与失败重试策略。  
9. 给出理论追踪与待决问题清单。

### 0.3 一句话定位

> Learning/Reflection 运行时是回路 B（经验蒸馏）的**调度与状态编排层**：把“何时复盘、谁在跑、跑完去哪”工程化；它不替代 Memory 的事实、不替代 Knowledge 的治理，也不替代 Self-review 的终审。

---

## 1. 运行时角色：Reflection Engine / Learning Engine

### 1.1 职责边界（相对上游详设）

对齐 `Memory_Knowledge_Boundary_v0.1.md` §1.2 / §2 与 Architecture §5：

| 引擎 | 主责 | 本文新增（运行时） | 绝不做 |
|---|---|---|---|
| **Reflection Engine (RFE)** | 触发并组织复盘；校验假设与响应窗口；产出 Finding 与治理信号 | 作业入队、幂等、状态机推进、报告落库 | 直接改 Rule/Strategy；直接改 Trust Score 本体；绕过 KE |
| **Learning Engine (LE)** | 从 Causal/Episode/报告中蒸馏 ExperienceCandidate；给出 promote/observe/discard 提案 | 蒸馏批编排、候选去重、投递 KE 的提交通道 | 跳过质量分入库；删除 Memory；在 env≠LIVE 自动晋升 |
| **编排器 Orchestrator** | 统一队列、触发源、租约、重试、隔离分流 | 本文主体 | 生成业务结论 |

**编排器逻辑角色（非新架构组件）：**  
实现上可位于 ME 旁或独立 worker；本文只要求对外暴露与 Architecture 回路 B 一致的契约，不新增 Confirmed 组件名。

### 1.2 触发器（Trigger Sources）

| 触发器 ID | 名称 | 来源 | 默认优先级 | 说明 |
|---|---|---|---|---|
| TRG-PKT | 单包复盘 | Decision Packet `status→Observed` 且 `outcome_ref` 就绪 | P1（高） | 对应 Reflected 回填；见 DPK §3 |
| TRG-WIN | 窗口复盘 | `expected_response_window` 到期或指标事件提前触发 | P1 | Adjustment Response Window 闭环校验 |
| TRG-WEEK | 周反思 | 日历调度（默认周日 23:00 本地，Proposed） | P2 | 理论 §11.4 十问 |
| TRG-FAIL | 失败计划批处理 | Episode `outcome_label=failure` / REJECT / 连续误差 | P1 | 架构 P6：失败即学习事件 |
| TRG-EVT | 事件驱动复盘 | 连续 N 次预测误差、风险拦截、Trust 升降、BDV FAIL 阻断 | P0–P1 | MKB-Q03 最少清单 |
| TRG-MAN | 人工触发 | 负责人/运营 | P0 | 必须记录操作者与原因 |

### 1.3 任务队列（Queue Model）

```text
                    ┌─────────────────────────────────────┐
  TRG-* ──────────► │         Reflection / Learn Queue     │
                    │  priority + lease + idempotency_key  │
                    └──────────────────┬──────────────────┘
                                       │ claim(worker)
                                       ▼
                              ┌────────────────┐
                              │   Job Runner   │
                              │  RFE / LE worker│
                              └───────┬────────┘
                                      │ emit
              ┌───────────────┬───────┴────────┬────────────────┐
              ▼               ▼                ▼                ▼
        ReflectionReport  ExperienceCandidate  Signals        Audit Events
        (session/findings) (proposal+Q)     (LE/KE/TE/RKE)  (TRACE)
```

**队列语义（逻辑契约，不绑定 MQ 选型）：**

| 属性 | 约定 |
|---|---|
| 至少一次投递 | 触发与投递采用 at-least-once；**幂等由消费端保证** |
| 租约 lease | worker claim 后持有 `lease_until`；过期可被其他 worker 重取 |
| 优先级 | P0 人工/紧急安全事件 > P1 单包/窗口/失败批 > P2 周反思 |
| 背压 | 同租户同 scope 的 RFE job 默认串行（Proposed `max_parallel_per_scope=1`）；跨 scope 可并行 |
| 去重窗口 | 见 §1.4 幂等键 |

### 1.4 幂等（Idempotency）

| 场景 | 幂等键（建议） | 冲突行为 |
|---|---|---|
| 单包复盘 | `RFE:PKT:{decision_id}` | 已有 completed Report → 返回既有 `session_id`，不重复 Findings |
| 窗口复盘 | `RFE:WIN:{decision_id}:{window_seq}` | 同 seq 已完成则跳过；允许补迟到的 `window_seq+1` |
| 周反思 | `RFE:WEEK:{tenant_id}:{iso_week}` | 重复触发合并到同一 Session |
| 失败批 | `RFE:FAIL:{episode_id}:{batch_id}` | `batch_id` 由编排器生成；重试复用 |
| 蒸馏批 | `LE:DISTILL:{batch_scope_hash}` | 已蒸馏 causal_ids 打 `mark_distilled`，禁止二次入批 |
| 经验提交 KE | `EXC:{candidate_id}` | KE 侧按 candidate_id 去重，重复返回既有 knowledge_id |

**硬规则：** 任何 completed job 不得静默重写 Findings；若需修订，创建 `revision+1` 的 Report 并保留 lineage（对齐 DPK-I7 追加原则）。

---

## 2. 触发类型详设

### 2.1 单包复盘（Packet-level Reflection）

**入口条件（全部满足）：**

1. Decision Packet `status ∈ {Observed, Reflected}`（已 Observed 才能完整复盘；Draft/Self-reviewed 仅可做预审分析，不产正式 Report）。  
2. `outcome_ref` 齐全（`observed_at`、`metrics_delta`、`validation_report_ref`）。  
3. ME 已写入对应 CausalRecord 骨架或可写。  
4. `RuntimeEnvelope.env` 已透传（禁止清洗）。

**作业步骤：**

```text
1. 锁定 packet 冻结字段（hypothesis / actions / objective / forecast / risk / trust 快照）
2. 读 outcome_ref + BDV validation → 计算 met_prediction 偏差
3. 校验 expected_response_window vs actual response_time
4. 生成 ReflectionFinding（prediction_error / rule_upgrade_suggest / ...）
5. 回填 packet.reflection_ref {session_id, finding_ids, outcome_label}
6. 触发 LE 蒸馏（TRG-PKT 联动，或标记 ready_for_distill）
```

**输出：** `ReflectionReport`（type=single_packet）+ 最多 1 条主 CausalRecord 的 reflection 段回填。

**对齐：** Decision Packet `Reflected` 状态由本作业（或覆盖本 decision 的窗口/周反思）写入；无 Report 不得标 Reflected。

### 2.2 窗口复盘（Adjustment Response Window）

**理论锚点：** GA-1 §8.6 调整响应窗口；DPK `expected_response_window`。

**入口条件：**

1. `now ≥ executed_at + min_minutes`（观察就绪）或指标事件提前命中。  
2. `now ≥ executed_at + max_minutes` 则强制关闭窗口（超时也算结果）。  
3. 同 `decision_id` 的 `window_seq` 递增；首次为 1。

**判定矩阵（Proposed）：**

| 观测 | 判定 | 后续 |
|---|---|---|
| 实际响应落在 [min,max] 且方向匹配 expected | `window_hit` | 正常 Reflected；成功率样本 |
| 响应过早（< min） | `window_early` | 可能噪声/外部干扰；Finding 降低该次验证权重 |
| 超时（> max）无匹配响应 | `window_miss` | 预测误差样本；评估是否干预无效或假设错误 |
| 方向相反 | `window_contradiction` | 高优先级；强制 LE Failure/Adjustment Pattern 候选 |
| BDV FAIL / 指标不可信 | `window_untrusted` | 不产成功/失败标签；进隔离观察 |

**输出：** 更新 CausalRecord.result；可选二次 Report（type=window）；标记 packet 可 Reflected。

### 2.3 周反思（Weekly Reflection）

**理论锚点：** GA-1 §11.4 十问；MKB ReflectionSession `trigger=weekly`。

**范围：** `tenant_id` + 可选 `shop_id` / domain；窗口 `[week_start, week_end)`。

**十问 → Finding 映射（工程化）：**

| # | 理论问题 | 产出 Finding 类型 | 路由 |
|---|---|---|---|
| 1 | 哪些计划成功？ | plan_decision / success 汇总 | CBA / Report |
| 2 | 哪些计划失败？ | 失败清单 + 强制进 LE 批 | LE |
| 3 | 哪些预测准确？ | prediction_error 校准输入 | FE（信号） |
| 4 | 哪些预测偏差较大？ | prediction_error | FE / RFE |
| 5 | 哪些规则应升级？ | rule_upgrade_suggest | KE 经 LE |
| 6 | 哪些经验应降权？ | exp_downweight_suggest | KE |
| 7 | 哪些风险基线需要更新？ | risk_baseline_update | RKE（建议） |
| 8 | 哪些参数模板需要修正？ | genome_revision | KE/OFG（建议） |
| 9 | 哪些商品适合继续放量？ | plan_decision | CBA |
| 10 | 哪些计划应停止探索？ | plan_decision | CBA |

**输出：** 一个 `ReflectionSession`（trigger=weekly）+ 多 Finding + 周度 `ReflectionReport`；**默认不自动晋升任何 Rule**。

### 2.4 失败计划批处理（Failure Batch）

**入口条件：**

1. Episode `outcome_label=failure`，或 Packet `review_result ∈ {REJECT, ESCALATE→HUMAN_REJECT}`，或窗口连续 `window_miss/window_contradiction ≥ N_fail`（Proposed N_fail=3）。  
2. 架构 P6 / MKB §4.4：失败 Episode **必须**进 LE，不得因结果为负直接 discard。

**批处理策略：**

```text
1. 收集失败 Episode / Packet 集合（同 scope 或同 pattern_type）
2. 强制完整 O-H-A-R-R（缺 result/reflection 记 data_gap，不伪造）
3. LE 蒸馏 Failure Pattern 候选；与成功经验同权进 Q 评分
4. 仅当 Q < θ_observe 且无因果解释时才可 discard（须写 discard_reason）
5. 高价值单次失败 → observing，不得直接 Rule
```

**输出：** 批 `ReflectionReport`（type=failure_batch）+ ExperienceCandidate（pattern_type=Failure）集。

---

## 3. 编排状态机

### 3.1 状态定义

| 状态 | 含义 | 进入条件 | 允许写入者 |
|---|---|---|---|
| `queued` | 已入队，未被 worker 认领 | 触发校验通过；幂等键不冲突 | Orchestrator |
| `running` | worker 持有租约执行中 | claim 成功；写 `lease_until`、`worker_id` | Job Runner |
| `completed` | 正常完成且产物齐全 | Report/Candidate 已落库；信号已投递或显式 deferred | Job Runner |
| `failed` | 执行失败，可重试 | 异常/超时/依赖不可用；记录 `error_code` | Job Runner / Orchestrator |
| `quarantined` | 隔离，禁止进入主学习链 | env 非法、污染检测、硬约束拒绝 | Orchestrator / 污染检测器 |

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
        │           │           │  │ quarantined  │◄── 污染/env 非法/硬失败
        │           │           │  └──────────────┘
        ▼           ▼           ▼
  completed   completed   (partial 产物
  (full)      (partial    标 degraded)
              + degraded)
```

### 3.3 迁移规则表

| 从 → 到 | 条件 | 审计 |
|---|---|---|
| （无）→ queued | 触发器通过前置校验；幂等插入成功 | trigger_id, idempotency_key |
| queued → running | worker claim；lease 成功 | worker_id, lease_until |
| running → completed | 产物 schema 校验通过；BEFORE/AFTER 审计完整 | report_id / candidate_ids |
| running → failed | 可恢复错误（超时、依赖 5xx、锁冲突） | error_code, stack_digest |
| failed → queued | attempts < max_retry 且退避到期 | retry_seq |
| failed → quarantined | attempts ≥ max_retry **或** 不可恢复错误 | quarantine_reason |
| running → quarantined | 污染检测：env 伪造、越权晋升尝试、数据源未校验却当 LIVE | policy_id |
| quarantined → queued | 人工解除隔离（须记录操作者） | operator, unquarantine_ticket |
| running → completed (degraded) | 依赖数据部分缺失但已显式标注 gap | degraded_flags |

### 3.4 完成语义

| 产物 | completed 必须具备 |
|---|---|
| ReflectionReport | session_id、trigger_type、scope、finding_ids（可空数组但须 reason）、closed_at |
| ExperienceCandidate | candidate_id、proposal、evidence_causal_ids、distill_batch_id；discard 必须有 discard_reason |
| Packet 回填 | `reflection_ref` 仅在 covering 本 decision 的 Report completed 后写入 |

**禁止：** `completed` 但未写任何审计事件；`completed` 但尝试写 Rule/Strategy payload。

---

## 4. 输入 / 输出对象

### 4.1 ReflectionJob（编排作业，新建逻辑对象）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| job_id | string | Y | 前缀 `RJOB-` |
| trigger_type | enum | Y | `single_packet` / `response_window` / `weekly` / `failure_batch` / `event` / `manual` |
| trigger_ref | string | Y | decision_id / episode_id / iso_week / event_id |
| priority | int | Y | P0–P2 |
| idempotency_key | string | Y | §1.4 |
| scope | object | Y | tenant/shop/domain/entity |
| input_refs | object | Y | packet_ids, episode_ids, causal_ids, state_ids |
| envelope | object | Y | RuntimeEnvelope 快照（env/mode/learning_pool） |
| status | enum | Y | §3.1 |
| worker_id / lease_until | string / ts | N | running 时 |
| attempts / max_retry | int | Y | Proposed max_retry=3 |
| error_code | string | N | failed 时 |
| quarantine_reason | string | N | quarantined 时 |
| created_at / updated_at / finished_at | ts | Y / Y / N | |
| output_refs | object | N | report_id, candidate_ids, signal_ids |

### 4.2 ReflectionReport（复盘报告）

> 扩展 MKB `ReflectionSession`，作为运行时标准产出。

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| report_id | string | Y | 前缀 `RFR-` |
| session_id | string | Y | 对应 ReflectionSession |
| trigger_type | enum | Y | 同 Job |
| window_start / window_end | ts | Y | 复盘窗口 |
| scope | object | Y | |
| checklist | object | N | 周反思十问完成标记 |
| finding_ids | list | Y | Finding 引用（可空） |
| outcome_label_summary | map | N | success/failure/neutral 计数 |
| packet_coverage | list | Y | 覆盖的 decision_id；含未 Reflected 原因 |
| signal_ids | list | Y | 发往 LE/KE/TE/RKE/CBA 的信号 |
| learning_pool | enum | Y | `LIVE_POOL` / `SHADOW_POOL` |
| degraded_flags | list | N | 数据缺口 |
| created_at / closed_at | ts | Y | |
| revision / superseded_by | int / string | A / N | 修订只追加 |

### 4.3 ExperienceCandidate（对齐 MKB §3.6，运行时约束）

字段沿用 MKB：`candidate_id, title, abstract, pattern_type, scope, statement, evidence_causal_ids, distill_batch_id, draft_quality, proposal, discard_reason, created_at`。

**运行时附加约束：**

| 约束 | 规则 |
|---|---|
| 证据 | `evidence_causal_ids ≥ 1`；跨计划 Rule 级建议 ≥ N_min（Proposed 3） |
| proposal 枚举 | `promote_to_case_or_exp` / `observe` / `discard`（与 MKB 一致） |
| env | `envelope.env != LIVE` ⇒ `enterprise_rule_eligible=false` |
| 去重 | 语义指纹：`hash(pattern_type, statement, scope_key)`；近重复并入已有 candidate 并加 evidence |
| 提交 | 仅经 `IF-LE-01` → KE；LE 不直写 Knowledge Store |

### 4.4 Finding 与信号载荷（摘要）

对齐 MKB `ReflectionFinding`：

| finding_type | 载荷要点 | routed_to | 是否可自动执行 |
|---|---|---|---|
| prediction_error | 预测 vs 实际、horizon | FE | 否（校准建议） |
| rule_upgrade_suggest | target_knowledge_ids、证据、建议幅度 | LE→KE | 否，须 Q+治理 |
| exp_downweight_suggest | 目标经验、反例率、FQ 规则号 | KE | 否，KE 治理确认 |
| risk_baseline_update | 基线版本、偏差分布 | RKE | 否，建议 |
| genome_revision | genome 引用、字段差分 | KE/OFG | 否，建议 |
| plan_decision | 继续放量/停止探索清单 | CBA | 否，进入下一决策 |

**硬不变式：**

| ID | 不变式 | 依据 |
|---|---|---|
| LRR-I1 | RFE 不得直接 `update knowledge.payload` | MKB I3 |
| LRR-I2 | LE 不得跳过 draft_quality / Q 门禁入库 | Architecture §5 LE 边界 |
| LRR-I3 | 任何降权/丢弃必须可审计 | MKB I4 |
| LRR-I4 | `env≠LIVE` 不得写入 live Trust，不得自动晋升 Rule/Strategy/Genome | Shadow §5；GA-DEC-004 |
| LRR-I5 | 编排本身不产生平台写副作用 | 架构 P6 / JD 红线 |
| LRR-I6 | 失败样本必须进入学习链或显式 discard_reason | 架构 P6 |

---

## 5. 与 Knowledge Engine 的升级 / 观察 / 丢弃接口

### 5.1 接口契约（逻辑 API）

| 接口 ID | 方向 | 语义 | 幂等 / 约束 |
|---|---|---|---|
| IF-LE-01 | LE → KE | `submit_experience_candidate(candidate)` | candidate_id 去重；必带 proposal + evidence + envelope |
| IF-RFE-01 | 调度/事件 → RFE | `start_reflection(trigger, scope)` | §1.4 幂等键 |
| IF-RFE-02 | RFE → KE/LE | `emit_finding(finding)` | 须被 accept/reject/defer 闭环 |
| IF-RFE-03 | RFE → TE/RKE | `emit_governance_signal(type, payload)` | 仅建议 |
| IF-KE-03 | KE → LE | `resolve_candidate(candidate_id, decision, knowledge_id?)` | decision ∈ accept_promote / accept_observe / reject |
| IF-LE-02 | LE → ME | `mark_distilled(ids)` | 防重复蒸馏 |

### 5.2 三路径处理（Promote / Observe / Discard）

对齐 MKB §4.2 与知识状态机：

```text
ExperienceCandidate
        │
        ├─ proposal=promote_to_case_or_exp
        │     条件: Q≥θ_promote ∧ n_rep≥N_min ∧ e≥e_min ∧ env=LIVE（或特批）
        │     KE: draft → business_case / experience（version+1）
        │
        ├─ proposal=observe
        │     条件: θ_observe ≤ Q < θ_promote，或单次高价值 n_rep=1
        │     KE: status=observing；可时间衰减
        │
        └─ proposal=discard
              条件: Q<θ_observe 且无高价值意外；或 FQ 阻断且不可修复
              动作: 记 discard_reason；停止晋升；Memory 原文保留
```

**阈值占位（全部 Proposed，须标定）：**  
`θ_promote=0.75`，`θ_observe=0.45`，`N_min=3`，`e_min=0.5`（与 MKB §4.2 一致，不得表述为已验证）。

### 5.3 升级门禁（谁批）

| 目标层级 | 自动化程度（Proposed） | 门禁 |
|---|---|---|
| business_case / experience | 可自动（LIVE + Q 达标） | KE 校验 evidence 可打开、无 FQ |
| operational_rule | 默认人工/SRA 确认 | MKB-Q01：Rule 及以上需门禁 |
| strategy / capability | 必须人工 + 版本评审 | Trust 门槛可配置 |
| env=shadow 任意层 | **禁止自动** | Shadow §5.4 特批通道 |

### 5.4 观察池与降权回调

1. `observing` 对象由 KE 持有；RFE 周反思可发 `exp_downweight_suggest`。  
2. LE 可在后续批次补充 evidence 到同一 candidate（lineage）。  
3. 降权走 KE `governance` 字段；RFE 不直接改 status。  
4. 时间衰减仅对 observing/downweighted，分层 λ 见 MKB §4.3。

---

## 6. Shadow / 隔离池处理规则

### 6.1 标签强制

对齐 Shadow §5.1：`RuntimeEnvelope.env ∈ {LIVE, SHADOW, SIMULATION, FIXTURE}` 全链路透传；RFE/LE **禁止**清洗或改写为 LIVE。

### 6.2 编排层过滤矩阵

| 产物 | env=LIVE | env≠LIVE |
|---|---|---|
| ReflectionReport | 主链；可 Reflected 主 Packet | 可生成；`learning_pool=SHADOW_POOL`；不 Reflected 为 live 成功样本语义时须标注 |
| ExperienceCandidate | 可进主蒸馏 | **默认隔离**；可 shadow-only 蒸馏 |
| Rule/Strategy/Genome 晋升 | 需 KE 治理 | **禁止自动晋升** |
| Trust 信号 | 允许（见 §7） | **禁止写入 live Trust** |
| Failure Pattern | 主链强制 | 影子失败单独标注，不与 live 混计 |
| discard | 须 reason | 同左 |

### 6.3 隔离池行为

```text
on_job_enqueue(job):
  if job.envelope.env != LIVE:
      job.learning_pool = SHADOW_POOL
      job.trust_credit_allowed = false
      job.enterprise_rule_eligible = false

on_candidate_emit(c):
  if c.envelope.env != LIVE:
      c.visibility = shadow_analytic
      # 仅 IF-LE-01 的 shadow 通道；KE 正式晋升接口硬拒绝
```

**防污染检查（继承 Shadow P-01…P-05，编排侧）：**

| 检查 | 通过条件 |
|---|---|
| LR-P01 | Job/Report/Candidate 均带 envelope |
| LR-P02 | KE 晋升接口拒绝 `env≠LIVE` 且无特批单号 |
| LR-P03 | TE 更新接口拒绝 `trust_credit_allowed=false` |
| LR-P04 | 抽样 0 条 live 规则引用 shadow-only 证据 |
| LR-P05 | quarantined job 不得静默转入 completed |

### 6.4 反 Reflected 污染

Shadow Packet 可被 RFE 复盘并写 `reflection_ref`，但：

1. `outcome_label` 不得解释为“平台已验证的成功”。  
2. 不得计入 live Trust T2/T8 样本。  
3. 可作为 GA-3 预留的 shadow-eval 样本（标签保留）。

---

## 7. 与 Trust Score 更新信号的衔接（仅 live）

### 7.1 原则

1. RFE 只产生**建议信号**，不改 Trust Score 本体（MKB §7.1、Risk 文档 RFE 边界）。  
2. Trust Engine（TE）消费信号并决定是否计入维度；权重公式属 GA2-T05。  
3. **`env≠LIVE` ⇒ 信号只进 SHADOW_POOL，不更新 live TS/Level。**

### 7.2 信号类型（映射理论 §11.3 Trust 构成）

| 信号 ID | 对应 Trust 因子 | 来源 | live 可计分 |
|---|---|---|---|
| TR-SIG-PRED | 历史预测准确率 | window_hit / prediction_error | 是 |
| TR-SIG-ACHV | 调整后达成率 | packet outcome vs expected | 是 |
| TR-SIG-RISK | 风险控制能力 | 无硬红线违规、回撤 | 是 |
| TR-SIG-BUD | 预算损失控制 | 预算事件 Finding | 是 |
| TR-SIG-REVIEW | 失败复盘质量 | 完整 Report、无静默丢弃 | 是 |
| TR-SIG-KNOW | 知识更新有效性 | accepted 观察→升级命中 | 是（滞后） |
| TR-SIG-GATE | 自审批准确性 | T8 样本：审批 vs 事后结果 | 是 |
| TR-SIG-SHADOW | 影子代理表现 | shadow eval | **否**（仅 proxy/材料） |

### 7.3 衔接时序

```text
RFE Report completed (env=LIVE)
    → emit_governance_signal(TR-SIG-*, payload)
        → TE.ingest(signal)
            → 若 trust_credit_allowed: 累计入维度候选
            → 下一次 Trust 重算窗口应用（非实时秒级）
            → 仅当 TE 策略确认后影响 Level
```

**硬约束：**

1. 编排器不得在 completed 回调里直接改 Trust Level。  
2. Shadow/proxy 分数与 live 分必须字段隔离（`shadow_trust_proxy` vs `trust_score`）。  
3. 升权评审材料可引用 RFE 报告，但升权事件本身走显式授权（Shadow §7）。

---

## 8. 审计字段与失败重试

### 8.1 审计事件（TRACE）

每次状态迁移与关键动作写审计事件：

| 字段 | 说明 |
|---|---|
| audit_id | 唯一 |
| job_id / report_id / candidate_id | 关联 |
| decision_id / episode_id / causal_ids | 业务锚点 |
| event_type | `enqueue` / `claim` / `heartbeat` / `complete` / `fail` / `quarantine` / `emit_finding` / `submit_candidate` / `trust_signal` |
| actor | `orchestrator` / `rfe_worker` / `le_worker` / `human:{id}` |
| envelope | env/mode 快照 |
| before_status / after_status | 状态机 |
| reason_codes | 可空 |
| payload_digest | 产物哈希，不整对象拷贝 |
| occurred_at | 时间戳 |

**规则：** 审计事件只追加；不得物理删除失败记录（架构 P6 / DPK-I6 同源）。

### 8.2 失败与重试策略（Proposed）

| 参数 | 占位 | 说明 |
|---|---|---|
| max_retry | 3 | 含首次共 3 次尝试后 quarantined |
| backoff | 指数：1m, 5m, 30m | 可配置 |
| heartbeat | 60s | running 需续约 lease |
| lease_timeout | 5m | 过期可被重新 claim |
| 不可恢复错误 | 直接 quarantined | schema 非法、env 伪造、越权晋升尝试 |
| 部分失败 | degraded completed | 依赖缺失但主结论可出；必须 degraded_flags |

### 8.3 错误码（草案）

| error_code | 类型 | 处置 |
|---|---|---|
| E_DEPENDENCY | ME/KE/BDV 不可用 | 重试 |
| E_TIMEOUT | 单步超时 | 重试 |
| E_LEASE_LOST | 租约丢失 | 回 queued |
| E_SCHEMA | 产物校验失败 | 重试 1 次后 quarantine |
| E_ENV_FORGERY | envelope 与证据不符 | 立即 quarantine |
| E_POLICY_ESCALATE | 检测到越权晋升写 | quarantine + 告警 |
| E_DATA_UNTRUSTED | 当 LIVE 用未校验指标 | quarantine 该结论分支 |

---

## 9. 理论追踪与待决问题

### 9.1 理论 → 工程追踪

| 理论主张 | GA-1 锚点 | 本文落点 | 覆盖 |
|---|---|---|---|
| 三阶段推理闭环 | §6.4；OHARR | §2.1 单包复盘；§4 Packet↔Causal 回填 | Mapped |
| Experience Distillation | §6.4, §9；GA-INNOV-004 | §1.1 LE；§2.4；§4.3；§5 | Mapped |
| Adjustment Response Window | §8.6 | §2.2 窗口复盘判定矩阵 | Mapped |
| Weekly Reflection | §11.4 | §2.3 十问映射 | Mapped |
| 失败即学习事件 | §9.4；架构 P6 | §2.4；LRR-I6 | Mapped |
| Knowledge Evolution 不越级 | §6.5, §10；GA-INNOV-005/006 | §5 三路径 + 门禁 | Mapped |
| Trust 权限随表现 | §11.3；GA-INNOV-007 | §7 仅建议信号；shadow 不计 live 分 | Mapped |
| 稳定性 / NO_ACTION | §8.5 | 单包复盘覆盖 NO_ACTION；正确 HOLD 计入稳定性样本 | Mapped |
| Causal Memory | §9.2；GA-INNOV-008 | 输入依赖 CausalRecord；不改写历史 | Mapped |

### 9.2 与上游不变式对齐声明

1. 未修改 GA-1 / PROJECT_SPEC。  
2. 与 Decision Packet：仅在 covering Report 完成后写 `reflection_ref` → `Reflected`。  
3. 与 Causal Memory：只读证据 + 追加 reflection/correction，不覆盖 O-H-A。  
4. 与 Knowledge 状态机：LE 提案、KE 治理；observing/downweighted/deprecated 路径一致。  
5. 与 Shadow：env 标签、隔离池、禁自动晋升、禁 live Trust。  
6. 无真实账户脚本与写路径。

### 9.3 待决问题

| ID | 问题 | 影响 | 建议（Draft） | 归属 |
|---|---|---|---|---|
| LRR-Q01 | 编排器是否独立服务还是 ME 旁 worker？ | 实现拓扑 | 逻辑独立、物理后置 | 技术栈后置 |
| LRR-Q02 | 周反思默认时区与店铺营业日历？ | 窗口边界 | 按 tenant 配置；默认 Asia/Shanghai | 负责人 |
| LRR-Q03 | 事件触发清单与 N_fail / N_pred 何值？ | 过频/过漏 | 先最小集：连续 3 次 window_miss、风险拦截、Trust 升降 | GA2-T14 标定 |
| LRR-Q04 | Report 覆盖多 Packet 时 Reflected 回填事务边界？ | 一致性 | 批回填 + 失败可重入；幂等键含 report_id | 实现评审 |
| LRR-Q05 | 语义去重用规则还是向量近邻？ | 重复经验 | 先规则指纹，向量后置 | LE 详设 |
| LRR-Q06 | degraded completed 是否允许写 Reflected？ | 审计语义 | 允许但 packet.tags 加 `reflected_degraded` | 待确认 |
| LRR-Q07 | shadow-only 蒸馏产物保留多久？ | 存储 | 与 Shadow Pool 生命周期策略对齐 | Shadow/存储 |
| LRR-Q08 | Trust 信号重算窗口（实时/日/周）？ | 自治节奏 | 先日批，周反思汇总 | GA2-T05 |
| LRR-Q09 | 人工解除 quarantined 的审批角色？ | 治理 | 项目负责人；重大须 GA-DEC | 负责人 |
| LRR-Q10 | 多租户队列公平性与饿死？ | SLO | 按 tenant 加权轮询（Proposed） | 实现 |

---

## 10. 最小运行时时序（端到端）

```text
[Decision Packet Observed]
        │ TRG-PKT / TRG-WIN
        ▼
  ReflectionJob queued → running
        │
        ├─ read Packet + outcome_ref + CausalRecord + BDV
        ├─ assess window_hit/miss/...
        ├─ emit Findings
        ├─ ReflectionReport completed
        ├─ packet.reflection_ref ← Report  ⇒ status=Reflected
        │
        ├─ LE distill batch (mark_distilled)
        │       └─ ExperienceCandidate → IF-LE-01 → KE
        │              promote / observe / discard
        │
        └─ if env=LIVE: emit TR-SIG-* → TE
           if env≠LIVE: SHADOW_POOL only

[周日 TRG-WEEK]
  ReflectionSession + 十问 Findings + 周度 Report
  同样走 LE；不自动晋升 Rule
```

---

## 11. 变更记录

| 日期 | 版本 | 变更 | 依据 |
|---|---|---|---|
| 2026-09-14 | v0.1 | 首次建立 Learning/Reflection 运行时编排：角色与触发器、队列幂等、状态机、Report/Candidate、KE 接口、Shadow 隔离、Trust 信号（仅 live）、审计重试、理论追踪与待决 | GA2-T24；Architecture v0.2；GA-DEC-004；MKB/DPK/Shadow/TCAL |

---

**Document Status:** Draft  
**Next Stage:** 架构/负责人评审 → 修订 v0.2；阈值与 Trust 耦合并入 GA2-T05 / GA2-T14  
**Owner Review:** 待评审  
**Explicit Non-claim:** 本文不代表已接入真实京东账户；所有阈值、重试与调度参数均为 Proposed；编排运行时不得产生真实投放副作用，也不得在非 LIVE 环境自动晋升企业规则或写入 live Trust Score。
