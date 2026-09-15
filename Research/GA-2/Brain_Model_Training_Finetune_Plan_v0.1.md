# GA-2：2B 大脑模型训练与微调计划

**文档编号：** GA-2-BRAIN-001  
**任务编号：** GA2-T33  
**版本：** v0.1  
**状态：** Draft  
**阶段：** GA-2 Engineering Design（落地执行前置设计）  
**输入基线：** `Research/GA-1/GA-1_Theory_v1.0.md`（GA-1.0 / v1.0，Confirmed）  
**主线架构：** `Architecture_Overview_v0.2.md`（Confirmed，GA-DEC-004）  
**工程基线：** `GA-2.0_Baseline_Package.md`（Confirmed，GA-DEC-005）  
**强关联：**  
- `Reasoning_Engine_Interface_v0.1.md`（RE 契约与五场景骨架；关闭 RE-Q01 的实现侧提案）  
- `Decision_Packet_Schema_v0.1.md`（成长最小原子；模型输出最终落地形态）  
- `Gate_Integration_Playbook_v0.2.md`（双字段可执行判定；模型不得越权）  
- `Risk_Trust_SelfReview_v0.1.md`（Risk/Trust 预览；SRA 终审）  
- `Learning_Reflection_Runtime_v0.1.md`（回路 B；持续训练数据来源）  
- `Shadow_Mode_Design_v0.1.md` / `Shadow_Trial_Run_Plan_v0.1.md`（无写验证场）  
- `Parameter_Genome_Templates_v0.1.md`（OFG/Genome 先验；场景模板）  
- `Module_Skeleton_Design_v0.1.md`（实现分层；brain 挂载点）  
- `GA-3_Validation_Protocol_Draft_v0.1.md`（验证指标衔接）  
**授权依据：** 本计划为实现前工程设计草案；**不授权**真实写操作、真实账户只读连接、启动 GA-3。  
**约束：** 不修改 GA-1 理论基线；全部训练超参、数据配比、阈值与性能目标一律 **Proposed**；模型永不绕过 Risk/Trust/Self-review/Adapter 门禁；`env≠LIVE` 数据不得自动晋升企业规则或计入 live Trust。

---

## 0. 范围声明

### 0.1 一句话定位

> **2B 小模型是 Reasoning Engine（RE）的认知内核（Cognitive Kernel），不是整机 Growth Agent。**  
> 它把 Trusted State + ForecastBundle + Objective Snapshot + Knowledge refs + Risk/Trust 预览，映射为可审计的 `ReasoningBundle`（候选动作或合法 `NO_ACTION`/`HOLD_SUGGEST`）。  
> Schema 校验、风险硬红线、响应窗口、Trust 半径、门禁终审全部由确定性层强制执行——**模型提案，系统拍板**。

### 0.2 本轮要做

1. 明确 2B 模型在四回路与 M-CORE 中的职责边界（做什么 / 永不做什么）。  
2. 给出基座选型建议（Proposed）与混合 RE（Hybrid Reasoning）运行时架构。  
3. 将 RE 输入/输出契约转成可训练的任务定义与提示/输出规范。  
4. 定义四阶段数据与训练流水线（SFT → 偏好对齐 → 约束解码精修 → Shadow 持续学习）。  
5. 定义评估套件、门禁指标与 GA-2/GA-3 验收衔接。  
6. 给出资源估算、里程碑、风险与待决问题。

### 0.3 本轮明确不做

| 项 | 说明 |
|---|---|
| 训练代码实现 / 权重发布 | 本文是计划与契约，不是训练仓 |
| 真实京东/抖音 API 或凭证 | 严格遵守只读/Shadow 红线 |
| 用模型替代 SRA / Risk / Trust / Adapter | 门禁不变量不可协商 |
| 把训练结果表述为已验证经营能力 | 须经 GA-3 与标定后升格 |
| 修改 GA-1 / Architecture v0.2 主线 | 偏离须新 `GA-DEC-NNN` |
| 启动 GA-3 | 仅预留评估钩子 |

### 0.4 与 RE-Q01 的关系

`Reasoning_Engine_Interface_v0.1.md` §9 RE-Q01 明确「内核形态（规则 / LLM / 混合）实现阶段再定」。  
**本计划提案：采用 Hybrid RE**——确定性骨架管硬约束与合规，2B 模型管观察解读、假设排序、候选生成与可解释对齐说明。该提案为 Draft，须负责人确认后写入新决策。

---

## 1. 为什么是 Hybrid，而不是「纯 LLM 大脑」

### 1.1 架构硬约束决定了分工

GA-2 不变量要求：

| 不变量 | 含义 | 对模型的含义 |
|---|---|---|
| 门禁先于智能 | Reasoning → Risk → Trust → SRA → Execute | 模型输出永远是 **Draft 候选**，不是批准动作 |
| `review_result` 仅 SRA 可写 | Gate 双字段语义 | 模型 JSON 中若出现 `review_result`/`APPROVE` 等字段 → **硬校验拒绝** |
| `NO_ACTION` 一等公民 | DPK-I2 必须成包 | 模型必须学会「有意识不动」，且输出完整 NO_ACTION 候选 |
| 预测先于动作 | 无有效 Forecast 不得写动作 | 模型收到 FE `BLOCKED` 时只能出 NO_ACTION/HOLD |
| 只信校验后状态 | Raw 禁入 hypothesis | 提示词只注入 Trusted/Validated 摘要，不给 Raw 指标 |
| Shadow 写路径硬拒绝 | DPK-I5 | 模型不感知执行通道；由 RuntimeEnvelope 隔离 |

