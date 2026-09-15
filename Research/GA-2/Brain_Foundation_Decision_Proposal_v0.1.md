# GA-2：Brain 基座确认建议书（GA2-T33c）

**文档编号：** GA-2-BRAIN-DEC-001  
**任务编号：** GA2-T33c  
**版本：** v0.1  
**状态：** Draft（**非最终 GA-DEC**）  
**阶段：** GA-2 Engineering Design / 实现前置决策建议  
**上游输入：**  
- `Brain_Model_Training_Finetune_Plan_v0.1.md`（GA2-T33，Draft）  
- `Reasoning_Engine_Interface_v0.1.md`（GA2-T23，Draft；RE-Q01 故意不锁内核形态）  
**强关联：** Architecture v0.2；DPK Schema；GIP v0.2；Shadow / Fixture 红线  
**作者角色：** Research Engineer 子代理  
**约束：** 仅形成**建议书**；**不**写入 `Meeting/Decision_Log.md`；**不**声称已批准；不改 GA-1 / PROJECT_SPEC；无真实训练、无真实连接、无权重发布。

---

## 0. 范围与批准状态声明

### 0.1 一句话

> 本文回答 Engineering_TODO **GA2-T33c**：「是否采用 Hybrid RE + 哪个 2B 级基座」，供负责人裁决。  
> **当前状态：建议就绪，未批准。** 任何「已锁定 Hybrid / 已选定 Qwen」的表述在新 `GA-DEC-NNN` 出现前均不成立。

### 0.2 本轮要做

1. 对照 Brain Plan 与 RE Interface，给出 RE 内核形态与基座的选项对比。  
2. 给出明确推荐（Draft）：**Hybrid RE + Qwen2.5-3B-Instruct（紧凑路径 1.5B）**。  
3. 列出风险与缓解。  
4. 列出**必须由负责人 GA-DEC 裁决**的事项清单。  
5. 提供可直接粘贴进 Decision Log 的**建议决议草稿**（仍待签发）。

### 0.3 本轮明确不做

| 项 | 说明 |
|---|---|
| 最终 GA-DEC | 不修改 Decision_Log；不将本文升格为 Accepted |
| 训练 / 下载权重 / 启动 SFT | 无训练代码与算力执行 |
| 真实京东/抖音只读或写连接 | 遵守 GA-DEC-004/005 红线 |
| 替代 SRA / Risk / Trust / Adapter | 门禁不变量不可协商 |
| 启动 GA-3 | 仅预留评估钩子 |

### 0.4 RE-Q01 关系（接口侧故意开放）

`Reasoning_Engine_Interface_v0.1.md` §9：

> RE-Q01：内核形态（规则引擎 / LLM / 混合）是否本文锁定？  
> **不锁定**；接口契约优先；实现选型后置。

Brain Plan §0.4 / BRAIN-Q01 主张：采用 **Hybrid RE**。  
**本文立场：** 支持该主张作为推荐项，但 **RE-Q01 的正式关闭须负责人 GA-DEC**；接口文档可继续写「不锁定，除非新决策覆盖」。

---

## 1. 决策问题拆解

| 子问题 | 内容 | 关联待决 |
|---|---|---|
| Q-A | RE 内核形态：规则 / 纯 LLM / **Hybrid** | BRAIN-Q01；RE-Q01 |
| Q-B | 部署基座：1.5B / **3B** / 其他开源 | BRAIN-Q02 |
| Q-C | 训练方式：LoRA 主路径是否锁定 | Plan §3.2 |
| Q-D | 本阶段范围：Fixture+Validator 先行，训练后置 | Plan §10 B-M0…B-M2 |
| Q-E | 数据与授权红线：LIVE 数据入模须新决策 | Plan §6.6 / 检查清单 |

Q-A/Q-B 为本建议书核心；Q-C/Q-D/Q-E 作为配套确认项。

---

## 2. 选项对比

### 2.1 RE 内核形态（Q-A）

