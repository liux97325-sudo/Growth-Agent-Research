# GA-2：Memory / Knowledge / Experience / Reflection 数据边界详设

**文档编号：** GA-2-MKB-001  
**版本：** v0.1  
**状态：** Draft  
**阶段：** GA-2 Engineering Design（组件详设 / GA2-T04）  
**输入基线：** `Research/GA-1/GA-1_Theory_v1.0.md`（GA-1.0 / v1.0，Confirmed）  
**上游架构：** `Research/GA-2/Architecture_Overview_v0.2.md`（Confirmed，GA-DEC-004）  
**追踪矩阵：** `Research/GA-2/Theory_Engineering_Trace.md`（Draft）  
**授权依据：** `GA-DEC-003`（Accepted，2026-09-11）  
**作者角色：** Research Engineer（按理论基线做工程派生整理）  
**约束：** 本文档为工程草案，不是新理论；与理论冲突时以理论基线为准并修订本文。本文档不含真实广告 API 调用代码。

---

## 1. 文档目的与范围

### 1.1 目的

在 Architecture Overview 已划定的 L2 引擎层与 L5 数据底座基础上，给出 **Memory / Learning（Experience 提炼过程）/ Knowledge / Reflection** 四层的：

1. 职责边界（谁存什么、谁提炼什么、谁治理什么、谁触发复盘）；
2. 字段级实体与对象模型（Schema 草案）；
3. 知识演化状态机与迁移条件；
4. 经验质量评分与遗忘规则的工程化表达；
5. Causal Memory 样例（O-H-A-R-R）到字段的映射；
6. 组件间读写权限与接口契约；
7. 对 GA-RQ / GA-INNOV 的追踪；
8. 待决问题清单。

### 1.2 严格区分原则（与理论对齐）

本设计将 GA-1 §12 中的“Memory / Knowledge / Experience / Reflection”底座，工程化为 **四层职责**，并把 **Experience** 理解为“经 Learning Engine 提炼后的中间产物 + Knowledge 底座中处于 Experience 层的知识对象”，避免“经验”一词在两处漂移：

| 概念 | 工程层 | 理论锚点 | 一句话边界 |
|---|---|---|---|
| Memory | Memory Engine + L5 Memory Store | §9.2 Causal Memory；GA-INNOV-008 | 只记录“发生过什么、为何判断、动作与结果、反思原文”；**不直接晋升为企业规则** |
| Learning（Experience 提炼） | Learning Engine | §6.4 Experience Distillation；GA-INNOV-004 | 从 Memory / 执行日志中蒸馏 **Experience Candidate**，并做升级/观察/丢弃判断 |
| Knowledge | Knowledge Engine + L5 Knowledge Store | §6.5 / §9.1 / §10 / §10.3；GA-INNOV-005/006/009 | 治理 Case→Experience→Rule→Strategy→Capability 的结晶、索引、复用、降权与版本 |
| Reflection | Reflection Engine | §11.4 Weekly Reflection；三阶段复盘 | 触发并组织复盘，校验假设与响应窗口，产出升级/降权信号；**不直接写规则，只发信号给 Learning/Knowledge** |

### 1.3 本轮不做

- 真实平台 API 调用、真实账户写操作；
- 数据库/向量库/消息队列技术栈终局选型；
- GA-3 实验设计；
- Trust / Risk 审批闭环详设（归 GA2-T05）；
- 参数基因目录与默认模板详设（归 GA2-T07）。

---

## 2. 四层职责边界表

### 2.1 核心职责矩阵