**结论：** 把「合规与硬约束」交给确定性代码，把「经营解释与候选构造」交给 2B 模型。纯端到端 LLM 既难保证 Schema/门禁，也违背「门禁先于智能」的工程主张。

### 1.2 混合 RE 运行时（Proposed）

```text
ReasoningRequest
        │
        ▼
┌───────────────────────────────┐
│  Pre-Assembler（确定性）        │
│  · 压缩/脱敏 Trusted State     │
│  · 注入 Forecast 摘要+关键对象  │
│  · 注入 Objective Snapshot     │
│  · 注入 Knowledge refs 摘要    │
│  · 注入 Risk/Trust 预览        │
│  · 强制场景候选集 / 白名单动作类 │
└───────────────┬───────────────┘
                │  BrainPrompt（结构化）
                ▼
┌───────────────────────────────┐
│  2B Cognitive Kernel           │
│  · 场景路由建议                │
│  · observation → cause_claim   │
│  · PRIMARY/ALT/NA/HOLD 候选    │
│  · 幅度/窗口/expected_effect   │
│  · objective_alignment 说明    │
└───────────────┬───────────────┘
                │  ReasoningBundleDraft(JSON)
                ▼
┌───────────────────────────────┐
│  Post-Validator（确定性）       │
│  · JSON Schema / 枚举校验      │
│  · 幅度≤Risk 预览；窗口冷却     │
│  · hard_block / Trust 半径过滤 │
│  · FE BLOCKED → 仅 NA         │
│  · 互斥动作 / 同对象冲突检测    │
│  · 违规则 REVISE 或降级 NA     │
└───────────────┬───────────────┘
                │  ReasoningBundle（契约合法）
                ▼
        CBA → Decision Packet Draft → RKE/TE/SRA
```

**失败策略：** 模型输出非法且无法自动修复 → 强制 `NO_ACTION` 包 + `degrade_reasons=["BRAIN_OUTPUT_INVALID"]`，禁止静默丢包（对齐 DPK-I2）。

---

## 2. 模型职责边界（必须写进实现验收）

### 2.1 主责（Primary Tasks）

| 任务 ID | 任务 | 输入 | 输出 | 理论锚点 |
|---|---|---|---|---|
| B-T1 | **ReasoningBundle 生成** | BrainPrompt（§4） | 合法 ReasoningBundle JSON | RE 契约；GA-1 §6.2/8 |
| B-T2 | **场景骨架路由** | State 特征 + Forecast 面板 | `scenario_skeleton_id` + 命中理由 | RE §4 五骨架 |
| B-T3 | **假设构造与鉴别** | observation 面板 + 知识先验 | hypothesis + rival_hypotheses | GA-1 §6.4 可反驳 |
| B-T4 | **NO_ACTION / HOLD 判定** | 稳定性/噪声/置信/窗口信号 | NA 候选或 HOLD_SUGGEST | 架构 P5；RE-P4 |
| B-T5 | **目标对齐说明** | Objective weights + 候选 | `objective_alignment` 人读说明 | 动态目标函数；SRA CHK_GOAL |

### 2.2 副责（Secondary，Stage-2 后可选开启）

| 任务 ID | 任务 | 说明 | 边界 |
|---|---|---|---|
| B-T6 | Reflection Finding 草稿 | 从 Packet+Outcome 起草复盘要点 | **仅草稿**；RFE 校验后才入 Report |
| B-T7 | ExperienceCandidate 草稿 | 从 CausalRecord 蒸馏经验表述 | **不得**直接写 KE；须质量分与治理 |
| B-T8 | SRA 解释辅助 | 生成人类可读检查说明 | **不写** `review_result`；SRA 谓词仍确定性/规则优先 |

### 2.3 永不做什么（Hard Negatives）

模型及推理包装层 **禁止**：

1. 输出或填充 `review_result`、`lifecycle_status=Self-reviewed/Executed`、`executor` 执行确认。  
2. 产出未经 Post-Validator 的幅度/频率超限写动作。  
3. 在 FE `BLOCKED` / STATE `validation_confidence=LOW` 时产出非 NO_ACTION 写动作。  
4. 伪造 `knowledge_basis`（无匹配知识时必须 `[]`）。  
5. 引用 Raw 指标作为 `observation` 主证据（只能引用 Trusted 摘要中的 validated 指标）。  
6. 绕过 Adapter；构造真实 API 参数或凭证。  
7. 在 `env≠LIVE` 样本上声称「已验证经营结论」或触发规则自动晋升。

以上违规在训练中作为 **负偏好样本 + 硬过滤规则** 双重压制。

---

## 3. 基座选型（Proposed）

### 3.1 选型原则

