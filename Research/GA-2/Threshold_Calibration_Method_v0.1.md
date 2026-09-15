# GA-2：知识 / 信任 / 风险阈值回填与预标定方法论

**文档编号：** GA-2-TCAL-001  
**版本：** v0.1  
**状态：** Draft  
**阶段：** GA-2 Engineering Design（参数治理 / GA2-T14）  
**输入基线：** `Research/GA-1/GA-1_Theory_v1.0.md`（GA-1.0 / v1.0，Confirmed）  
**上游架构：** `Research/GA-2/Architecture_Overview_v0.2.md`（Confirmed，GA-DEC-004）  
**强关联：** `Memory_Knowledge_Boundary_v0.1.md`（GA2-T04）、`Risk_Trust_SelfReview_v0.1.md`（GA2-T05）、`Parameter_Genome_Templates_v0.1.md`（GA2-T07）、`Shadow_Mode_Design_v0.1.md`（GA2-T11）  
**授权依据：** `GA-DEC-003`（Accepted）+ `GA-DEC-004`（Accepted；**参数默认值一律 Proposed，待历史预标定**）  
**作者角色：** Research Engineer 子代理（工程派生，不新增理论主张）  
**约束：** 本文为**标定方法论**，不含真实账户脚本、不含真实历史标定结果、不修改 GA-1 / PROJECT_SPEC；一切数值示例均标注 **Proposed / Example-Only**；与理论冲突时以 GA-1 为准并修订本文。

---

## 0. 安全边界与范围声明（强制阅读）

### 0.1 本轮明确不做

| 项 | 说明 |
|---|---|
| 真实标定结果 | 不写入任何企业历史数据标定后的“终值”；本文只给流程与占位 |
| 真实账户写操作 / 投放脚本 | 不包含任何可对广告账户产生副作用的代码或命令 |
| 凭证与密钥 | 不创建、不示例、不落盘任何 AppKey / Token / Secret |
| 反向修改理论 / 项目规格 | 不修改 `GA-1_Theory_v1.0.md`、`PROJECT_SPEC.md`、GA-1 问题清单 |
| GA-3 实验结论 | 不在本文执行或声称 GA-3 验证结果 |
| 自动升格 Proposed → Confirmed | 标定输出默认仍为 **Proposed**；升格需人工评审 + 版本化决策 |

### 0.2 本轮明确要做

1. 枚举三类阈值清单（Experience Quality Score / Risk Baseline / Trust Score）。  
2. 定义标定所需历史字段（来自 Memory / JD 只读对象，只读消费）。  
3. 定义端到端标定流程：清洗 → BDV → 分层 → 分位/分箱 → 稳健估计 → 回写 Proposed → 人工评审 → 版本化。  
4. 定义防过拟合与防噪声策略（失败样本、活动期、异常订单、理论遗忘/降权呼应）。  
5. 定义冷启动路径：理论优先级先验 + 小预算影子验证。  
6. 定义 `calibration_version` 与 Genome / Knowledge 引用约定。  
7. 定义与 Shadow Mode 指标 `SM-M01…M10` 的衔接。  
8. 列出待决问题。

### 0.3 一句话定位

> **标定不是“算出最优参数”，而是把历史经营证据整理成可审计的 Proposed 修正包，并用版本与门禁保证不会把噪声写成企业规则。**

---

## 1. 目标与原则

### 1.1 目标

| 目标 ID | 目标 | 非目标 |
|---|---|---|
| TC-G1 | 为三类阈值提供**可重复、可审计**的历史回填方法 | 不声称全局最优 |
| TC-G2 | 在数据不足时仍能安全冷启动（保守先验） | 不用少量样本假装“已验证” |
| TC-G3 | 将标定产物接入 KE / RKE / TE 的版本与治理链 | 不绕过人工评审与 Risk 硬红线 |
| TC-G4 | 与 Shadow Mode / GA-3 验证钩子对齐 | 不在影子结果上直接升 live Trust |

### 1.2 标定原则（自理论与 GA-DEC-004 派生）

| ID | 原则 | 锚点 | 工程含义 |
|---|---|---|---|
| C1 | 默认值是先验，不是结论 | GA-DEC-004；理论边界 §14 | 所有回填结果 status=Proposed，直至负责人确认 |
| C2 | 先保守后放宽 | §11.1 最低成效比；稳定性优先 §8.5 | 无历史/低样本时用高阈值、窄幅度、低频率 |
| C3 | 遗忘是降权不是删除 | §9.4；MKB FQ-01…07 | 失败与异常样本进入证据链，但降权/隔离，不静默丢弃 |
| C4 | 分层优先于全局拟合 | §7.2–7.4 价格带/目的/生命周期；§11.1 分档 | 先槽位内估计，再跨槽位继承，禁止全局单阈值覆盖所有场景 |
| C5 | 影子不写 live 分 | Shadow §5 / §7.3 | SM 指标可作标定反馈，不得直接提高 Trust Level |
| C6 | 版本可回滚 | 架构 KE 版本治理 | 每次标定输出绑定 `calibration_version` + lineage |
| C7 | 理论序关系不可被标定打乱 | Genome §5.2；GA-1 §7.2–7.3 | 标定可调**数值与权重强度**，不得改写理论指标优先级序 |