| 维度 | Memory | Learning（Experience 提炼） | Knowledge | Reflection |
|---|---|---|---|---|
| **主责** | 事实与因果留存 | 从事实提炼可复用经验候选 | 结晶后的规则/策略/能力治理 | 复盘触发与闭环校验 |
| **写入对象** | Episode、CausalRecord、WorkingContext、指标快照 | ExperienceCandidate、蒸馏批作业 | BusinessCase、Experience、OperationalRule、Strategy、Capability、ParameterGenome | ReflectionSession、ReflectionFinding、Trust/Risk 修正建议 |
| **不做什么** | 不直接改策略；不做跨计划归纳；不打企业标准标签 | 不直接改线上策略；不替代 Knowledge 审批；不删 Memory | 不篡改 Memory 原文；不执行平台动作 | 不直接写 Rule/Strategy；不绕过 Knowledge 治理 |
| **时间尺度** | 事件级 / 日内 / 计划周期 | 计划结束、事件窗口结束后；跨计划批处理 | 版本级；长周期资产 | 周期（默认周更）+ 事件驱动双通道（Draft） |
| **理论锚点** | §9.2；GA-INNOV-008 | §6.4；§9.3–9.4；GA-INNOV-004 | §6.5；§9.1；§10.1–10.4；GA-INNOV-005/006/009 | §6.4 反思步骤；§8.6；§11.4 |
| **架构组件** | Memory Engine（ME） | Learning Engine（LE） | Knowledge Engine（KE） | Reflection Engine（RFE） |
| **输入主源** | TRACE / Decision Log、STATE 快照、执行回执 | ME 产出、CBA 动作包、平台回执、RFE Finding | LE 升级候选、RFE 降权信号、人工/企业标准导入 | ME CausalRecord、KE 版本与命中日志、Trust/Risk 事件 |
| **输出主消费** | RE / FE 上下文、LE 蒸馏、RFE 复盘 | KE 晋升候选、RFE 反思材料 | RE / CBA / SRA / OFG 决策输入 | LE 知识更新任务、TE/RKE 信号、KE 降权任务 |
| **可删除性** | 原则上不可无记录删除；可归档与降权 | 候选可丢弃（须记丢弃原因） | 可降权/观察/归档；Capability 退役须版本化 | Session 完整保留审计；Finding 关联知识对象 |

### 2.2 “Experience” 的双重归属说明（Draft）

理论 §12 将 Memory / Knowledge / Experience / Reflection 并列为底座。本工程草案为避免职责重叠，作如下拆分（**工程派生，非新理论**）：

1. **Experience 作为过程**：由 Learning Engine 负责“日志→经验”的蒸馏与筛选（§6.4）。  
2. **Experience 作为状态**：作为 Knowledge 演化链上的中间态对象（§6.5 中的 Experience 阶段），由 Knowledge Engine 持有版本、索引与降权。  
3. Memory 中的 O-H-A-R-R 是 **证据与叙事**，不是 Experience 本身；Learning 产出的 ExperienceCandidate 指向若干 CausalRecord 作为证据链。

该拆分满足 Architecture Overview §6：`Memory 能否直接改策略？否；必须经 Learning + Knowledge 治理`。

---

## 3. 实体 / 对象模型（字段级 Schema 草案）

> 下列表为 **Draft Schema**，字段类型为逻辑类型；不绑定具体存储引擎。ID 规则建议统一使用前缀 + 单调/UUID 混合，详见 §3.9。

### 3.1 RawMetricSnapshot（原始指标快照，Raw Data 层）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| snapshot_id | string | Y | 唯一 ID |
| source_system | enum | Y | `platform_ad` / `platform_ecom` / `erp` / `wms` / `crm` / `manual` |
| entity_type | enum | Y | `campaign` / `adgroup` / `keyword` / `audience` / `sku` / `shop` |
| entity_id | string | Y | 平台侧或内部业务 ID |
| metric_time | timestamp | Y | 指标时间窗起点 |
| window_size | string | Y | 如 `15m` / `1h` / `1d` |
| metrics | map&lt;string,number&gt; | Y | CTR/CPC/CVR/ROI/GMV/花费/展现/点击/加购等 |
| attribution_flags | map&lt;string,bool&gt; | N | 是否含待付款/退款/跨计划/重复归因等标记 |
| ingest_time | timestamp | Y | 入库时间 |
| trust_state | enum | Y | `raw` / `validated` / `quarantined` |

**边界：** 仅 BDV/STATE 读写；**不得**被 RE 直接当作优化目标。

### 3.2 TrustedBusinessState（校验后经营状态）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| state_id | string | Y | 唯一 ID |
| as_of | timestamp | Y | 状态生效时间 |
| shop_id / sku_id / campaign_ids | string / list | Y | 作用域 |
| inventory | object | N | 可售、在途、仓内、安全库存 |
| budget | object | Y | 日预算、已花、剩余、推广余额 |
| lifecycle_phase | enum | Y | `explore` / `growth` / `mature` / `burst` / `decline` |
| plan_mode | enum | Y | `seeding` / `harvest` / `mixed` |
| activity_events | list&lt;ActivityEvent&gt; | N | 活动窗口 |
| compliance_state | enum | Y | `ok` / `review` / `restricted` |
| source_snapshots | list&lt;snapshot_id&gt; | Y | 证据链 |
| validation_report | object | Y | 偏差比、剔除项、置信度 |