| 原则 | 要求 | 原因 |
|---|---|---|
| C1 中文经营语境 | 中文指令跟随强 | 京东域、运营话术、复盘文本以中文为主 |
| C2 结构化输出 | JSON / 函数调用可靠 | ReasoningBundle 必须可 Schema 校验 |
| C3 可本地/私有部署 | 2B 级、可 LoRA | 企业数据不出域；成本可控 |
| C4 长上下文够用 | ≥8k tokens（目标 16k） | State 摘要 + Forecast 对象 + 知识 refs |
| C5 许可证友好 | 商用允许微调与私有部署 | 研究落地与后续产品化 |
| C6 教师可蒸馏 | 易用 7B/14B 教师生成 SFT | 小模型冷启动依赖高质量合成数据 |

### 3.2 候选矩阵（2026-09 草案，**Proposed**）

| 优先级 | 基座（约 1.5–3B） | 优势 | 风险 |
|---|---|---|---|
| **P0 推荐** | Qwen2.5-1.5B-Instruct 或 Qwen2.5-3B-Instruct | 中文强、JSON 好、生态成熟、LoRA 稳 | 1.5B 复杂假设鉴别能力有限 |
| P0 备选 | Qwen3-1.7B / Qwen3-4B（若训练栈就绪） | 推理/结构化更新 | 版本迭代快，需锁定 revision |
| P1 | MiniCPM / InternLM2.5-1.8B 级 | 中文与工具调用可 | 社区工具链碎片化 |
| P2 | Llama-3.2-1B/3B-Instruct | 国际生态 | 中文经营语境弱于 Qwen |
| 教师（不部署） | Qwen2.5-7B/14B-Instruct 或更大 | 合成高质量轨迹 | 仅离线；不进生产链路 |

**默认锁定（待负责人确认）：**  
- **部署基座：** `Qwen2.5-3B-Instruct`（若显存/延迟预算紧则 `1.5B`）  
- **教师模型：** `Qwen2.5-7B-Instruct`（或 14B）仅用于数据合成与偏好标注辅助  
- **训练方式：** LoRA（主）+ 可选全参 SFT（仅 1.5B 且数据充足时）

> 选型本身不是理论结论；实现阶段可替换，但 **必须保持 RE I/O 契约与门禁不变量**。

### 3.3 推理形态（Proposed）

| 维度 | 建议 |
|---|---|
| 解码 | temperature 0.2–0.4（决策）；0 用于回归测试 |
| 约束解码 | JSON Schema guided decoding（若栈支持）；否则强 Post-Validator |
| 延迟预算 | Shadow/日内回路：P95 < 2–4s（本地 GPU，Proposed） |
| 并发 | 同 scope 串行（对齐 RFE 队列思想）；跨 scope 可并行 |
| 部署 | vLLM / llama.cpp / TensorRT-LLM 任一；不绑死 |

---

## 4. 任务定义：BrainPrompt → ReasoningBundle

### 4.1 输入规范（BrainPrompt）

Pre-Assembler 产出的提示包（逻辑字段，非固定自然语言模板）：

```text
BrainPrompt {
  task: "RE_REASON" | "RE_REVISE" | "RFE_DRAFT" | "LE_DRAFT"
  request_id, as_of, runtime_env: FIXTURE|SIMULATION|SHADOW|LIVE
  decision_intent?, scenario_hint?, prior_packet_id?, revise_feedback?

  state_digest: {          // 仅 Trusted/Validated 摘要
    plan_mode, lifecycle_phase, plan_status,
    trusted_metrics_summary, budget_summary,
    inventory_summary, active_events,
    validation_confidence, gap_flags, working_context_id
  }
  forecast_digest: {
    status: OK|DEGRADED|BLOCKED,
    overall_confidence,
    key_objects: [ {object_id, headline, bands?, noise?, eta?, burst?, inv_risk?} ]
  }
  objective_snapshot: { template_id, weights, lifecycle_bias?, valid_until? }
  knowledge_refs: [ {id, version, kind, summary} ]   // 摘要，非全文
  genome_ref?: { id, version, prefer_stability, response_window_hours, adjustment_policy }
  risk_trust_preview: { risk_level_hint, hard_block_flags, max_*_delta_pct,
                        allow_new_plan, trust_actual, trust_required_map }

  allowed_action_classes: [...]     // 预览约束后的白名单
  forced_no_write: bool             // FE BLOCKED / hard_block 等
  output_schema_hint: "ReasoningBundle@0.1"
}
```

**硬规则：** 不向模型注入原始平台 Raw 日志、密钥、完整账户 PII；只给决策所需摘要。

### 4.2 输出规范（ReasoningBundleDraft）

严格对齐 `Reasoning_Engine_Interface_v0.1.md` §3，模型只产出 RE 字段：