---

## 2. 三类阈值清单

> 下列符号与字段与 MKB / Risk / Genome 文档一致。**所有“建议初始值”均为 Proposed / Example-Only，必须标定后替换。**

### 2.1 Experience Quality Score（Q）阈值族

来源：`Memory_Knowledge_Boundary_v0.1.md` §4。

| 阈值 ID | 符号 | 语义 | 当前占位（Proposed / Example-Only） | 标定目标数据 |
|---|---|---|---|---|
| TC-Q01 | \(w_1…w_8\) | Q 八维权重（D1–D8） | 线性加权和 =1；示例见 MKB §4.1 | 历史晋升/丢弃/降权案例 + 后续验证正确性 |
| TC-Q02 | \(\theta_{promote}\) | 晋升 Case/Experience 门槛 | 0.75 | 已晋升对象的事后稳定率 vs 晋升时 Q |
| TC-Q03 | \(\theta_{observe}\) | 进入观察池下限 | 0.45 | 观察池对象的后续复现率 |
| TC-Q04 | \(N_{min}\) | 晋升所需最小独立重复次数 | 3 | 跨 Episode 复现成功 vs 失败的样本量分布 |
| TC-Q05 | \(e_{min}\) | 因果解释完备度下限 | 0.5 | O-H-A-R-R 完备率与事后可解释性 |
| TC-Q06 | \(\theta_{forget}\) | 降权/归档触发 Q 下限 | Pending（建议取 observe 以下分位） | 长期无命中对象的有效 Q 分布 |
| TC-Q07 | \(\lambda_{level}\) | 时间衰减系数（observe > experience > rule…） | Pending；分层设置 | 各层最后命中时间 vs 仍有效比例 |
| TC-Q08 | \(N_{rule}\) | experience→rule 最小复现 | ≥ \(N_{min}\)，建议更高 | 规则升级后的反例率 |
| TC-Q09 | 反例率阈值 | FQ-04 强制降权 | Pending | 反例/总命中 vs 知识层 |

**回填产出对象：** KnowledgeObject 的 `quality_score`、晋升/观察/遗忘判定参数包（写入 KE 配置，不直接改 payload）。

### 2.2 Risk Baseline 参数族

来源：`Risk_Trust_SelfReview_v0.1.md` §3 / §7；`Parameter_Genome_Templates_v0.1.md` §6。

| 阈值 ID | 参数 | 语义 | 当前占位（Proposed / Example-Only） | 标定目标数据 |
|---|---|---|---|---|
| TC-R01 | `max_bid_delta_pct`（按 R 档） | 出价单次相对幅度上限 | R0–R1≈10–20%；R2≈5–10%；R3≈0–5%；R4=0 | 历史有效调整幅度 vs 事后响应/风险事件 |
| TC-R02 | `max_budget_delta_pct` | 预算单次相对幅度上限 | 通常严于出价 | 同上 + 预算超损事件 |
| TC-R03 | `max_daily_adjust_count` | 日内同类调整次数 | Pending；分 plan_mode | 高频调整 vs 稳定性/噪声 |
| TC-R04 | `min_response_window` | 同对象再调整最小间隔 | 对齐 §8.6 与 Genome §6.4 先验窗 | 调整后指标拐点分布 |
| TC-R05 | `exploration_budget_cap` | 周期探索/新建花费上限 | Pending；企业配置 | 探索花费 vs 成功率/最低成效比 |
| TC-R06 | `N_new_max` / `max_concurrent_new_plans` | 新建数量/并发上限 | Explore 1–3 等 Proposed | 新建计划存活与达标率 |
| TC-R07 | `E_min`（`min_effectiveness_ratio`） | 最低成效比底线 | Mature 0.80–0.95 等 Proposed 区间 | 成效比分布与计划存活 |
| TC-R08 | `max_daily_loss_ratio` | 相对日预算损失上限 | 分生命周期区间 Proposed | 超损事件率与幅度 |
| TC-R09 | `risk_scale(R)` | 风险补偿系数 | R0/R1→1.0，R2→0.6，R3→0.3，R4→0.0 | 不同 R 档下“放宽后”的风险后验 |
| TC-R10 | 活动窗 ROI 放宽幅度 | Campaign Overlay | +0.05–0.15 等 Proposed | 活动窗内 ROI 短暂下修 vs 事后 GMV |

**回填产出对象：** `RiskAssessment.constraints` 各分段 baseline 的 **PROPOSED patch**（对齐 Risk §8.4 `risk_baseline_patch`），经确认后形成下一周期 `baseline_version`。

### 2.3 Trust Score 权重与升降条件

来源：`Risk_Trust_SelfReview_v0.1.md` §4。