| 维度 | 规则-only | 纯 LLM 大脑 | **Hybrid RE（推荐）** |
|---|---|---|---|
| Schema / 枚举稳定 | 高 | 低–中（幻觉/漂移） | **高**（Post-Validator 强制） |
| 门禁「先于智能」 | 易满足 | 难保证（易越权写 review 语义） | **满足**：模型只出 Draft；SRA 终审 |
| 观察解读 / 假设鉴别 | 弱，规则爆炸 | 强 | **中–强**（模型负责） |
| NO_ACTION 可训练性 | 手工规则 | 可学但易偏「永动」或「永不动」 | **可监督 + 硬过滤** |
| 可解释 / 审计 | 规则可追溯 | 难 | **对齐说明 + 谓词 trace** |
| FE BLOCKED / 低置信降级 | 易 | 难伪精确 | **Pre/Post 层硬降级 NA** |
| 冷启动成本 | 低 | 高（数据+对齐） | 中（先 Validator+Fixture） |
| 与架构主张一致 | 部分 | **弱**（违门禁先于智能） | **强**（Plan §1.1） |
| Shadow 可行性 | 易 | 中 | **易（双轨 rules vs hybrid）** |

**倾向：** Hybrid。纯 LLM 与 GA-2 门禁红线冲突风险最大；规则-only 难覆盖五场景假设质量，不利于后续经验蒸馏。

### 2.2 部署基座（Q-B，约 1.5–3B）

| 优先级 | 基座 | 优势 | 风险 | 适用 |
|---|---|---|---|---|
| **P0 推荐** | **Qwen2.5-3B-Instruct** | 中文经营语境强；JSON/指令好；LoRA 生态成熟；许可友好 | 复杂假设鉴别仍有限（靠 Hybrid 兜底） | 默认部署 |
| P0 紧凑 | Qwen2.5-1.5B-Instruct | 显存/延迟更松；端侧友好 | 长上下文与鉴别上限更低 | 延迟/显存紧时 |
| P0 备选 | Qwen3-1.7B / 4B（若栈就绪） | 推理/结构化更新 | 版本迭代快，须锁 revision | 训练栈就绪后 |
| P1 | MiniCPM / InternLM2.5-1.8B 级 | 中文与工具调用可 | 工具链碎片化 | 备选 |
| P2 | Llama-3.2-1B/3B-Instruct | 国际生态 | 中文经营语境弱 | 不推荐首选 |
| 教师（不部署） | Qwen2.5-7B/14B-Instruct | 合成高质量轨迹 | 成本；须防偏见 | 仅离线合成 |

### 2.3 组合推荐矩阵（摘要）

| 组合 | 评价 |
|---|---|
| 规则-only | 可作 Shadow 对照基线，**不建议**作为唯一生产内核 |
| 纯 LLM 3B | **不建议**：门禁与 Schema 风险不可接受 |
| **Hybrid + 3B** | **主推荐** |
| Hybrid + 1.5B | 紧凑备选；须更严 Validator 与更保守动作半径 |
| Hybrid + 外部大 API 生产推理 | **不建议**：数据出域与延迟/审计风险 |

---

## 3. 推荐方案（Draft，待 GA-DEC）

### 3.1 推荐决议（内容建议）

1. **正式采用 Hybrid Reasoning Engine**：  
   - 确定性层：Pre-Assembler、场景骨架白名单、Post-Validator、熔断、强制 `NO_ACTION` 回退；  
   - 模型层：场景路由建议、observation→cause_claim、PRIMARY/ALT/NA/HOLD 候选、expected_effect、objective_alignment 说明；  
   - **模型提案，系统拍板**；模型类型上不得携带/写入 `review_result`。  
2. **默认部署基座：`Qwen2.5-3B-Instruct`**（锁 revision）；资源受限时回退 **`Qwen2.5-1.5B-Instruct`**。  
3. **教师模型：** `Qwen2.5-7B-Instruct`（或 14B）仅离线合成/偏好辅助，不进生产链路。  
4. **训练方式：** LoRA（主）；全参 SFT 仅 1.5B 且数据充足时可选。  
5. **本阶段范围：** 先 B-M1 契约 Fixture + Post-Validator；**不**因本决议自动授权 GPU 训练排期或 LIVE 数据入模。  
6. **对照基线：** Shadow 双轨保留 rules-only vs hybrid（BRAIN-Q06）。  
7. **关闭关系（建议）：**  
   - BRAIN-Q01 → Closed（采纳 Hybrid）；  
   - BRAIN-Q02 → Closed（默认 3B / 回退 1.5B）；  
   - RE-Q01 → 由新 GA-DEC **覆盖**为「实现侧锁定 Hybrid」（接口文档可加注记，不改 I/O 契约）。