```json
{
  "status": "OK | DEGRADED | BLOCKED | NO_ACTION_ONLY",
  "primary_candidate_id": "REC-001",
  "scenario_skeleton_id": "SC-SEED-INTRADAY-DROP",
  "confidence_self": 0.72,
  "degrade_reasons": [],
  "knowledge_basis_used": ["EXP-12@1.0"],
  "candidates": [
    {
      "candidate_id": "REC-001",
      "candidate_role": "PRIMARY",
      "action_class": "KEYWORD_BID",
      "hypothesis": {
        "observation": {"window": "...", "metrics": {}, "baseline_ref": "...", "state_id": "..."},
        "cause_claim": "关键词竞争增强导致排名份额下降",
        "confidence": 0.68,
        "supporting_signals": [],
        "rival_hypotheses": ["素材疲劳", "数据延迟"],
        "knowledge_basis": []
      },
      "proposed_actions": [
        {
          "action_id": "ACT-001",
          "action_type": "WA-BID-01",
          "action_class": "KEYWORD_BID",
          "target": {"plan_id": "P1", "keyword_id": "K9"},
          "change": {"field": "bid", "relative_pct": 8},
          "priority": 1,
          "rationale_ref": "hypothesis",
          "within_risk_preview": true
        }
      ],
      "expected_response_window": {"min_minutes": 120, "max_minutes": 360, "metric_hint": ["impressions", "clicks"]},
      "expected_effect": {"direction": "recover", "metric_targets": {}, "side_effect_notes": []},
      "objective_alignment": {"summary": "…", "weight_notes": "…"},
      "risk_awareness": {"note": "…"},
      "rival_hypotheses": []
    }
  ],
  "no_action_candidate": null
}
```

**JSON 禁字段（出现即拒绝）：** `review_result`、`lifecycle_status`、`trust_score` 本体写入、`executor` 执行结果、平台原始 API payload。

### 4.3 确定性后处理规则（与模型能力解耦）

| 规则 ID | 检查 | 失败处理 |
|---|---|---|
| V-01 | JSON Schema / 必填字段 / 枚举 | 重试 N 次（Proposed=2）→ 强制 NO_ACTION |
| V-02 | `relative_pct` ≤ Risk 预览上限 | 降幅重写或标 ALTERNATIVE + `within_risk_preview=false` |
| V-03 | hard_block 非空 → 删除对应写动作 | 若无剩余 → NO_ACTION |
| V-04 | trust_actual < trust_required | 删除该动作类或改 ADVISE/NA |
| V-05 | 同对象同向未过 `min_response_window` | 删除同向 PRIMARY |
| V-06 | FE BLOCKED / confidence 过低 | 强制 NO_ACTION_ONLY |
| V-07 | 动作互斥（清仓 vs 扩种草等） | 保留 objective 对齐更高者 |
| V-08 | 禁字段扫描 | 整包拒绝 → NO_ACTION + degrade |
| V-09 | `NO_ACTION` 必须有 `no_action_reason` + 完整 hypothesis | 补全或拒绝 |
| V-10 | 骨架不在注册表 | 降为 AUTO 路由或 HOLD |

> Post-Validator 是 **门禁前置收敛**，不是 SRA 终审；最终 `review_result` 仍只由 SRA 写入。

---

## 5. 数据战略

### 5.1 数据分层与来源

| 层 | 名称 | 来源 | 用途 | 是否可进训练 |
|---|---|---|---|---|
| D0 | **契约/骨架合成** | 五场景骨架 × Fixture/Mock State/FE/OFG | 冷启动 SFT：学会格式与硬规则 | 是 |
| D1 | **专家轨迹** | 资深投手/研究员对同一 Prompt 手写 Bundle | 行业常识与判断风格 | 是（脱敏） |
| D2 | **规则蒸馏** | 由确定性 RE 规则版生成「金标」 | 保证底线行为（幅度、NA、窗口） | 是 |
| D3 | **教师合成** | 7B/14B 教师按契约生成 + 自动过滤 | 扩多样性与长尾场景 | 是（过滤后） |
| D4 | **仿真回放** | FIXTURE/SIMULATION 环境多策略 rollout | 策略对比与偏好对 | 是 |
| D5 | **Shadow 运行** | Shadow 包 + 后验 outcome + SRA 结果 | 偏好学习 / 难例挖掘 | 是（授权后） |
| D6 | **Reflection 闭环** | RFE Report / ExperienceCandidate / Failure Pattern | 持续微调与对齐 | 是（治理过滤后） |
| D7 | **LIVE 真实账户** | 京东只读/写回执 | 最终校准 | **须单独授权**；默认不进 |

**污染规则（对齐 Shadow 设计）：**

- `env∈{FIXTURE,SIMULATION,SHADOW}` 样本必须打 `source_env` 标签；训练集可混用，但 **评估报告必须分 env 汇报**。  
- `env≠LIVE` 的「成功」不得标注为已验证经营真值；偏好标签以「契约合法 + 与金标/规则一致 + SRA 不 REJECT」为准。  
- Failure Pattern 与 REJECT 包 **必须** 进入难例集（架构 P6：失败即学习事件）。

### 5.2 规模建议（Proposed，非承诺）

| 阶段 | 样本量级（有效） | 构成 |
|---|---|---|
| SFT-0 契约 | 2k–5k | D0+D2 为主 |
| SFT-1 业务 | 8k–20k | D1+D3+D2；五骨架覆盖均匀 |
| 偏好 DPO | 3k–10k pair | D4/D5/SRA 结果 + 违规负例 |
| 持续学习 | 每周 0.5k–2k 增量 | D6 Shadow+RFE 过滤 |