| 阈值 ID | 参数 | 语义 | 当前占位（Proposed / Example-Only） | 标定目标数据 |
|---|---|---|---|---|
| TC-T01 | \(w_{T1}…w_{T8}\) | 八维权重 | 0.15/0.15/0.12/0.12/0.10/0.10/0.08/0.18 | 各维与“事后正确决策/风险结果”的相关性 |
| TC-T02 | 滚动窗口 \(W\) | 维度统计窗 | 28 天 | 指标自相关与稳定性 |
| TC-T03 | \(n_{min}\) | 最小可判定事件数 | 30 | 稀疏维是否应标 sparse |
| TC-T04 | 平滑 \(\alpha\) | 指数平滑 | 0.3 | 抗单日噪声 vs 响应速度 |
| TC-T05 | Level 分带 | 0–5 分数带 | L1:40–55 … L5≥90 | TS 与权限误放行/误杀的代价曲线 |
| TC-T06 | 升级附加条件阈值 | 如 `T2≥60`、`T8≥65` | Risk §4.3 表 | 升级后实际成功率 |
| TC-T07 | 迟滞 \(k\) | 升/降级连续次数 | 升 k=2，降 k=1 | 分带边界抖动率 |
| TC-T08 | \(P_{hard},P_{repeat},P_{human}\) | 乘性惩罚上界 | 0.5 / 0.3 / 0.4 | 硬红线与人类否决后恢复曲线 |
| TC-T09 | sparse 先验中心 | 样本不足时回退分 | 50 或父级继承 | 冷启动误升降幅度 |

**回填产出对象：** TE 配置表的 Proposed 权重包 + Level 映射表；**不**直接改 live Trust 历史分值（只改规则，不改既有分轨迹）。

### 2.4 清单交叉依赖（标定顺序建议）

```text
BDV/清洗规则稳定
    → 先标 TC-R04 / TC-R03（动作与窗口，决定样本切分）
    → 再标 TC-Q*（知识晋升噪声控制）
    → 并行标 TC-R01/02/05/07/08（幅度与预算约束）
    → 最后标 TC-T*（Trust 在较稳的数据与门禁语义上更新）
原因：Trust 与 Q 依赖“什么算一次有效调整 / 什么算异常订单”，
若先拟合 Trust，会把清洗口径噪声固化进权重。
```

---

## 3. 数据需求（历史字段清单，只读）

### 3.1 数据来源与权限

| 来源 | 对象（对齐 MKB / JD / Shadow） | 权限 | 标定用途 |
|---|---|---|---|
| Memory Store | Episode、CausalRecord、WorkingContext | **只读** | O-H-A-R-R 完备率、响应窗口、成败标签 |
| Knowledge Store | KnowledgeObject、ParameterGenome、governance | **只读**（标定包回写除外） | 现行阈值、晋升/降权历史、lineage |
| TRACE | ReviewEvent、Decision/Shadow Packet、ActionReceipt | **只读** | 门禁结果、幅度、频率、Trust/Risk 版本 |
| JD Adapter RO | RO-MET-*、RO-BUD-*、订单/退款/归因类只读 | **只读**（dry_run 恒 true） | 指标真值、BDV 输入 |
| BDV / STATE | RawMetricSnapshot、TrustedBusinessState、validation_report | **只读** | 清洗后样本、gap_flags、lifecycle/plan_mode |
| Reflection | ReflectionSession / Finding | **只读** | 阈值表现 FP/FN、RiskBaselinePatch 建议 |
| Shadow Pool | ShadowPacket、SimulatedActionReceipt、SM 评估产物 | **只读**；隔离池 | 冷启动与影子反馈；**不进 live Trust** |

**硬约束：** 标定管道**不得**调用任何平台 write；不得写穿 Memory 原文；不得把 `env≠LIVE` 样本并入 live 统计（对齐 Shadow §5）。

### 3.2 最小字段字典（标定视图，逻辑字段）

> 下列为**标定所需最小集合**，类型为逻辑类型；以 GA2-T04 Schema 为权威，冲突时以 T04 为准。

#### 3.2.1 会话 / 计划上下文

| 字段 | 来源 | 说明 |
|---|---|---|
| episode_id / plan_id / product_id | Episode | 标定单元主键 |
| price_band, plan_purpose, life_cycle_stage | STATE / Genome category | 分层键 |
| inventory_state, activity_phase | STATE | 风险分层与活动剔除 |
| plan_mode (seed/harvest/mixed) | TrustedBusinessState | 频率/幅度分层 |
| env / mode / learning_pool | RuntimeEnvelope | 样本池过滤（LIVE vs SHADOW） |
| started_at / ended_at / outcome_label | Episode | 窗口与成败 |

#### 3.2.2 动作与门禁

| 字段 | 来源 | 说明 |
|---|---|---|
| action_type, target, before, after, delta_ratio | CausalRecord.action / TRACE | 幅度标定 |
| ts_action, ts_result, response_time | CausalRecord | 响应窗口标定 |
| daily_adjust_count | TRACE 聚合 | 频率上限 |
| risk_level, hard_block, constraints 版本 | RiskAssessment | 分档约束 |
| trust_level, TS 分量快照 | TE / TRACE | Trust 分带与权重标定 |
| from_state, to_state, reason_codes | ReviewEvent | APPROVE/REVISE/HOLD/REJECT/ESCALATE |

#### 3.2.3 结果与质量