### 3.3 Episode（单次计划/调整周期事实包）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| episode_id | string | Y | 唯一 ID |
| episode_type | enum | Y | `plan_lifecycle` / `intraday_intervention` / `weekly_cycle` |
| parent_episode_id | string | N | 嵌套（计划周期内含多次日内干预） |
| entity_scope | object | Y | 商品/计划/关键词等 |
| started_at / ended_at | timestamp | Y / N | 结束时间可空（进行中） |
| goal_ref | string | Y | 关联当期经营目标与动态目标权重版本 |
| pre_state_id | string | Y | 调整前 TrustedBusinessState |
| post_state_id | string | N | 周期结束状态 |
| causal_record_ids | list&lt;string&gt; | Y | 关联因果记忆 |
| outcome_summary | object | N | 结束后汇总：成功/失败/中性、核心指标对比 |
| outcome_label | enum | N | `success` / `failure` / `neutral` / `pending` |

### 3.4 CausalRecord（因果记忆，O-H-A-R-R 见 §5）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| causal_id | string | Y | 唯一 ID |
| episode_id | string | Y | 所属 Episode |
| seq | int | Y | 因果链内序号 |
| observation | object | Y | 观察：现象、指标、时间窗、对比基线 |
| hypothesis | object | Y | 假设：原因判断、置信度、依据引用 |
| action | object | N | 动作：类型、参数前后值、幅度、执行者（Agent/人） |
| expected_effect | object | N | 预期效果与 Adjustment Response Window |
| result | object | N | 结果：指标变化、是否符合预判、实际响应时间 |
| reflection | object | N | 反思：为何成功/失败、适用边界初判 |
| knowledge_note | object | N | 是否值得进入知识库的初判（**非正式晋升**） |
| evidence_refs | list&lt;string&gt; | Y | snapshot/state/action_receipt 引用 |
| created_at / updated_at | timestamp | Y | 时间戳 |
| visibility | enum | Y | `internal` / `enterprise_asset`（后者仅当晋升后） |

### 3.5 WorkingContext（当前经营窗口上下文）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| context_id | string | Y | 唯一 ID |
| session_key | string | Y | 经营窗口键（shop+date+campaign 组） |
| active_state_id | string | Y | 当前状态 |
| active_episode_ids | list | Y | 进行中 Episode |
| open_hypotheses | list&lt;causal_id&gt; | Y | 未闭环假设 |
| pending_response_windows | list&lt;object&gt; | Y | 等待观察的响应窗口 |
| ttl | duration | Y | 上下文保留时长（日内/跨日策略另定） |

### 3.6 ExperienceCandidate（Learning 产出，未入 Knowledge）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| candidate_id | string | Y | 唯一 ID |
| title / abstract | string | Y | 经验摘要 |
| pattern_type | enum | Y | §9.1：Performance / Attribution / Exposure / Budget / Conversion / Adjustment / Failure / Lifecycle |
| scope | object | Y | 适用商品类型、计划类型、生命周期、平台 |
| statement | text | Y | “若…则…因为…”形式的可复用表述 |
| evidence_causal_ids | list | Y | 证据链（≥1；跨计划建议≥N，N 待标定） |
| distill_batch_id | string | Y | 蒸馏批次 |
| draft_quality | object | Y | 初评分（见 §4） |
| proposal | enum | Y | `promote_to_case_or_exp` / `observe` / `discard` |
| discard_reason | string | N | 丢弃时必填 |
| created_at | timestamp | Y | 时间戳 |

### 3.7 KnowledgeObject（Knowledge 底座统一壳）

> 所有演化层共用元数据壳 + 按 `knowledge_level` 扩展 payload。

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| knowledge_id | string | Y | 唯一 ID |
| knowledge_level | enum | Y | `business_case` / `experience` / `operational_rule` / `strategy` / `capability` |
| status | enum | Y | `draft` / `active` / `observing` / `downweighted` / `deprecated` / `archived` |
| title | string | Y | 名称 |
| payload | object | Y | 按层级不同（见 3.8） |
| scope | object | Y | 适用边界 |
| quality_score | object | Y | 当前综合质量分（见 §4） |
| version | int | Y | 单调版本 |
| lineage | object | Y | 上游 candidate/parent_knowledge_id；下游派生 |
| evidence_refs | list | Y | Causal/Episode/跨计划摘要 |
| governance | object | Y | 晋升/降权操作审计：操作者、原因、时间、决策 ID |
| enterprise_asset | bool | Y | 是否计入企业知识资产（§6.6） |
| created_at / updated_at | timestamp | Y | 时间戳 |

### 3.8 各演化层 payload 差异（Draft）