### 3.2 不变量重申（写入任何批准文本时必须保留）

| ID | 不变式 |
|---|---|
| BF-I1 | 无有效 Forecast / `validation_confidence=LOW` → 模型不得产出非 NO_ACTION 写动作 |
| BF-I2 | 模型输出不得绕过 Risk / Trust / SRA / Adapter |
| BF-I3 | 非法输出且不可修 → 强制 `NO_ACTION` + `degrade_reasons`，禁止静默丢包 |
| BF-I4 | `source_env≠LIVE` 样本不得自动晋升企业规则或计入 live Trust |
| BF-I5 | LIVE 数据入模、真实连接、LIVE 写路径 **一律另案授权** |
| BF-I6 | 全部超参 / 门槛 / 延迟预算保持 **Proposed**，待 TCAL / GA-3 |

### 3.3 与里程碑的衔接（不构成开工令）

| 里程碑 | 依赖本决议？ | 备注 |
|---|---|---|
| B-M0 计划确认 | **是**（本文目标） | 负责人签发 GA-DEC 后关闭 |
| B-M1 Fixture + Validator | 形态确认后可并行准备 | **不依赖真实连接** |
| B-M2 SFT-0 | 需算力与数据授权 | 本决议不自动授予 |
| B-M5 Shadow 联调 | 需 B-M4 + T26 环境 | 无写 |

---

## 4. 风险与缓解

| ID | 风险 | 影响 | 缓解（建议写入决议） |
|---|---|---|---|
| BF-R1 | **过早锁基座**导致训练栈/许可证/revision 漂移 | 不可复现、返工 | 锁 `model_id+revision`；替换须新决策但**保持 RE I/O 契约** |
| BF-R2 | **把 Hybrid 当已批准**提前开工训练 | 治理违规、无效投入 | 本文状态强制 Draft；B-M1 仅契约/Fixture；训练前再检授权 |
| BF-R3 | **2B 容量不足**假设鉴别弱 | 误动作或过度 NA | Hybrid Validator；Knowledge 检索；难例 HOLD/NA；under_action 门槛 |
| BF-R4 | 训练成「永远 NO_ACTION」或「刷存在感」 | 失去决策价值 / 破坏稳定 | DPO 平衡；over/under_action 双指标；SRA REJECT 偏好 |
| BF-R5 | JSON 幻觉 / 枚举漂移 | 链路崩溃 | 强制 NA 回退；熔断（Proposed N=5）；guided decoding |
| BF-R6 | LIVE 数据泄漏入模 | 治理违规 | source_env 强制；入模审查；BF-I4/I5 |
| BF-R7 | 负责人只批「用小模型」未批门禁边界 | 越权风险 | 决议必须捆绑 BF-I1…I6 与「模型不写 review_result」 |

---

## 5. 待负责人 GA-DEC 裁决项（Checklist）

> 以下每项须负责人明确 **接受 / 修改 / 否决**；子代理与研究工程师**无权代签**。

| # | 裁决项 | 建议 | 对应待决 |
|---|---|---|---|
| 1 | 是否采用 **Hybrid RE**？ | **是** | BRAIN-Q01 / RE-Q01 |
| 2 | 默认部署基座？ | **Qwen2.5-3B-Instruct**；回退 1.5B | BRAIN-Q02 |
| 3 | 教师模型是否仅离线？ | **是**（7B/14B，不进生产） | BRAIN-Q05 |
| 4 | 本阶段是否授权真实训练启动？ | **否**（先 Fixture+Validator；训练另案） | Plan B-M1/B-M2 |
| 5 | 是否确认 Shadow/Fixture 优先、无写？ | **是** | GA-DEC-004/005 延续 |
| 6 | 模型是否永不写 `review_result`？ | **是**（类型与 Validator 双保险） | 检查清单 §12 |
| 7 | NO_ACTION 正确性是否一等训练目标？ | **是** | 同上 |
| 8 | LIVE 数据入模是否须单独授权？ | **是** | BF-I5 |
| 9 | 评估是否分 env 汇报、禁止伪造标定？ | **是** | 同上 |
| 10 | 是否将 Brain Plan + 本文纳入下一工程基线包标签？ | 建议 **纳入 Draft 扩展包**，仍标 Proposed | GA-2.0 基线治理 |
| 11 | 是否采纳 rules vs hybrid Shadow 双轨？ | **是**（B-M5） | BRAIN-Q06 |
| 12 | 中文解释 + 英文枚举契约？ | **是** | BRAIN-Q07 |