| 字段 | 来源 | 说明 |
|---|---|---|
| metrics + attribution_flags | RawMetricSnapshot / BDV | 成交、ROI、CTR 等；待付款/退款/重复归因标记 |
| trust_state, validation_report | BDV | 是否纳入主标定集 |
| expected_effect vs result | CausalRecord | 预测准确率 D4 / T1 |
| O-H-A-R-R 完备位 | CausalRecord | e（D8） |
| evidence_causal_ids, n_rep 独立 Episode 数 | ExperienceCandidate / KE | D1、N_min |
| quality_score 历史、status 变更、governance | KnowledgeObject | 晋升/降权标签 |
| human_override / HUMAN_* | TRACE | T8、抽检、误放行/误杀 |

#### 3.2.4 预算与探索

| 字段 | 来源 | 说明 |
|---|---|---|
| budget_trace, B_spent, B_exp | STATE / TRACE | 探索预算标定 |
| projected_exhaust_at / budget lifetime | FE（若有） | 续量相关 |
| effectiveness_ratio 近期值 | BDV/STATE | E_min 标定 |
| new_plan_count | TRACE | N_new_max |

### 3.3 样本纳入 / 排除规则（进入清洗前的逻辑门）

| 规则 | 处理 | 理论/工程呼应 |
|---|---|---|
| `env != LIVE` | 默认仅进 Shadow/模拟标定辅集；不进 live 主标定 | Shadow §5；FQ-02 |
| BDV `trust_state=quarantined` 或 FAIL | 排除出主集；可作数据质量负样本 | 架构 P3；I5 |
| 标签缺失率过高（槽位键不全） | 观察样本，不进分层主集 | Genome S2 |
| 异常大额订单（BDV 标记） | 降权 / winsorize；禁止单独支撑规则 | FQ-01 |
| 活动爆发窗内样本 | 单独分层或 Overlay，不与常态混合估主阈值 | §11.1 动态放宽 |
| 平台异常窗口 | 默认不参与主蒸馏/主标定 | FQ-02 |

---

## 4. 标定流程（清洗 → … → 版本化）

### 4.1 端到端流水线

```text
[S0 授权与范围]
  指定标定对象（哪类阈值）、租户/时间窗、样本池（live only 或 live+shadow 辅）
        │
[S1 只读抽取]
  Memory / TRACE / BDV / STATE / KE 配置快照 → 标定工作区（只读镜像）
        │
[S2 清洗与标签]
  去重、归因修正、待付款/退款处理、异常订单标记、活动窗切分、槽位回填
        │
[S3 BDV 门禁]
  仅 trust_state=validated 进入主集；输出 validation_report 摘要
        │
[S4 分层]
  price_band × plan_purpose × life_cycle ± inventory/activity 子层
  样本不足槽位 → 继承父层 Prior，不强行估计
        │
[S5 分位 / 分箱]
  幅度、频率、窗口、成效比等 → p25/p50/p75 或分位箱；分类型指标分箱
        │
[S6 稳健估计]
  截尾/winsorize、MAD、分位回归或加权中位数；小样本用层级先验（见 §6）
        │
[S7 目标对齐与约束投影]
  估计值投影回 Risk/Trust/Q 的可行域（理论序、硬红线、单调性）
        │
[S8 回写 Proposed 包]
  生成 Calibration Patch：old/new、segment、evidence_refs、confidence、status=PROPOSED
        │
[S9 人工评审]
  负责人 / Research Architect 评审；SRA 检查清单；接受 / 拒绝 / 降级幅度
        │
[S10 版本化入库]
  calibration_version + lineage；绑定 Genome / Knowledge / baseline_version
        │
[S11 影子或沙箱验证（可选并行）]
  小预算影子 / 只读回放 → SM-M* 反馈 → 新 Proposed 迭代（见 §7）
        │
[S12 归档报告]
  样本量、剔除表、分层覆盖矩阵、未决槽位、风险声明
```

### 4.2 分阶段要点

#### S2–S3 清洗与 BDV

1. 使用去重后真实成交，不直接采用平台展示成交额标定 ROI（对齐 Genome S1）。  
2. `attribution_flags`（待付款、退款、跨计划、重复归因）进入 `validation_report`；高偏差计划可整段降权。  
3. 失败计划**不得**因 outcome=failure 排除；失败是 Q/D2/D6 与 Failure Pattern 的关键负例（§4.4 / MKB §4.4）。

#### S4 分层

| 分层键 | 取值来源 | 用途 |
|---|---|---|
| price_band | Genome category / STATE | TC-Q、TC-R、TC-T 全系 |
| plan_purpose | Seed / Harvest | 频率、幅度、目标序 |
| life_cycle_stage | Explore…Decline | 风险档与探索预算 |
| inventory_state | 充足→临界 | R 硬条件 |
| activity_phase | 无/预热/爆发/收尾 | 活动 Overlay，避免污染常态阈值 |

**继承规则（Proposed）：**  
`n_segment < n_min_segment` → 不输出该段独立估计；标记 `sample_size_low`；使用：父层分位 → 理论 Prior → 全局更保守值（三选一，记录选择）。

#### S5 分位 / 分箱