| knowledge_level | payload 关键字段 | 说明 |
|---|---|---|
| business_case | 场景叙述、指标时间线、决策点、结果 | 具体经营案例（§6.5） |
| experience | statement、适用条件、反例、置信度 | 可复用经验 |
| operational_rule | condition、action_template、guardrail、priority | 经过验证的规则 |
| strategy | intent、组合规则集、目标函数权重、风险包络 | 可迁移策略 |
| capability | capability_name、触发条件、策略引用集、Trust 门槛、评价指标 | 稳定经营能力；对接权限与自动化 |

**ParameterGenome** 与 **EnterpriseStandard** 作为 Knowledge 的扩展对象类型（Draft）：

| 对象 | 关键字段 | 理论锚点 |
|---|---|---|
| ParameterGenome | 商品类型、生命周期、初始预算、ROI 目标、出价/溢价基线、种草收割比、预期指标、风险基线、调整频率 | §10.2；GA-INNOV-009 |
| EnterpriseStandard | 标准类型（新建/高客单调整/放量/稳定性/预警/回收）、阈值、适用组织单元、版本 | §10.4 |

### 3.9 ID 与引用约定（Draft）

| 规则 | 约定 |
|---|---|
| 前缀 | `SNAP-` `STATE-` `EP-` `CR-` `CTX-` `EXC-` `KO-` `RFS-` `RFI-` `TRB-` |
| 版本对象 | `KO-{level}-{seq}@v{n}` |
| 删除策略 | 默认软删 + 审计；物理清理由治理策略单独授权 |
| 跨库引用 | 一律使用稳定 ID 列表，不嵌套整对象拷贝 |

### 3.10 Reflection 对象（见职责表，字段摘要）

**ReflectionSession**

| 字段 | 类型 | 说明 |
|---|---|---|
| session_id | string | 唯一 ID |
| trigger | enum | `weekly` / `event_driven` / `manual` |
| window_start / window_end | timestamp | 复盘窗口 |
| scope | object | 店铺/计划/商品范围 |
| checklist | object | 对应 §11.4 十问的完成标记 |
| finding_ids | list | Finding 引用 |
| signal_ids | list | 发往 LE/KE/TE/RKE 的信号引用 |
| closed_at | timestamp | 关闭时间 |

**ReflectionFinding**

| 字段 | 类型 | 说明 |
|---|---|---|
| finding_id | string | 唯一 ID |
| session_id | string | 所属 Session |
| finding_type | enum | `prediction_error` / `rule_upgrade_suggest` / `exp_downweight_suggest` / `risk_baseline_update` / `genome_revision` / `plan_decision` |
| content | object | 证据、对比、建议幅度 |
| target_knowledge_ids | list | 指向 Knowledge 对象（若适用） |
| routed_to | enum | `LE` / `KE` / `TE` / `RKE` / `CBA` |
| resolution | enum | `accepted` / `rejected` / `deferred` + 理由 |

---

## 4. 经验质量评分与遗忘规则（工程化表达）

> 理论依据：§9.3 Experience Quality Score；§9.4 Experience Selection 与 Forgetting。  
> 本节为 **工程派生的可计算草案**，权重与阈值须在 GA-2 参数预标定（GA2-T07 / 后续标定任务）中落地，**不得表述为已验证结论**。

### 4.1 质量分维度（Draft）

综合分记为 \(Q \in [0,1]\)，建议加权几何/线性混合，首轮先用加权平均便于审计：

| 维度 ID | 名称 | 符号 | 取值 | 数据来源 | 理论依据 |
|---|---|---|---|---|---|
| D1 | 重复验证次数 | \(n_{rep}\) | 归一化到 [0,1] | 独立 Episode 中再次成立次数 | §9.3 |
| D2 | 稳定性 | \(s\) | 方向一致率 | 多次结果方向/幅度稳定度 | §9.3 |
| D3 | 可迁移性 | \(t\) | 跨商品/计划类型覆盖度 | scope 命中与外推成功 | §9.3；§10.1 |
| D4 | 预测准确率 | \(a\) | 假设 vs 结果吻合度 | expected_effect vs result | §9.3；§8.4 |
| D5 | 经营收益 | \(g\) | 归一化收益/成本比 | 结果指标 vs 基线 | §9.3 |
| D6 | 风险程度（负向） | \(r\) | 风险暴露 | RKE 风险事件、回撤 | §9.3；§11.1 |
| D7 | 适用场景清晰度 | \(c\) | scope 可判定性 | 条件是否可机读判定 | §9.3 |
| D8 | 因果解释完整度 | \(e\) | O-H-A-R-R 完备率 | CausalRecord 字段完备 | §9.3；§9.2 |