2B 模型不需要海量；**质量与契约对齐 > 数量**。单场景有效样本建议 ≥ 1k（SFT）以避免骨架偏斜。

### 5.3 场景覆盖矩阵（SFT 必覆盖）

| 骨架 | 必须覆盖的子情形 | 默认期望行为 |
|---|---|---|
| SC-SEED-INTRADAY-DROP | 显著下滑 / 噪声内 / FE 降级 / hard_block | 小步 BID/PRM 或 NA |
| SC-BUDGET-LIFETIME | 安全 / 偏紧 / 触红线 / 异常消耗 | 小步加预算 / 降速 / NA |
| SC-HARVEST-STABILITY | 稳定 / 轻微波动 / 显著恶化 | **默认 NO_ACTION** |
| SC-CAMPAIGN-WINDOW | PRE / PEAK / POST / 叠加库存紧 | 窗口内获量或收敛 |
| SC-INVENTORY-TIGHT | TIGHT / CRITICAL / 清仓 | 禁扩量；降速/维持/NA |
| 跨骨架 | 多骨架同时命中 / 无知识 / Trust 低 | 规则优先级 + HOLD/NA |

另需 **对抗/安全子集**：模型试图写 `review_result`、编造 knowledge、Raw 指标、超幅度、FE BLOCKED 仍放量——全部标为负例。

### 5.4 标注规范（人机协同）

| 标签 | 取值 | 谁标 |
|---|---|---|
| schema_valid | bool | 自动 |
| gate_compatible | bool | 自动（Post-Validator） |
| skeleton_correct | 五骨架 + OTHER | 专家/教师+抽检 |
| hypothesis_plausible | 0–2 | 专家 |
| action_reasonableness | 0–2 | 专家 |
| no_action_correctness | 0–2 | 专家（关键） |
| objective_alignment | 0–2 | 专家 |
| sra_outcome | APPROVE / NO_ACTION_APPROVE / REVISE / HOLD / REJECT | SRA 模拟或真实门禁 |
| outcome_met_prediction | bool | RFE（有 outcome 时） |

**金标 Bundle 的硬条件：** `schema_valid ∧ gate_compatible`；其余质量分用于过滤与 DPO 排序。

### 5.5 与企业知识资产的衔接

| 知识对象 | 在训练中的用法 |
|---|---|
| Rule / Strategy | 注入 prompt 摘要；生成时必须能引用或显式空 |
| Parameter Genome | 幅度/窗口/`prefer_stability` 先验；约束幅度 |
| Experience / Case | 正负例检索增强（RAG in prompt，不先全量记忆进权重） |
| Failure Pattern | 硬负例与 rival_hypotheses 生成素材 |
| CausalRecord | B-T6/T7 草稿任务输入 |

> **原则：** 企业可演化知识放 KE + prompt 注入；模型权重只沉淀「如何按契约推理」的通用能力。避免把可变经营规则烧死进 2B 权重。

---

## 6. 四阶段训练流水线

### 6.1 总览

```text
[数据准备] → [SFT-0 契约对齐] → [SFT-1 业务能力] → [DPO/偏好对齐]
                                                      ↓
              [约束解码 + Post-Validator 联调] ←———————┘
                              ↓
              [Shadow 试运行评估] → [持续学习 / 重训触发器]
                              ↓
              [GA-3 验证协议指标正式评估]
```

### 6.2 Stage-A：契约 SFT（SFT-0）

**目标：** 100% 产出可解析 JSON；禁止禁字段；掌握 NA/HOLD 基本形态。

| 项 | 值（Proposed） |
|---|---|
| 方法 | LoRA SFT |
| 数据 | D0+D2，约 2k–5k |
| 学习率 | 1e-4（LoRA） |
| epoch | 2–4 |
| 序列长度 | 8k |
| 早停 | schema_valid ≥ 99.5% 且 gate_violation ≈ 0 |

**退出标准（Exit-A）：**

- 自动校验 `schema_valid ≥ 99.5%`  
- 禁字段出现率 < 0.5%  
- FE BLOCKED 子集上非 NA 写动作率 < 1%  
- 五骨架均有 ≥ 200 条通过样本  

### 6.3 Stage-B：业务 SFT（SFT-1）

**目标：** 在契约之上学会场景路由、假设鉴别、幅度与窗口、目标对齐。

| 项 | 值（Proposed） |
|---|---|
| 方法 | 继续 LoRA（或合并后新 LoRA） |
| 数据 | D1+D3+D2 精选，8k–20k；按骨架分层采样 |
| 配比建议 | 种草 25% / 预算 20% / 收割稳定 20% / 活动 15% / 库存 10% / 跨场景对抗 10% |
| 关键损失加权 | NO_ACTION 正确样本 ×1.5；违规负例在偏好阶段处理 |

**退出标准（Exit-B）：**

- 骨架路由准确率 ≥ 85%（相对金标）  
- 收割稳定子集 NO_ACTION 正确率 ≥ 90%  
- 幅度超限率（Validator 前）≤ 10%；Validator 后 ≤ 0.5%  
- 专家抽检 action_reasonableness 均分 ≥ 1.4/2  
- REVISE 场景（带 revise_feedback）修复率 ≥ 70%  