| 阈值类型 | 建议估计对象（Proposed） |
|---|---|
| 幅度上限 U_bid / U_bud | “成功且无风险事件”动作幅度的 p75–p90（偏保守可取 p75） |
| 日内频率 F_max | 成功会话日均调整次数分布的 p75 |
| min_response_window | 动作→首次可确认响应时间的 p25–p50（过短=过拟合噪声） |
| E_min / max_daily_loss_ratio | 成败计划比值分布的分位；失败侧 p10 等 |
| θ_promote / θ_observe | 用 Q 分布与事后标签做工作点选择（见 §4.3） |
| Trust Level 分带 | TS 与“权限决策错误代价”曲线的拐点 |

#### S6 稳健估计（防单点绑架）

1. **Winsorize** 指标尾部（如 1%/99%），异常订单单独标记而非删除记录。  
2. 优先 **分位数 / 加权中位数**，避免均值被活动爆发与大额订单拉偏。  
3. 对重复使用同一 product/plan 的样本做 **episode 聚类稳健 SE** 或简单降权，防止“一计划刷样本”。  
4. 输出 **bootstrap 区间**（示例方法，非实现绑定）：区间过宽 → 不 Proposed 新值，维持 Prior。

#### S7 约束投影（不可跳过）

标定数值必须满足：

1. Risk 硬红线语义不变（R4 永不被“标定放宽”）。  
2. 单调性：更高 R 档的幅度/频率上限 ≤ 更低档。  
3. Trust：升级附加条件不得弱于理论权限路径（§6.7）。  
4. Q：\(\theta_{observe} < \theta_{promote}\)；\(w_i≥0, Σw_i=1\)。  
5. 不改写理论指标序关系（Genome C7 / GA-1 §7.2–7.3）。

#### S8 回写 Proposed 包（逻辑结构）

```text
CalibrationPatch {
  calibration_id,
  calibration_version,          // 见 §8
  target_class: EXPERIENCE_Q | RISK_BASELINE | TRUST_SCORE,
  segment: { price_band?, plan_purpose?, life_cycle?, inventory?, activity? },
  field: symbol_or_parameter_id,
  old_value,                    // 当前 Proposed/Prior
  new_value,                    // 仍为 Proposed
  estimator: { method, window, winsorize, n_eff, ci_low, ci_high },
  evidence_refs: [ episode/causal/trace ids 摘要 ],
  excluded_summary: { bdv_reject, activity, anomaly, env_filter },
  confidence: HIGH | MEDIUM | LOW,
  status: PROPOSED,
  reviewer_queue: [ roles ],
  notes: Example-Only until approved
}
```

#### S9 人工评审

| 检查 | 内容 |
|---|---|
| 数据 | 是否仅 validated；活动/异常是否隔离；n_eff 是否达标 |
| 方法 | 分层是否合理；稳健估计是否使用；区间是否报告 |
| 业务 | 是否符合稳定性优先、探索预算、合规 |
| 治理 | 是否误用 shadow；是否触碰硬红线语义 |
| 决策 | Accept / Accept-with-narrower-band / Reject / Defer |

#### S10 版本化

见 §8。评审通过前，任何运行时组件**不得**加载新 patch 作为 live 约束。

---

## 5. 防过拟合与防噪声

### 5.1 风险清单

| 风险 ID | 表现 | 缓解 |
|---|---|---|
| TC-O01 | 活动爆发样本抬高幅度/放宽 ROI | 活动 Overlay 分层；窗后回落检查 |
| TC-O02 | 单一爆款/大额订单支配分位 | FQ-01 降权 + winsorize；禁止单样本支撑 |
| TC-O03 | 只用成功计划标定 → 过度乐观 | 成功/失败联合估计；Failure Pattern 强制入池（MKB §4.4） |
| TC-O04 | 重复计划刷 n_rep | 按独立 Episode / product 去重计数 |
| TC-O05 | 多重比较刷阈值 | 预注册标定对象清单；一次标定只动一族参数 |
| TC-O06 | 窗口过短学噪声 | min_response_window 下限；禁止短于理论先验下界的“最优窗” |
| TC-O07 | 影子高分驱动过宽 live 阈值 | Shadow 标注；live 标定默认 `env=LIVE` only |
| TC-O08 | 分层过碎导致空槽 | 继承 Prior；不编造段内估计 |

### 5.2 失败样本处理（呼应理论遗忘 / 降权）

| 策略 | 做法 | 不做 |
|---|---|---|
| 入库 | 失败 Episode 必须有 CausalRecord；outcome_label=failure | 无记录删除 |
| 标定集 | 作为负例参与 D2/D6、Trust T2/T3/T4、R 档后验 | 不因“结果为负”直接丢弃 |
| 降权 | BDV 异常、归因污染 → `weight_sample < 1` 或剔除出主集但保留审计 | 静默改写原始指标 |
| 遗忘 | 长期无复现且 Q_effective 低 → 观察/归档（FQ-03）；标定侧对应提高 \(\theta\) 或维持保守 | 物理删除证据链 |
| 反例 | 反例率超阈 → 强制降权建议 + Reflection Finding（FQ-04） | 用均值抹掉反例 |