建议公式（Draft）：

```text
Q = w1·n_rep + w2·s + w3·t + w4·a + w5·g + w6·(1-r) + w7·c + w8·e
约束: Σwi = 1, wi ≥ 0
默认起始权重（待标定，非最优）: 
  w4=a 相关 0.15, w5=g 0.15, w1 0.10, w2 0.15, w3 0.10, 
  w6 0.15, w7 0.10, w8 0.10
```

### 4.2 晋升与观察阈值（Draft）

| 条件（同时满足） | 动作 |
|---|---|
| \(Q \ge \theta_{promote}\) 且 \(n_{rep} \ge N_{min}\) 且 \(e \ge e_{min}\) | LE 提交晋升候选 → KE 校验后 Case/Experience |
| \(\theta_{observe} \le Q < \theta_{promote}\) | 进入观察池 `status=observing` |
| \(Q < \theta_{observe}\) 且无高价值单次意外 | `proposal=discard`，记录 discard_reason |
| 单次高价值但 \(n_{rep}=1\) | 不晋升；进入 Failure/Success Pattern 观察（§9.1） |

建议初始值（**必须标定后替换**）：\(\theta_{promote}=0.75\)，\(\theta_{observe}=0.45\)，\(N_{min}=3\)，\(e_{min}=0.5\)。

### 4.3 遗忘 / 降权规则（非删除）

理论：§9.4 “遗忘不是删除一切，而是降低其对未来决策的影响权重”；架构：失败计划可降权不可无记录丢弃。

| 规则 ID | 触发条件 | 处置 | 是否物理删除 |
|---|---|---|---|
| FQ-01 | 偶然大额订单/异常订单被 BDV 标记 | 相关 Causal/Episode 证据降权；禁止单独支撑规则 | 否 |
| FQ-02 | 平台异常窗口数据 | 打 `platform_anomaly` 标签；默认不参与蒸馏 | 否 |
| FQ-03 | 长期无复现且 \(Q\) 衰减至 \(\theta_{forget}\) 以下 | Knowledge `status=downweighted` → 可 `archived` | 否（归档） |
| FQ-04 | 反例命中率超过阈值 | 强制降权 + 触发 Reflection Finding | 否 |
| FQ-05 | 企业标记“不重要个性化数据源” | 该 source 的新数据不入蒸馏；存量降权 | 否 |
| FQ-06 | Capability 对应 Trust/权限已退役 | `status=deprecated`，保留审计 | 否 |
| FQ-07 | 版本被新策略替代 | 旧版本 `deprecated`，lineage 指向新版本 | 否 |

**时间衰减（Draft）：**  
对 `observing` / `downweighted` 对象，按最后命中时间做衰减：

```text
Q_effective(t) = Q · exp(-λ · Δt_hit)
λ 分层：observe 层 > experience 层 > rule 层 > strategy/capability 层
（strategy/capability 主要靠反例与版本替代，而非时间衰减）
```

### 4.4 Failure Pattern 特殊策略

- 失败 Episode **必须**生成 CausalRecord 并进入 Learning；  
- 高质量 Failure Pattern 与成功经验同权进入 Knowledge（§9.1 Failure Pattern）；  
- 不得因“结果为负”直接 discard；仅当无因果解释且 \(Q\) 过低才可丢弃并记原因。

---

## 5. Causal Memory 样例结构（O-H-A-R-R）字段映射

理论 §9.2 样例（高客单种草计划 CTR 下降）映射到 `CausalRecord` 字段：

| O-H-A-R-R 段 | 理论样例文本（摘要） | Schema 字段 | 建议子结构（Draft） |
|---|---|---|---|
| Observation | 上午 CTR 显著下降 | `observation` | `{window, metric:"CTR", delta, baseline, peer_comparison, state_id}` |
| Hypothesis | 关键词竞争增强，导致展现能力下降 | `hypothesis` | `{cause_claim, confidence, supporting_signals:[...], rival_hypotheses:[...]}` |
| Action | 核心关键词出价上调 15% | `action` | `{action_type:"keyword_bid_up", target, before, after, delta_ratio:0.15, actor, receipt_id}` |
| Expected（工程扩展） | 预期展现恢复、CTR 回升；响应窗口 | `expected_effect` | `{predicted_metrics, response_window, horizon}` |
| Result | 两小时后展现恢复，点击率小幅回升 | `result` | `{actual_metrics, met_prediction:partially, response_time, side_effects}` |
| Reflection | 种草阶段 CTR 下降时优先提高关键词竞争力，而非降低 ROI | `reflection` | `{why_success_or_fail, boundary_conditions, next_time_note}` |
| Knowledge（初判） | 高客单种草计划中，若展现与点击同步下降，应优先检查关键词出价与人群溢价 | `knowledge_note` | `{worth_distill:true, pattern_type:"adjustment", draft_statement}` |