---

## 6. 建议的 Decision Log 草稿（**未签发，勿当作已 Accepted**）

> 编号建议 `GA-DEC-007`（以 Decision Log 下一空号为准；签发时由负责人最终定号）。  
> **在负责人于 `Meeting/Decision_Log.md` 正式写入并标 Accepted 前，本节无效。**

```text
GA-DEC-007（草案）：确认 Brain Hybrid RE 与默认基座（实现前置）

- 日期：待签发
- 状态：Draft（本文件）
- 决策者：Project Owner
- 背景：
  1. GA2-T33 产出 Brain_Model_Training_Finetune_Plan_v0.1.md，主张 Hybrid RE + 2B 基座。
  2. GA2-T23 RE 接口 RE-Q01 故意不锁内核形态。
  3. GA2-T33c 要求形成负责人可签发的确认建议。
- 决定（待负责人勾选）：
  1. 采纳 Hybrid RE；模型提案、系统拍板；模型不写 review_result。
  2. 默认基座 Qwen2.5-3B-Instruct（锁 revision）；紧凑回退 1.5B。
  3. 教师 7B/14B 仅离线；生产不依赖教师。
  4. 本决策不授权真实写、真实只读连接、LIVE 数据入模或自动开工训练。
  5. 下一步优先 B-M1 契约 Fixture + Post-Validator；训练排期另报。
  6. 关闭 BRAIN-Q01/02；RE-Q01 实现侧由本决策覆盖（接口 I/O 契约不变）。
- 禁止：修改 GA-1；启动 GA-3；把 Proposed 门槛当真值。
```

---

## 7. 输入文档要点摘录（便于负责人快速审）

### 7.1 Brain Plan 关键主张

- 2B 是 RE **认知内核**，不是整机 Growth Agent（Plan §0.1）。  
- Hybrid 运行时：Pre-Assembler → 2B Kernel → Post-Validator → CBA/DPK（§1.2）。  
- 模型永不：写 review_result、超幅度、FE BLOCKED 时写动作、伪造 knowledge、Raw 入 observation、绕过 Adapter、env≠LIVE 声称已验证（§2.3）。  
- 默认锁定建议：Qwen2.5-3B（或 1.5B）+ LoRA + 教师 7B/14B（§3.2）。  
- 里程碑 B-M0 即「本文审阅；确认 Hybrid + 基座」（§10）。  
- 明确不声称已具备经营智能（§14）。

### 7.2 RE Interface 约束

- RE 只消费 Trusted State / ForecastBundle / Objective Snapshot / Knowledge / Risk-Trust 预览。  
- RE-P1…P10：预测先于动作、只信校验、NO_ACTION 一等公民、门禁不越权等。  
- FE BLOCKED → 仅 NO_ACTION（§2.3）。  
- RE-Q01 **不锁定**内核——与本文「建议锁定但须 GA-DEC」衔接。

---

## 8. 变更记录

| 日期 | 版本 | 变更 | 依据 |
|---|---|---|---|
| 2026-09-15 | v0.1 | 首次建立 Brain 基座确认建议书：选项对比、Hybrid+3B 推荐、风险、GA-DEC 裁决清单与未签发决议草稿 | GA2-T33c；Brain Plan v0.1；RE Interface v0.1；Architecture v0.2；GA-DEC-004/005 |

---

**Document Status:** Draft  
**Next Review:** 项目负责人（GA-DEC 签发）  
**Explicit Non-claim:** **非最终 GA-DEC**；不表示 Hybrid RE 或任何基座已获批准；无真实训练或平台连接；全部数值与门槛为 Proposed。