### 5.3 时间与分布漂移

1. 标定报告必须声明 **样本时间窗** 与平台政策/大促季标记。  
2. 超过有效期（Proposed：一个大促周期或 90 天，Example-Only）的 patch 进入 `stale` 候选，触发重估而非自动删除。  
3. 连续两次影子/沙箱反馈方向与 patch 相反 → 回退评审（见 §7）。

### 5.4 与“理论遗忘”的对齐声明

- 理论 §9.4：遗忘 = 降低对未来决策的影响权重。  
- 本文将该原则用于**标定样本与阈值包**：旧 patch 可 downweight/stale，历史 evidence 不销毁；与 MKB FQ 规则、Risk 周反思 `RiskBaselinePatch` 同一治理哲学。

---

## 6. 冷启动（无历史 / 历史极薄）

### 6.1 路径总览

```text
阶段 CS-0  理论 Prior 装载
    全部阈值使用 MKB/Risk/Genome 中 Proposed 占位
    偏保守：高 θ_promote、紧幅度、低频率、高 E_min 倾向
        │
阶段 CS-1  只读与影子闭环
    MODE_READ / MODE_SHADOW_DECIDE；跑 SM-JD 最小任务集
    收集 SM-M01..M10，不更新 live Trust
        │
阶段 CS-2  小样本分层估计
    仅在 n_eff 达标的槽位输出 CalibrationPatch(Proposed)
    其余槽位继续继承 Prior
        │
阶段 CS-3  小步收紧/放宽策略
    按 §6.3 规则调整，每次变更幅度受限
        │
阶段 CS-4  首次历史预标定授权后
    走 §4 完整流水线；CS 期 patch 可作为对照基线
```

### 6.2 理论优先级先验（装载顺序）

| 优先级 | 内容 | 来源 |
|---|---|---|
| P0 | 硬红线与权限不变量（Trust 任意级不得绕过 SRA；R4 阻断） | Risk §2；架构 |
| P1 | 分档结构（价格带×目的×生命周期）与理论指标序 | GA-1 §7；Genome §4–5 |
| P2 | 幅度/频率/窗口的保守区间 | Risk §7；Genome §6 |
| P3 | Q 与 Trust 权重占位 | MKB §4；Risk §4 |
| P4 | 企业可覆盖项（绝对预算等） | 企业配置；PENDING_ENTERPRISE_SCALE |

### 6.3 小预算影子验证下的收紧 / 放宽规则（Proposed）

| 信号（影子域） | 阈值动作 | 幅度限制（Example-Only） |
|---|---|---|
| SM-M01 方向一致率持续低于门槛且 n 达标 | **收紧** 对应动作类幅度或提高 review_mode | 单次不超过当前值的 10–15% 相对变化 |
| SM-M02 NO_ACTION 正确率高但干预一致率低 | 可能过度干预 → 降 F_max 或加 min_response_window | 只动频率/窗口，不动硬红线 |
| SM-M03 预测命中率差 | 先修 FE/BDV，**禁止**用放宽阈值掩盖预测失败 | 阈值冻结 |
| SM-M07 误拒代理高 | 可微幅放宽该动作类，仍受 R 档约束 | 需人工评审 |
| SM-M09 数据校验影响率高 | 视为数据质量问题，不调整业务阈值 | 冻结 |
| SM-M10 隔离失败 | **立即停标定**；修复防污染 | — |
| 连续两期 SM 向好且 live 只读复盘一致 | 提交放宽的 Proposed patch | 仍需 S9 评审，不得自动 Active |

**原则：** 冷启动只允许**单方向、小步、可回滚**变更；放宽必须有影子 + 只读双证据，收紧可仅由风险信号触发。

### 6.4 冷启动禁止事项

1. 禁止用 Fixture / SIM 分布“证明” live 最优。  
2. 禁止在 n_eff 不足时输出段内独立估计冒充标定结果。  
3. 禁止把 `shadow_trust_proxy` 写入 live Trust Level。  
4. 禁止一次标定同时大改 Q、R、T 三族（耦合噪声）。

---

## 7. 与 Shadow Mode 指标 SM-* 的衔接

### 7.1 角色划分

| 角色 | SM 指标在标定中的作用 | 不做什么 |
|---|---|---|
| 反馈信号 | CS-3 收紧/放宽触发；§4 S11 迭代输入 | 不直接写 live Trust |
| 工作点参考 | SM-M01/M02/M03 用于选择 θ、F_max、窗口的候选 | 不替代 BDV 清洗后的主集估计 |
| 治理验收 | SM-M10 / P-01..05 失败则标定熔断 | 不把影子经验晋升 Rule/Genome |
| 升权材料 | SM 达标可支持“进入写权限评审”的材料 | 升权仍要新 GA-DEC + live 证据（Shadow §7） |

### 7.2 指标 → 阈值族映射（Proposed）