**链式关系（Draft）：**

```text
Episode(plan_lifecycle)
  └─ CausalRecord(seq=1) Observation→Hypothesis→Action→Result→Reflection
  └─ CausalRecord(seq=2) …
  └─ outcome_summary
        │
        ▼
Learning: ExperienceCandidate（聚合多条 CR + 可选跨 Episode）
        │
        ▼
Knowledge: Experience / Rule（携带 lineage → causal_ids）
```

**硬规则：**

1. 任一 Knowledge 对象 `active` 后，必须能追溯到 ≥1 条 CausalRecord；跨计划规则建议 ≥3 条独立 Episode。  
2. Memory 中 `knowledge_note` **不是**正式晋升；晋升唯一入口是 LE 提案 + KE 治理。  
3. Reflection 可引用 CausalRecord 做复盘，但不得改写已写入的 observation/action/result 历史字段（可追加 correction 子记录，Draft）。

---

## 6. 知识演化状态机与迁移条件

### 6.1 状态机（对应 §6.5 / §10.3）

```text
                    ┌─────────────────────────────────────────┐
                    │              Knowledge Engine             │
Raw Data            │  business_case → experience →            │
  │ BDV/STATE       │  operational_rule → strategy → capability│
  ▼                 └─────────────────────────────────────────┘
Trusted State / Episode
  │ Memory 写入 Causal / Episode
  ▼
Causal Memory Store
  │ Learning 蒸馏
  ▼
Experience Candidate ──discard──▶（记 discard_reason，停止）
  │ promote
  ▼
business_case ──抽象+Q达标──▶ experience
  │                              │
  │                              ├─observing / downweighted（可回 experience 或 archive）
  ▼                              ▼
operational_rule ──组合+可迁移──▶ strategy
  │                              │
  └────────────► capability ◀───┘
                   │
                   ├─deprecated（Trust/场景失效）
                   └─archived
```

### 6.2 迁移条件表（Draft）

| 迁移 | 发起方 | 必要条件 | 审计要求 |
|---|---|---|---|
| Raw → Trusted State/Episode | BDV / STATE | 通过真实性校验；标记异常项 | validation_report |
| Episode → Causal 完备 | ME / CBA | O-H-A-R-R 关键字段齐；result 到期可补 | causal_id 链 |
| Causal → ExperienceCandidate | LE | 窗口结束或计划周期结束；或 Reflection Finding 触发 | distill_batch_id |
| Candidate → business_case | KE | proposal=promote；证据可打开；无 FQ 阻断 | lineage |
| business_case → experience | KE | \(Q\ge\theta_{promote}\) 或跨案例归纳完成；scope 可机读 | version+1 |
| experience → operational_rule | KE + RFE 建议 | \(n_{rep}\ge N_{rule}\)；反例率低于阈值；guardrail 可表达 | 规则测试记录（离线回放，非 GA-3） |
| operational_rule → strategy | KE + CBA/OFG 协同 | 多规则可组合；与动态目标函数一致；风险包络明确 | strategy 版本 |
| strategy/rule → capability | KE + TE | Trust 门槛可配置；触发条件稳定；评价指标闭环 | capability 注册表 |
| 任意层降权/归档 | RFE 信号或 KE 治理 | FQ-01…07 或反例 | governance 字段 |

### 6.3 与组件控制流的衔接

对齐 Architecture §5 时序：`执行回执 → ME 写因果记忆 → LE 触发学习 → KE 经验升级候选 → KE 返回规则/策略/基因给 CBA`。  
Reflection 挂在两处：周期任务读 ME/KE；事件任务（预测严重偏差、连续失败、风险触发）即时开会。

---

## 7. 读写权限与组件间接口（谁写谁读）

### 7.1 读写矩阵（R=读，W=写，RW=读写，—=无）