### 6.4 Stage-C：偏好对齐（DPO / 可选 RLHF-lite）

**目标：** 拉开「合规且合理」vs「违规/贪婪/乱动」的间隔；压制门禁越权。

| 项 | 值（Proposed） |
|---|---|
| 方法 | DPO（主）；可选 ORPO |
| Pair 来源 | 同 Prompt 下：金标/规则金标 vs 模型采样中违规或低分样本；SRA REJECT vs APPROVE |
| 难例挖掘 | Validator 失败、SRA REVISE 循环耗尽、RFE `prediction_error` 高、误杀 NO_ACTION |
| β | 0.1–0.3 |

**偏好原则（与理论对齐）：**

1. 合规 NA > 贪婪写动作（P5 稳定性可战胜贪婪）  
2. 有假设与 rival 的小步动作 > 无依据大调  
3. 引用真实 knowledge_refs > 编造 basis  
4. 遵守 Risk/Trust 预览 > 超半径  
5. FE 降级时诚实 HOLD > 伪精确  

**退出标准（Exit-C）：**

- 相对 Stage-B：gate_violation 下降 ≥ 50%  
- SRA 模拟 REJECT 率下降 ≥ 30%  
- NO_ACTION 正确率不降（≥ Exit-B）  
- 过度保守误检：显著恶化却 NA 的错误率 ≤ 15%（防「永远不动」）  

### 6.5 Stage-D：约束运行时联调 + Shadow

**目标：** 把模型嵌进 Hybrid RE，用 Shadow Trial 计划做无写验证。

| 检查项 | 通过线（Proposed） |
|---|---|
| 端到端 JSON 可装配 Decision Packet Draft | 100%（含强制 NA 回退路径） |
| REVISE 回路（≤2 轮）可完成 | ≥ 90% 用例 |
| 平均/ P95 延迟 | 满足 §3.3 |
| 熔断：连续 N 次非法输出 | N=5 → 熔断到规则-only RE + 告警 |
| Shadow 包审计完整性 | decision_id / envelope / degrade_reasons 齐全 |

**明确：** Stage-D **不产生**平台写副作用；对齐 `Shadow_Trial_Run_Plan_v0.1.md`。

### 6.6 Stage-E：持续学习（回路 C 反哺模型，而非只反哺 KE）

```text
Shadow/Live(授权后) Decision Packet
  → outcome_ref → RFE Report
  → 过滤：contract 合法 + 有可学习信号
  → 难例 / 偏好 pair / 增量 SFT 语料
  → 周期性微调（Proposed：每 1–2 周增量，或触发器驱动）
  → 版本：brain_model@semver + 训练数据快照 hash
```

**触发重训（任一）：**

| 触发器 | 阈值（Proposed） |
|---|---|
| schema_valid 崩溃 | < 97%（Shadow 连续 3 日） |
| NO_ACTION 正确率下滑 | 较基线 −10pt |
| SRA REJECT 率上升 | 较基线 +50% 相对 |
| 新骨架/新平台域注册 | 必须增量 SFT |
| 阈值标定（TCAL）大幅更新 | prompt 中的约束摘要变更 |

**硬约束：** 持续学习数据必须带 `source_env`；LIVE 数据入模 **须新决策授权**；每次重训保留 prior 版本与评估对比报告。

---

## 7. 评估套件（与 GA-3 衔接）

### 7.1 自动指标（每版本必跑）

| 指标 | 定义 | 门槛（Proposed，Exit-C 后） |
|---|---|---|
| schema_valid_rate | Schema 通过 | ≥ 99% |
| gate_violation_rate | V-02..V-08 违规（Validator 前） | ≤ 2% |
| forced_na_rate | 因输出非法被强制 NA | ≤ 1% |
| skeleton_route_acc | 骨架路由准确率 | ≥ 85% |
| no_action_precision / recall | NA 正确性 | P≥0.90 / R≥0.85 |
| over_action_rate | 应 NA 却写动作 | ≤ 8% |
| under_action_rate | 显著恶化仍 NA | ≤ 15% |
| magnitude_violation | 超 Risk 预览幅度 | ≤ 1%（后） |
| window_violation | 冷却期内同向 | 0（后） |
| knowledge_hallucination | 伪造 basis | ≤ 1% |
| revise_repair_rate | REVISE 后合规修复 | ≥ 70% |
| objective_align_score | 对高权指标方向一致性 | 报告用 |

### 7.2 人工抽检协议

- 每版本每骨架 ≥ 30 包双人盲评（reasonableness / NA 正确 / 假设质量）。  
- 分歧率 > 20% 时升级仲裁并回写标注指南。  
- 抽检报告入 `Research/GA-2/` 评估附录（实现阶段）。

### 7.3 与 GA-3 验证协议的衔接（草案级）

| GA-3 关注点 | 模型侧供给指标 |
|---|---|
| 预测驱动是否成立 | 条件于 FE 质量分层的决策质量 |
| 稳定性是否可战胜贪婪 | NA 正确率、误动作率 |
| 经验是否可蒸馏 | B-T6/T7 草稿被 RFE/LE 采纳率 |
| Trust 是否可成长 | 模型包的 SRA APPROVE 率与后验达成率（仅 LIVE 时） |
| 门禁是否有效 | 违规样本在 Validator/SRA 的拦截召回 |