| SM 指标 | 主要反馈的阈值族 | 衔接方式 |
|---|---|---|
| SM-M01 方向一致率 | TC-R01/02、决策相关 Q（D4） | 低则收紧幅度或加强 review |
| SM-M02 NO_ACTION 正确率 | TC-R03/04、prefer_stability | 验证“不调整”价值；防过度干预 |
| SM-M03/M04 预测 | 不直接改阈值；驱动 FE/BDV | 阈值冻结直至预测可接受 |
| SM-M05 提前量 | TC-R04 响应窗口 | 窗口过短/过长的证据 |
| SM-M06/M07 门禁 | TC-T05–T07、N_revise | 误拒/误放行工作点 |
| SM-M08 幅度校准误差 | TC-R01/02 | 直接幅度回归输入（仍须稳健化） |
| TC-M09 数据校验影响 | 清洗与 BDV 规则 | 非业务阈值 |
| SM-M10 隔离完整率 | 标定熔断开关 | 1.0 为硬门槛 |

### 7.3 双池统计

```text
live_calibration_set     = filter(env==LIVE, trust_state==validated, 主分层)
shadow_feedback_set      = filter(env in {SHADOW,SIMULATION}, 隔离池)

主阈值估计  → 仅 live_calibration_set
影子反馈    → 仅用于 CS-3 与评审材料；patch 中 evidence 必须标注 shadow
禁止：将两集合合并后计算同一分位作为 live 终值
```

### 7.4 升权边界（重申）

对齐 Shadow §7.3：影子表现**不能**提高 live Trust Score；标定包也不得通过“影子分高”自动放宽 live 权限相关阈值。进入写权限仍需：新授权决策 + live 证据 + Trust 达标 + 人工否决保留。

---

## 8. 版本管理：`calibration_version` 与引用

### 8.1 版本标识

| 字段 | 约定 | 示例（Example-Only） |
|---|---|---|
| `calibration_version` | `CAL-{target_class}-{yyyyMM}[-{seq}]` | `CAL-RISK-202609-01` |
| `status` | `PROPOSED` / `APPROVED` / `ACTIVE` / `SUPERSEDED` / `REJECTED` | 评审前恒 PROPOSED |
| `baseline_version` | Risk 侧生效基线版本；与 patch 一对一或一对多 | `BL-2026-W38` |
| `trust_config_version` | TE 权重/分带配置版本 | `TRC-0.1.0` |
| `quality_threshold_version` | Q 权重与 θ 版本 | `QT-0.1.0` |
| `genome_ref` | 受影响 genome_id + version | `JD-LFM-HARVEST-MATURE@0.1.0` |
| `knowledge_ref` | 相关 KO id/version | `KO-experience-12@v2` |
| `evidence_digest` | 样本集摘要（时间窗、n、排除计数） | hash + 计数表 |

### 8.2 引用矩阵

| 标定产物 | 必须引用 | 可选引用 |
|---|---|---|
| TC-Q patch | knowledge_threshold_version、MKB FQ 规则版本 | shadow eval_id |
| TC-R patch | baseline_version、Genome risk_baseline version | activity overlay id |
| TC-T patch | trust_config_version、权限矩阵版本（Risk §5） | shadow_trust_proxy 报告 id |

### 8.3 生命周期

```text
PROPOSED ──评审通过──► APPROVED ──装载窗口──► ACTIVE
    │                      │                     │
    │                      │                     ├─新版本 SUPERSEDED（旧版只读保留）
    └─评审拒绝──► REJECTED  └─数据熔断/回退──► SUPERSEDED 或 回滚到上一 ACTIVE
```

**不变量：**

1. 任意 ACTIVE patch 必须可回滚到上一 ACTIVE 或出厂 Prior。  
2. SUPERSEDED 不物理删除；lineage 单向可追。  
3. 运行时 Decision / Shadow Packet 必须记录当时生效的 `calibration_version` 族（便于事后归因）。  
4. Research 仓库默认树只保存**方法**与 **Example-Only** 骨架；企业租户标定结果写入 `enterprise/` 运行期目录（对齐 Genome §8），不提交敏感数据。

### 8.4 与 Genome 状态机对齐

| Genome source/status | 标定关系 |
|---|---|
| Expert_Prior / Proposed | 冷启动 Prior；可被 CalibrationPatch 建议替换字段 |
| Calibrated | 完成 §4 流程且评审通过后的基因；必须带 quality_score 与 lineage.calibration_ref |
| Evolved | 运行期小幅修订；应指向最近 calibration_version |
| Deprecated/Retired | 旧阈值随基因退役；patch 一并 SUPERSEDED |

---

## 9. 端到端样例（Example-Only，非真实数据）

> **下列数字全部为 Example-Only，用于说明 Patch 结构，不得引用为真值。**

```text
场景：低客单 × 收割 × 成熟期；仅 LIVE 验证样本；活动窗已剥离。

输入摘要（示意）:
  n_episode = 42, n_eff = 35（去重后）
  成功动作幅度 p75 ≈ 12%（winsorize 后）
  风险事件率：幅度>15% 时显著上升

CalibrationPatch（示意）:
  target_class: RISK_BASELINE
  field: max_bid_delta_pct @ R1
  old: 0.20 (Proposed Prior)
  new: 0.12 (Proposed)
  estimator: quantile_p75 + winsorize_1_99, ci: [0.09, 0.15]
  status: PROPOSED → 等待人工评审
  note: Example-Only；非企业标定结果
```