| 数据对象 | ME | LE | KE | RFE | RE | FE | CBA | SRA | RKE | TE | 场景 Agent | BDV/STATE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RawMetricSnapshot | R | R | — | R | — | R | — | — | R | — | R | **W** |
| TrustedBusinessState | R | R | R | R | R | R | R | R | R | — | R | **W** |
| Episode | **RW** | R | R | R | R | R | W(开闭) | R | R | — | R | — |
| CausalRecord | **RW** | R | R | R | R | R | W(发起) | R | R | — | R | — |
| WorkingContext | **RW** | R | — | R | R | R | R | R | — | — | R | — |
| ExperienceCandidate | R | **RW** | R | R | — | — | — | — | — | — | — | — |
| KnowledgeObject | R | R(提案) | **RW** | R | R | R | R | R | R | R | R | — |
| ParameterGenome / Standard | R | R | **RW** | R | R | R | R | R | R | — | R | — |
| ReflectionSession / Finding | R | R(任务) | R(任务) | **RW** | R | R | R | R | R | R | — | — |
| Trust / Risk 信号 | R | R | R | W(建议) | R | — | R | R | RW* | RW* | R | — |

\* Trust Score 本体与 Risk Baseline 本体归 TE/RKE 详设（GA2-T05）；RFE 只写**建议信号**。

### 7.2 接口契约（逻辑 API，非真实广告 API）

| 接口 ID | 方向 | 语义 | 幂等/约束 |
|---|---|---|---|
| IF-ME-01 | CBA/场景 Agent → ME | `append_causal(O-H-A-R-R)` | 按 episode_id+seq 幂等 |
| IF-ME-02 | ME → LE | `on_episode_closed(episode_id)` | 至少一次投递 |
| IF-ME-03 | RE/FE → ME | `query_recent_context(scope, window)` | 只读；不返回未校验 Raw 作为决策依据 |
| IF-LE-01 | LE → KE | `submit_experience_candidate(candidate)` | 带 proposal 与 evidence |
| IF-LE-02 | LE → ME | `mark_distilled(episode/causal ids)` | 防重复蒸馏 |
| IF-KE-01 | RE/CBA/SRA → KE | `retrieve_knowledge(scope, intent, min_level)` | 返回 active 优先；含 effective Q |
| IF-KE-02 | KE → CBA/OFG | `export_strategy_bundle(strategy_ids)` | 版本锁定 |
| IF-RFE-01 | 调度/事件 → RFE | `start_reflection(trigger, scope)` | 周期 + 事件 |
| IF-RFE-02 | RFE → KE/LE | `emit_finding(finding)` | 须被接受/拒绝闭环 |
| IF-RFE-03 | RFE → TE/RKE | `emit_governance_signal(type, payload)` | 仅建议，不直接改权限 |

### 7.3 不变式（Invariants）

1. **I1** 无 CausalRecord 支撑的 Knowledge 不得 `active`。  
2. **I2** Memory 不得被 RE 用于“优化目标计算”，只可作为上下文与证据。  
3. **I3** Reflection 不得直接 `update knowledge.payload`；只能产生 Finding → LE/KE 执行。  
4. **I4** 任何降权/归档/丢弃必须可审计（governance 或 discard_reason）。  
5. **I5** 平台原始指标进入 Episode 前必须过 BDV（对齐 §8.1 / 架构 P3）。  
6. **I6** 学习与知识变更不得触发真实广告写操作；执行只经 Self-review 门禁后的场景 Agent（对齐 §11.2，细节 GA2-T05）。

---

## 8. 与 GA-RQ / GA-INNOV 的追踪

### 8.1 GA-INNOV 追踪

| 创新点 | 本设计覆盖 | 覆盖内容 | 状态 |
|---|---|---|---|
| GA-INNOV-004 Experience Distillation | §2 LE 职责；§3.6；§6 | 日志→候选经验 | Mapped |
| GA-INNOV-005 Knowledge Evolution | §3.7–3.8；§6 状态机 | Case→Capability + 迁移条件 | Mapped |
| GA-INNOV-006 Enterprise Knowledge Compounding | §3.7 enterprise_asset；§4 遗忘非删除 | 资产化与版本治理 | Mapped |
| GA-INNOV-008 Causal Memory | §3.4；§5 O-H-A-R-R 映射 | 因果记忆字段级 | Mapped |
| GA-INNOV-009 Promotion Parameter Genome | §3.8 扩展对象 | 仅 Schema 占位；目录详设 GA2-T07 | Partial |
| GA-INNOV-003 Business State Awareness | §3.1–3.2；I5 | Raw 不可直用 | Mapped |
| GA-INNOV-001/007 | §7 权限接口边界 | Memory/知识不直接改权限 | Partial（本体在 GA2-T05） |

### 8.2 GA-RQ 追踪