> GA-3 正式协议未启动前，以上仅为钩子，不构成验证结论。

---

## 8. 工程挂载与目录建议（对齐 Module Skeleton）

```text
garp/
├── brain/                          # Proposed：大脑子系统
│   ├── README.md
│   ├── configs/
│   │   ├── base_model.yaml         # 基座、revision、dtype
│   │   ├── prompt_templates/       # BrainPrompt 渲染（版本化）
│   │   └── decode.yaml             # temperature、guided json
│   ├── assemble/
│   │   ├── pre_assembler.py        # State/FE/OFG/KE 压缩
│   │   └── post_validator.py       # V-01..V-10
│   ├── serve/
│   │   └── reasoner_client.py      # 对 M-CORE-RE 暴露 reason()
│   ├── train/
│   │   ├── data/                   # 仅 schema + 生成脚本；语料可外置
│   │   ├── sft/
│   │   ├── dpo/
│   │   └── eval/
│   └── tests/
│       ├── test_contract_roundtrip.py
│       ├── test_hard_constraints.py
│       └── test_forced_no_action.py
```

**依赖方向：** `brain` → 契约类型（schemas）→ 被 `core.reasoning` 调用；**禁止** `brain` 依赖 `domain` 写路径或 `gate.review_result` 写接口。

---

## 9. 资源估算（Proposed）

| 项 | 3B LoRA 主路径 | 1.5B 紧凑路径 |
|---|---|---|
| 训练 GPU | 1×A100/L40S 40GB 或 2×4090（QLoRA） | 1×24GB 可 QLoRA |
| SFT-0/1 时长 | 约 4–12 小时/阶段 | 更短 |
| DPO 时长 | 约 4–10 小时 | 更短 |
| 推理 | 本地 1×GPU 或 CPU/Apple Silicon 量化（评估用） | 更易端侧 |
| 教师合成 | 7B API 或本地 7B，离线批量 | 同左 |
| 存储 | 基座 + 多版本 LoRA + 数据快照，约 20–80GB | 较小 |

**人力（建议）：** 1 名 ML 工程（训练/评估）+ 1 名领域专家（标注/抽检）+ 现有 Research Engineer（契约与 Validator）。小团队可并行压缩为 1.5 人。

---

## 10. 里程碑与依赖

| 里程碑 | 内容 | 退出标准 | 依赖 |
|---|---|---|---|
| **B-M0 计划确认** | 本文审阅；确认 Hybrid + 基座 | 负责人确认或新 GA-DEC | 无 |
| **B-M1 契约与夹具** | BrainPrompt/Bundle Schema；五骨架 Fixture 包 ≥ 200 | 回归测试绿 | DPK/RE 文档；无真实连接 |
| **B-M2 契约模型** | SFT-0 + Post-Validator | Exit-A | B-M1 |
| **B-M3 业务模型** | SFT-1 + 专家抽检 | Exit-B | B-M2 + D1 专家时间 |
| **B-M4 对齐模型** | DPO + 对抗集 | Exit-C | B-M3 |
| **B-M5 Shadow 联调** | 嵌入 Hybrid RE；跑 Shadow Trial 子集 | Exit-D；报告归档 | B-M4 + GA2-T26 环境 |
| **B-M6 持续学习就绪** | 数据管道 + 版本门禁 + 重训触发器 | 演练一次增量 | B-M5 |
| **B-M7 GA-3 输入就绪** | 评估报告与指标定义冻结 | 待 GA-3 启动决策 | B-M5 + GA-DEC |

**关键路径：** B-M1 Fixture 质量 → 决定 SFT 上限；专家时间集中在 B-M3；**不依赖**真实只读连接即可完成 B-M0–B-M4。

---

## 11. 风险与缓解

| 风险 | 影响 | 缓解 |
|---|---|---|
| 2B 容量不足，假设鉴别弱 | 误动作 | Hybrid：强 Validator；检索注入 Knowledge；难则 HOLD/NA |
| 训练成「永远 NO_ACTION」 | 失去决策价值 | under_action 指标门槛；显著恶化子集加权；DPO 平衡 |
| 训练成「刷存在感」 | 破坏稳定（违 P5） | 收割稳定子集加权；over_action 指标；SRA REJECT 偏好 |
| JSON 幻觉 / 格式漂移 | 链路崩溃 | 强制 NA 回退；熔断；guided decoding |
| 数据泄漏 LIVE 未授权 | 治理违规 | source_env 强制；入模审查清单；审计 |
| 把 Proposed 阈值当真值 | 科研不严谨 | 所有超参与门槛文内 Proposed；TCAL 后统一回填 |
| 教师合成偏见 | 系统性错误 | 规则金标并行；专家抽检；失败模式对抗集 |
| 版本漂移（基座升级） | 不可复现 | 锁 revision；训练数据 hash；评估锁 |
| 模型输出被误当作已批准 | 安全事故 | 类型上无 review_result；Packet 组装器拒绝；双字段门禁 |