若评审要求更保守，可将 new 收至 `0.10` 并保持区间披露；**任何情况下不得在无评审时写入 ACTIVE。**

---

## 10. 产出物清单

| 产物 | 说明 |
|---|---|
| 本方法论 | `Threshold_Calibration_Method_v0.1.md`（Draft） |
| CalibrationPatch 模板 | §4.2 S8 结构；落地时可 JSON Schema 化（后置） |
| 分层覆盖矩阵模板 | 20 槽位 × 样本量/状态（对齐 Genome 槽位） |
| 标定报告模板 | 样本量、剔除、分位表、CI、未决槽位、风险声明 |
| 熔断与回滚清单 | SM-M10、BDV 失败率、区间过宽、评审拒绝路径 |

**执行前提：** 真正跑历史抽取须单独授权（只读凭据、租户范围、时间窗）；本文不预授权执行。

---

## 11. 理论与工程追踪

| 内容 | 锚点 | 本文章节 | 状态 |
|---|---|---|---|
| 经验质量分与阈值 | GA-1 §9.3–9.4；MKB §4 | §2.1、§5.2 | Mapped（方法） |
| 动态风险基线 | GA-1 §11.1；Risk §3/§7 | §2.2、§4 | Mapped（方法） |
| Trust 八维与分带 | GA-1 §11.3；Risk §4 | §2.3 | Mapped（方法） |
| 失败可降权不可无记录丢弃 | §9.4；架构边界 | §5.2 | Mapped |
| 默认值 Proposed | GA-DEC-004 | 全文 | Enforced |
| 影子不升 live Trust | Shadow §5/§7 | §7.4 | Mapped |
| 基因预标定流程 | Genome §7 | §4 呼应、不重复实现 | Complementary |
| GA-3 验证 | 后续 | 仅预留钩子 SM-* / 报告 | Deferred |

**明确不声称：** 本文不含任何已验证阈值；不构成 GA-3 结论；不授权真实写操作或真实历史数据执行。

---

## 12. 待决问题

| ID | 问题 | 建议 | 阻塞 |
|---|---|---|---|
| TCAL-Q1 | 最小有效样本量 \(n_{min}\) 如何按槽位定义？ | 统计功效评估后定；先统一保守值并披露 CI | S5–S6 |
| TCAL-Q2 | 企业多租户是否分租户标定 vs 共享池？ | 默认租户内；跨租户仅方法共享，数值不合并 | 治理 |
| TCAL-Q3 | Q 权重能否用历史人工晋升结果直接回归？ | 可作工作点参考，但需防标签噪声；先固定序再调强度 | MKB-Q02 |
| TCAL-Q4 | Trust 八维权重是否预置企业类型 profile？ | 先单 profile；Profile 后置（Risk Q-R2） | TE |
| TCAL-Q5 | 活动 Overlay 是否独立 calibration_version？ | 是；与常态 patch 隔离 | 版本模型 |
| TCAL-Q6 | 影子反馈进入 patch 的上限权重？ | 默认只触发评审，不直接给 new_value 赋终值 | Shadow |
| TCAL-Q7 | 标定管道技术栈（Notebook vs 服务）？ | 方法先行；实现后置，不阻塞本文 | 实现 |
| TCAL-Q8 | `stale` 判定周期（90 天 / 大促周期）？ | 双条件先用较严者；首期后修订 | 运维 |
| TCAL-Q9 | 与 GA2-T15 预标定实验设计的分工？ | T14=阈值回填方法；T15=实验与模拟设计；交叉引用不重复 | 任务边界 |
| TCAL-Q10 | 是否允许在无 LIVE 样本时仅用影子标定？ | **否**；影子只能冷启动反馈，不能替代 live 主集 | 硬约束 |

---

## 13. 与后续任务的接口

| 下游 | 本文供给 |
|---|---|
| GA2-T15 参数预标定实验设计 | 分层键、稳健估计、Patch 结构、禁止事项 |
| KE / RKE / TE 配置实现 | 阈值清单 ID、版本字段、回写门禁 |
| Shadow Mode 运营 | SM-* 与阈值族映射、熔断条件 |
| GA-3 验证 | 标定前后对照指标定义入口；样本组织原则 |
| 负责人评审 | 待决问题 TCAL-Q*；升格 APPROVED 的检查单 |

---

## 14. 变更记录

| 日期 | 版本 | 变更 | 依据 |
|---|---|---|---|
| 2026-09-11 | v0.1 | 首次建立三类阈值清单、数据需求、标定流程、防过拟合/冷启动、calibration_version、SM-* 衔接与待决问题（方法论，非结果） | GA2-T14；GA-DEC-004；MKB/Risk/Genome/Shadow v0.1 |

---

**Document Status:** Draft  
**Next Stage:** Research Architect / 负责人评审 → 修订 v0.2；真实历史标定执行需单独授权  
**Explicit Non-claim:** 一切数值均为 Proposed / Example-Only；未运行真实账户或真实历史标定；未修改 GA-1 / PROJECT_SPEC；影子结果不得直接提升 live Trust 或绕过硬红线。