| GA-RQ | 本设计贡献 | 状态 |
|---|---|---|
| GA-RQ-001 如何从真实环境获得经验 | ADAPT→BDV→ME→LE 链路与 IF 接口 | Partial（接入层 GA2-T06） |
| GA-RQ-002 如何区分有效/噪声/干扰 | trust_state、attribution_flags、Q 维度、FQ 规则 | Mapped（权重待标定） |
| GA-RQ-003 一次投放→可复用经验 | Episode/Causal→Candidate→Knowledge | Mapped |
| GA-RQ-004 多计划→企业级规律 | LE 跨计划 + KE 状态机；D3 可迁移性 | Mapped |
| GA-RQ-009 不可流失知识资产 | enterprise_asset、版本与 lineage、归档非删除 | Mapped |
| GA-RQ-015 反思持续改进 | ReflectionSession/Finding 双通道 | Mapped（频率待确认） |
| GA-RQ-016 可复用经营知识 | 状态机 + 不变式 I1 | Mapped |
| GA-RQ-002/003/004/016 的 GA-3 验证 | 依赖本 Schema 可观测字段 | 后续 GA-3 |

### 8.3 理论章节索引

§6.4、§6.5、§9.1–9.4、§10.1–10.4、§11.4、§12、§15.5–7 / §15.15。

---

## 9. 待决问题

| ID | 问题 | 影响 | 建议（Draft） | 归属 |
|---|---|---|---|---|
| MKB-Q01 | ExperienceCandidate 晋升是否需要人工确认，尤其升到 Rule/Strategy？ | Trust 与企业治理 | Rule 及以上默认需 SRA/人工门禁；Case/Experience 可自动 | GA2-T05 / 负责人 |
| MKB-Q02 | Q 权重 \(w_i\) 与阈值如何标定？ | 晋升噪声、知识污染 | 用历史人工运营案例离线回放标定；先保守高阈值 | GA2-T07 / 后续标定 |
| MKB-Q03 | Reflection 事件驱动触发器清单？ | 过频/过漏 | 最少：连续 N 次预测误差、计划失败、风险拦截、Trust 升降 | 架构 Q2 联动 |
| MKB-Q04 | WorkingContext TTL 与跨日种草窗口如何定义？ | 日内决策一致性 | 按计划类型配置；收割更长 | FE/RE 详设 |
| MKB-Q05 | 存储选型（关系型 + 文档/向量检索）是否分库？ | 实现 | 逻辑分层先行，物理分库后置 | 技术栈后置 |
| MKB-Q06 | 同一 CausalRecord 被多条 Knowledge 引用时的降权传播规则？ | 一致性 | 证据降权联动 effective Q；策略层不自动废弃 | KE 详设 |
| MKB-Q07 | 企业多组织/多店铺知识隔离与共享粒度？ | 知识复利边界 | scope 增加 org_id；共享默认同租户同品类 | 负责人 |
| MKB-Q08 | Correction 记录是否允许“修正”历史 Observation？ | 可审计性 | 只追加 correction，不覆盖原文 | 待确认 |
| MKB-Q09 | ParameterGenome 与 Strategy 边界（基因是参数模板还是策略）？ | 对象模型 | 暂作 Knowledge 扩展类型，GA2-T07 再裁决 | GA2-T07 |
| MKB-Q10 | Reflection Finding 与 Trust Score 的正式耦合公式？ | 自治成长 | 本设计只留信号接口 | GA2-T05 |

---

## 10. 与上游文档的一致性声明

1. 未修改 `GA-1_Theory_v1.0.md` 与 `PROJECT_SPEC.md`。  
2. 未新增与 GA-1 冲突的理论主张；阈值、公式、状态机细节均为 **工程 Draft**。  
3. 未包含真实京东/抖音/ERP 等 API 调用代码或账户操作脚本。  
4. 与 `Architecture_Overview_v0.1.md`（历史，已被 v0.2 承接）§6 边界第一轮约定一致：Memory 不直接改策略；失败计划不无记录删除；平台数据先校验；权限分级不由本设计授予。

---

## 11. 变更记录

| 日期 | 版本 | 变更 | 依据 |
|---|---|---|---|
| 2026-09-11 | v0.1 | 首次建立：四层边界、Schema 草案、状态机、质量分与遗忘、O-H-A-R-R 映射、读写接口、RQ/INNOV 追踪、待决问题 | GA-DEC-003；GA-1 Theory v1.0；Architecture_Overview_v0.1；GA2-T04 |

---

**Document Status:** Draft  
**Next Stage:** 架构/负责人评审 → 修订 v0.2；阈值与权限耦合并入 GA2-T05 / GA2-T07  
**Owner Review:** 待评审