---

## 12. 实现前检查清单（负责人）

- [ ] 确认 Hybrid RE 提案（关闭或改写 RE-Q01 实现侧）  
- [ ] 确认基座：Qwen2.5-3B-Instruct（或改选）  
- [ ] 确认本阶段不接真实写；Shadow/Fixture 优先  
- [ ] 确认模型永不写 `review_result`  
- [ ] 确认 NO_ACTION 正确性为一等训练目标  
- [ ] 确认 LIVE 数据入模须单独授权  
- [ ] 确认评估分 env 汇报，禁止伪造标定  
- [ ] 是否将本文纳入下一工程基线包  

---

## 13. 待决问题

| ID | 问题 | 建议（Draft） | 阻塞 |
|---|---|---|---|
| BRAIN-Q01 | 是否正式采用 Hybrid RE？ | 是（本文主张） | 实现开工前 |
| BRAIN-Q02 | 1.5B 还是 3B 作默认部署？ | 优先 3B；延迟/显存紧再 1.5B | B-M0 |
| BRAIN-Q03 | 是否需要多任务头（B-T6/T7）同一权重？ | 先单任务 RE；副责用独立 LoRA 适配器 | B-M3 后 |
| BRAIN-Q04 | RAG（KE 检索）是否一阶段就上？ | SFT-0 可先无 RAG；SFT-1 引入摘要检索 | 否 |
| BRAIN-Q05 | 教师模型是否允许调用外部 API？ | 优先本地/私有；若 API 须脱敏与授权记录 | 数据合成前 |
| BRAIN-Q06 | 与规则-only RE 如何 A/B？ | Shadow 双轨：rules vs brain vs hybrid | B-M5 |
| BRAIN-Q07 | 中文输出 vs 字段英文枚举？ | 字段/枚举英文契约；解释文本中文 | 否 |
| BRAIN-Q08 | 量化部署（INT4）是否影响 JSON 稳定性？ | 必须单独回归；不达标则 FP16/BF16 | B-M5 |
| BRAIN-Q09 | 持续学习是否覆盖写回权重或只外挂知识？ | 默认双轨：KE 走治理晋升；权重走周期微调 | B-M6 |
| BRAIN-Q10 | 评估是否纳入「人工投手基线」？ | 是，作为上界与对照 | B-M3 |

---

## 14. 理论与架构追踪

| 主张 | 锚点 | 本计划落点 |
|---|---|---|
| Prediction-driven Decision | GA-1 §6.2；RE-P1 | FE 摘要为一等输入；BLOCKED→NA |
| Business State Awareness | GA-1 §6.3；RE-P2 | 仅 Trusted Digest 入模 |
| 动态目标函数 | GA-1 §7.2–7.4；RE-P3 | objective_alignment 任务；不改 weights |
| 稳定性可战胜贪婪 | GA-1 §8.5；RE-P4 | NA 一等公民；偏好与指标加权 |
| 假设可反驳 | GA-1 §6.4；RE-P5 | rival_hypotheses 强制字段 |
| 响应窗口 | GA-1 §8.6；RE-P6 | V-05 + 训练样本 |
| 门禁先于智能 | 架构 §3–6；GIP v0.2 | Hybrid：模型不终审 |
| 失败即学习 | 架构 P6；LRRT | D6 持续学习含失败包 |
| 信任随表现成长 | 架构 P8/回路 D | 模型不改 Trust；仅影响候选半径 |
| Shadow/只读红线 | GA-DEC-004 | Stage-D 无写；source_env |

**明确不声称：** 本计划不证明 2B 模型已具备经营智能；一切能力表述以评估报告与 GA-3 为准。

---

## 15. 建议的下一步（仍属 GA-2，不启动 GA-3）

1. 负责人审阅本文，确认 Hybrid RE + 基座（建议形成 `GA-DEC-007`）。  
2. 产出 `Brain_Contract_Fixture_Pack`：五骨架各 ≥ 40 条可序列化 Request/Digest（FIXTURE）。  
3. 实现 `post_validator.py` 与契约回归测试（先于模型训练）。  
4. 启动 SFT-0（契约）并冻结评估脚本。  
5. 并行征集专家轨迹（每骨架双人各 50 条）。  
6. 完成 B-M2 后再决定是否投入 DPO 与 Shadow 联调排期。

---

## 16. 变更记录

| 日期 | 版本 | 变更 | 依据 |
|---|---|---|---|
| 2026-09-15 | v0.1 | 首次建立 2B 大脑模型训练微调计划：Hybrid RE 定位、基座选型、任务契约、四阶段数据与训练、评估、里程碑、风险与待决 | GA2-T33；Architecture v0.2；RE/DPK/GIP/Shadow/LRRT/Genome；GA-1 理论锚点 |

---

**Document Status:** Draft  
**Next Review:** 项目负责人 / Research Architect  
**Explicit Non-claim:** 本文为训练与微调工程计划草案；不包含已训练权重、不授权真实广告写操作或真实账户只读连接；全部超参、配比与门槛为 Proposed；模型输出不得绕过 Risk / Trust / Self-review / Adapter 任何门禁。
