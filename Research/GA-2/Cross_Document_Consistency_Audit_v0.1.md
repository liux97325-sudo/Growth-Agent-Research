# GA-2：跨文档接口一致性终审

**文档编号：** GA-2-XDCA-001  
**版本：** v0.1  
**状态：** Draft  
**阶段：** GA-2 Engineering Design（GA2-T27）  
**审计对象：** Research/GA-2/ 现行权威文档（双字段 / v0.2 为准）  
**输入基线：** `Research/GA-1/GA-1_Theory_v1.0.md`（Confirmed）  
**主线架构：** `Architecture_Overview_v0.2.md`（Confirmed，GA-DEC-004）  
**授权依据：** GA-2.0 Baseline（GA-DEC-005）§2「实现前建议做跨文档一致性终审（GA2-T27）」  
**作者角色：** Research Engineer 子代理  
**硬约束：** 不改 GA-1/PROJECT_SPEC；发现冲突只登记与建议，不擅自改主线。

---

## 0. 审计范围与方法

### 0.1 范围（15 份现行权威）

| # | 文档 | 版本 | 角色 |
|---|---|---|---|
| 1 | Architecture_Overview_v0.2.md | v0.2 Confirmed | 架构主线 |
| 2 | Decision_Packet_Schema_v0.1.md | v0.1 Draft | 成长最小原子 Schema |
| 3 | Forecast_Engine_Interface_v0.1.md | v0.1 Draft | 预测契约 |
| 4 | Reasoning_Engine_Interface_v0.1.md | v0.1 Draft | 推理契约 |
| 5 | Memory_Knowledge_Boundary_v0.1.md | v0.1 Draft | 记忆/知识边界 |
| 6 | Risk_Trust_SelfReview_v0.1.md | v0.1 Draft | 风控信任审批 |
| 7 | Gate_Integration_Playbook_v0.2.md | v0.2 Draft | 门禁联调（现行） |
| 8 | JD_Adapter_Interface_v0.2.md | v0.2 Draft | 京东接入（现行） |
| 9 | Shadow_Mode_Design_v0.1.md | v0.1 Draft | 影子运行 |
| 10 | Runtime_Envelope_Selfcheck_v0.1.md | v0.1 Draft | 运行时信封自检 |
| 11 | Learning_Reflection_Runtime_v0.1.md | v0.1 Draft | 回路 B 编排 |
| 12 | Shadow_Trial_Run_Plan_v0.1.md | v0.1 Draft | 试运行计划 |
| 13 | Parameter_Genome_Templates_v0.1.md | v0.1 Draft | 参数基因 |
| 14 | Threshold_Calibration_Method_v0.1.md | v0.1 Draft | 阈值标定方法 |
| 15 | GA-2.0_Baseline_Package.md | v0.1 Confirmed | 基线打包说明 |

**辅助对照（非现行权威，仅作证据）：** Fixture_Migration_Guide_v0.1.md、GA-2_Complete_Review_Package.md、Engineering_TODO.md。

**排除：** GA-1/、PROJECT_SPEC.md、v0.1 历史文档（Architecture_v0.1 / JD_v0.1 / Gate_v0.1）——仅在版本引用审计中作为「是否被误引为现行」的检查对象。

### 0.2 方法

1. **字段枚举抽取**：对 8 个审计维度做全库 grep + 关键节精读，抽取权威定义与各文档表述。  
2. **公式比对**：可执行判定公式逐字比对（符号、集合成员、附加条件）。  
3. **写权与职责表**：对照 GIP/JD/Risk/RE/基线的「写者」声明。  
4. **版本引用扫描**：搜索仍把 JD/Gate/Architecture v0.1 标为现行/强关联的位置。  
5. **冲突分级**：`冲突`（语义互斥或权威源落后于派生源）/ `警告`（可推导但未统一或引用过期）/ `通过`。

### 0.3 裁决原则（继承基线，不新增）

- 与 GA-1 冲突 → 改工程文档。  
- 与 Architecture_v0.2 + GA-DEC-004 冲突 → 以主线为准并修订详设。  
- 双字段语义以 Decision_Packet_Schema §2.2/§3 + Gate_Integration_Playbook_v0.2 §1.1 + JD_Adapter_Interface_v0.2 §3.4 为三角权威。  
- GA-2.0 Baseline §3.3 门禁不变量为冻结门槛。

---

## 1. 一致性矩阵

| 维度 | 权威定义源 | 一致性 | 结论摘要 |
|---|---|---|---|
| **1. lifecycle_status 枚举** | DPK §2.2；GIP v0.2 §1.1；JD v0.2 §2 D1 | **通过（附警告）** | 全库统一为 `Draft → Self-reviewed → Executed → Observed → Reflected → Archived / Superseded`。警告：Architecture_v0.2 §6 最小契约与 Risk_Trust 未引入该字段（见 C-02）。 |
| **2. review_result 枚举 + SRA 独占写** | DPK §2.2/§2.6；GIP C5/§2.3.5；JD v0.2 §10 | **通过（附冲突）** | 枚举 `APPROVE / NO_ACTION_APPROVE / REVISE / HOLD / REJECT / ESCALATE_HUMAN` 在 DPK/GIP/JD/Fixture/Shadow_Trial/基线一致；「仅 SRA 可写」在基线/GIP/RE/JD 一致。冲突：Risk_Trust 仍为单字段状态机且未写入 NO_ACTION_APPROVE（见 C-01）。 |
| **3. 可执行判定公式** | GIP v0.2 §1.1（最完整）；JD v0.2 G-01；基线 §3.3.1 | **通过（附警告）** | 核心双条件在 ≥6 处一致：`LS ∈ {Self-reviewed, Executed} ∧ RR ∈ {APPROVE, NO_ACTION_APPROVE}`。警告：GIP 额外含 `execution_mode ≠ SHADOW_READ_ONLY` 与 `risk.hard_block==[]`，基线公式更短（见 C-04）。 |
| **4. NO_ACTION 成包 vs SRA** | DPK-I2；GIP C3；RE §3.7/§6.3；Fixture §4.1 | **通过** | 「必须成包 + SRA 写 NO_ACTION_APPROVE + 合成回执 NOT_APPLICABLE_NO_ACTION + 跳过 Executed 进 Observed」四处一致。 |
| **5. env / source_env / trust_credit_allowed** | Shadow §3.4；Runtime_Envelope RE-I*；JD v0.2 §4.9；GIP §7 | **冲突** | 信封字段名与枚举集合未统一：`source` vs `source_env`；`REAL` vs `LIVE`；Fixture 校验集合缺 LIVE（见 C-03）。 |
| **6. forecast_ref 结构** | DPK §2.3；FE §5.1 | **通过** | `forecast_id / horizon / confidence / summary / based_on_validated_ids` 对齐；FE 明确为 superset 且 Packet 引用 FE summary；FR-I1..I5 与 DPK-I3 一致。 |
| **7. G-01–G-09 与 Risk/Trust/SRA 衔接** | JD v0.2 §3.4；GIP §3/§4；Shadow_Trial §3 | **通过（附警告）** | G-01 双字段、G-02 Trust 子对象、G-03 Risk hard_block、G-07 dry_run/Shadow 扩展在 JD/GIP/Fixture/Shadow_Trial/Runtime_Envelope 一致。警告：Runtime_Envelope 强关联仍写 Gate_v0.1（见 C-05）；Risk_Trust 未使用 G-* 编号（属上游层，可接受但缺交叉引用，见 C-06）。 |
| **8. 版本引用（是否仍引 v0.1 JD/Gate 为现行）** | GA-2.0 Baseline §2 | **警告** | 基线已明确 v0.1 仅历史承接；但 ≥6 份现行文档的「关联/强关联」头仍指向 JD_v0.1 或 Gate_v0.1 或 Architecture_v0.1（见 C-05/C-07）。 |

---

## 2. 冲突登记表

| ID | 严重度 | 位置 | 问题描述 | 建议裁决 |
|---|---|---|---|---|
| **C-01** | **高（必改）** | `Risk_Trust_SelfReview_v0.1.md` §2.4 控制原则、§6.5 状态机表、全文 | 仍以单字段审批状态（APPROVE/REVISE/HOLD/REJECT/ESCALATE_HUMAN）表述；**未纳入** `NO_ACTION_APPROVE`；**未声明** `review_result` 仅 SRA 可写（双字段语义）；关联架构仍写 `Architecture_Overview_v0.1.md`。与基线 §3.3.1–2、GIP C5、DPK §2.6 直接落后。 | **不改本文语义主体**；建议出 Risk_Trust_v0.2 补丁：(1) 状态机输出对齐 `review_result` 六元枚举；(2) 增写「review_result 仅 SRA 可写（HUMAN 经 SRA 映射）」；(3) 头部关联改为 Architecture_v0.2 + GIP_v0.2。在补丁落地前，实现以 GIP v0.2 §1.1 + JD v0.2 G-01 为准。 |
| **C-02** | **高（必改）** | `Architecture_Overview_v0.2.md` §6 决策包最小契约 | Confirmed 主线最小契约仅含 `review_result`，**无 `lifecycle_status`**；字段表亦无 `execution_mode` / `packet_kind`。双字段模型（DPK/JD/GIP）在架构确认之后引入，主线未回写。实现若以架构 §6 为唯一 Schema 将漏生命周期门禁。 | 建议走架构变更记录（不改 GA-DEC-004 四回路/CBA/Shadow 红线本体）：§6 增补 `lifecycle_status` + `execution_mode`（或明确「字段全集以 Decision_Packet_Schema_v0.1 为准，§6 仅为最小逻辑契约」）。**登记不擅改**；由负责人裁决是否升 Architecture_v0.2.1。 |
| **C-03** | **中高（必改）** | `JD_Adapter_Interface_v0.2.md` §4.9 `source_env`；`Gate_Integration_Playbook_v0.2.md` §7；`Fixture_Migration_Guide_v0.1.md` §4.1 序号 5；`Shadow_Mode_Design_v0.1.md` §5 | 回执来源字段名与枚举不一致：JD 用 `audit.source_env ∈ {FIXTURE, SIMULATION, SHADOW, LIVE}`；GIP 用 `source ∈ {REAL, SIMULATION, FIXTURE, HUMAN}`（或 source_env 含 SHADOW）；Fixture 校验写 `source_env ∈ {FIXTURE, SHADOW, SIMULATION}`（无 LIVE）；Shadow/Runtime 用 envelope `env` + `trust_credit_allowed`。`REAL` vs `LIVE` 同义异名，实现时易漏过滤。 | **建议裁决：** 统一权威字段名为 `audit.source_env`；枚举冻结为 `{LIVE, SHADOW, SIMULATION, FIXTURE, HUMAN}`（吸收 GIP 的 HUMAN，废止 REAL 别名）；GIP §7 与 Fixture §4.1 同步改写。信封侧 `env` 与回执侧 `source_env` 保持同值透传（Runtime_Envelope RE-I6 已要求）。 |
| **C-04** | **中（警告）** | `Decision_Packet_Schema_v0.1.md` DPK-I1 vs `Gate_Integration_Playbook_v0.2.md` §1.1 vs `GA-2.0_Baseline_Package.md` §3.3.1 | 可执行公式三处核心双条件一致，但完整度不同：GIP 含 Shadow 硬拒绝 + hard_block 空；基线只有双条件；DPK-I1 写「状态 ≥ Self-reviewed 且 review_result=APPROVE」（针对非 NO_ACTION 写动作，可接受，但未点名字段 `lifecycle_status`，且与 GIP 的 `∈ {Self-reviewed, Executed}` 集合写法不完全同构）。 | **建议：** 冻结实现时以 **GIP v0.2 §1.1 四条件** 为唯一完整公式；DPK-I1 保持「非 NO_ACTION 写动作」语境但在变更记录中补一句「字段名与集合以 GIP §1.1 为准」。基线 §3.3.1 可保持短式（不变量层）。不阻塞实现。 |
| **C-05** | **中（警告）** | `Runtime_Envelope_Selfcheck_v0.1.md` 头部强关联；`JD_Adapter_Interface_v0.2.md` 头部关联详设；`Shadow_Mode_Design_v0.1.md` 头部强关联；`Decision_Packet_Schema_v0.1.md` 头部关联详设；`Forecast_Engine_Interface_v0.1.md` 输入清单；`Architecture_Overview_v0.2.md` §9 索引；`Risk_Trust_SelfReview_v0.1.md` 头部 | 多份现行文档仍将 `JD_Adapter_Interface_v0.1.md` 和/或 `Gate_Integration_Playbook_v0.1.md` 列为「强关联/关联详设/组件索引」，未标注「已被 v0.2 承接」。基线 §2 已声明 v0.1 仅历史承接，文档头未同步。 | **建议：** 实现前批量做「引用卫生」：凡现行文档头部/索引中的 JD_v0.1、Gate_v0.1、Architecture_v0.1 改为 v0.2，或加「（历史，已被 v0.2 承接）」后缀。属文档同步，**不改语义**。 |
| **C-06** | **低（可延后）** | `Risk_Trust_SelfReview_v0.1.md` 与 JD/GIP 门禁编号 | Risk/Trust/SRA 详设未使用 G-01–G-09 编号，也未显式映射「Risk hard_block → G-03」「Trust Level → G-02」。GIP §4 组合裁决表已从 Adapter 侧完成衔接，属单向覆盖。 | 可延后至 Risk_Trust_v0.2：增加「上游谓词 ↔ G-* 门禁」对照小节，降低联调时的双套编号漂移（Runtime_Envelope RE-Q8 已提出同类问题）。 |
| **C-07** | **低（警告）** | `GA-2_Preliminary_Answer_2026-09-11.md`、`Engineering_TODO.md` | 历史文档/TODO 表仍把 JD_v0.1、Gate_v0.1 标为产出物且未全部加「被 v0.2 承接」。基线已覆盖声明，风险低。 | 可延后：TODO 表补承接状态即可；Preliminary Answer 属快照文档，建议只读保留。 |
| **C-08** | **低（可延后）** | `Learning_Reflection_Runtime_v0.1.md` §相关；`Memory_Knowledge_Boundary_v0.1.md` | 学习/记忆侧对 `review_result` 的消费（如 failure 触发条件含 REJECT/ESCALATE）依赖双字段包，但 Memory 文档仍关联 JD_v0.1。与 C-05 同源。 | 随 C-05 引用卫生一并处理；语义本身与 DPK-I6/NO_ACTION 成包不冲突。 |

**冲突数量：** 高 2（C-01、C-02）+ 中高 1（C-03）+ 中 2（C-04、C-05）+ 低 3（C-06–C-08）= **8**。

---

## 3. 必改清单 vs 可延后清单

### 3.1 必改（实现前冻结门槛；不改则不得宣称「双字段门禁可实现」）

| 项 | 对应冲突 | 动作 | 建议责任文档 |
|---|---|---|---|
| M1 | C-01 | Risk_Trust 补丁或 v0.2：`review_result` 六元枚举 + 仅 SRA 可写 + 关联改 v0.2 主线 | Risk_Trust_SelfReview |
| M2 | C-02 | Architecture §6 与双字段对齐，或显式声明「字段全集以 DPK Schema 为准」 | Architecture_Overview（负责人裁决是否升版） |
| M3 | C-03 | 统一 `source_env` 字段名与枚举（含 REAL→LIVE、补 HUMAN），同步 GIP §7 与 Fixture 校验 | JD_v0.2 + GIP_v0.2 + Fixture |
| M4 | C-05 | 现行文档头/索引中 v0.1 引用改 v0.2 或标「历史」 | 多文档批量（纯引用卫生） |

### 3.2 可延后（不阻塞实现骨架，但应进 Engineering_TODO）

| 项 | 对应冲突 | 动作 |
|---|---|---|
| D1 | C-04 | DPK-I1 补一句指向 GIP §1.1 完整公式 |
| D2 | C-06 | Risk_Trust 增加上游谓词 ↔ G-* 对照 |
| D3 | C-07 | Engineering_TODO 承接状态补全 |
| D4 | C-08 | Memory/Learning 引用卫生随 M4 |
| D5 | — | GIP-Q9（Executed 包重试幂等）保持 Proposed，实现时按 G-05 落地 |

---

## 4. 分维度证据摘要（审计轨迹）

### 4.1 lifecycle_status

| 文档 | 表述 | 判定 |
|---|---|---|
| DPK §0.1/§2.2 | Draft→Self-reviewed→Executed→Observed→Reflected→Archived/Superseded | 权威 |
| GIP v0.2 §1.1 概念表 | 同上 | 一致 |
| JD v0.2 D1 / §10 映射 | 同上 | 一致 |
| Fixture §1 | 同上 | 一致 |
| Shadow_Trial G-01 行 | 同上 | 一致 |
| Architecture_v0.2 §6 | **无此字段** | C-02 |
| Risk_Trust | **无此字段**（单状态机） | C-01 |

### 4.2 review_result 与 SRA

枚举六值在 DPK/GIP/JD/Fixture/Shadow_Trial/基线/RE（边界声明）一致。  
SRA 独占写：基线 §3.3.2；GIP C5 + §2.3.5 + §8.3；RE §5.4/§7；JD §1.5。  
Risk_Trust §6.5 仅有五值状态机且无 NO_ACTION_APPROVE → C-01。

### 4.3 可执行公式出现点（≥3 处）

1. GIP v0.2 §1.1（四条件完整式）  
2. JD v0.2 §3.4 G-01 + 伪逻辑  
3. GA-2.0 Baseline §3.3.1（短式）  
4. Shadow_Trial §3 契约表  
5. Fixture §4.1 校验清单 + 伪逻辑  
6. Runtime_Envelope §6.1（引用 JD v0.2，不弱化）

核心双条件一致 → 维度 3 通过；完整式差异见 C-04。

### 4.4 NO_ACTION

DPK-I2（跳过 Executed→Observed→Reflected）+ GIP C3 + RE §3.7/§6.3 + Fixture NO_ACTION 样例 B + 基线 §3.3.4 → **通过**。

### 4.5 信封贯通

| 字段 | 定义处 | 消费处 | 问题 |
|---|---|---|---|
| envelope.env | Shadow §3；Runtime_Envelope | ME/Trust/TE 过滤 | 一致 |
| envelope.trust_credit_allowed | Shadow §3.4；Runtime RE-I2 | Trust 更新拒绝 false | 一致 |
| envelope.execution_mode | DPK-I5；JD；Runtime RE-I3/I8 | G-01 写硬拒 | 一致 |
| receipt.audit.source_env | JD v0.2 | Fixture；Memory 过滤 | **枚举/别名冲突 C-03** |
| source（GIP） | GIP §7 | Memory/Trust/Reflection 入口 | **与 source_env 异名 C-03** |

### 4.6 forecast_ref

DPK §2.3 五子字段；FE §5.1 对齐声明 + FR-I1..I5；JD 仅声明 object；Architecture 一行摘要 → **通过**。

### 4.7 G-01–G-09

JD v0.2 为权威表；GIP 组合裁决表 + 动作类型矩阵与之对齐；Shadow_Trial SC-C2/C3/B5 与 Runtime_Envelope SC-* 对 G-01/G-07 一致；Fixture 映射 G-02/G-03 字段改读 risk.*/trust.* → **通过**（引用卫生见 C-05）。

### 4.8 版本引用

基线明确：Architecture/JD/Gate v0.1 = 历史承接。  
仍指向 v0.1 为现行/强关联的现行文档：Decision_Packet_Schema（JD_v0.1）、Architecture_v0.2 §9（JD_v0.1）、Risk_Trust（Arch_v0.1）、Shadow_Mode（JD_v0.1）、Runtime_Envelope（Gate_v0.1）、JD_v0.2 头（Gate_v0.1）、Forecast_Engine（JD_v0.1）→ C-05。

---

## 5. 结论：是否具备实现前冻结条件

| 判定项 | 状态 |
|---|---|
| 双字段核心语义（枚举 + SRA 独占 + 可执行双条件 + NO_ACTION 成包） | **已收敛**，三角权威（DPK / GIP_v0.2 / JD_v0.2）+ 基线不变量一致 |
| 主线 Architecture 与双字段 | **未回写**（C-02） |
| Risk_Trust 与双字段/NO_ACTION_APPROVE | **未承接**（C-01） |
| 信封/回执来源枚举 | **未统一**（C-03） |
| 引用卫生 | **未清理**（C-05） |

**综合结论：**

> **有条件冻结（Conditional Freeze）。**  
> 实现骨架（Packet Schema、Adapter G-01–G-09、SRA 谓词、Shadow 只读红线）**可以按 GIP v0.2 §1.1 + JD v0.2 + DPK 双字段启动**，前提是：  
> 1. 实现以 GIP_v0.2 / JD_v0.2 / DPK 为唯一门禁语义源，**不得**回读 Risk_Trust 或 Architecture §6 的旧单字段表述；  
> 2. 必改项 M1–M4 在**编码冻结（code freeze）前**关闭；  
> 3. M2（Architecture 对齐）由负责人单独裁决——若不升架构版本，必须在实现规范中书面声明「§6 为逻辑最小契约，字段全集以 DPK Schema 为准」。  
> **在 M1–M4 关闭前，不得宣称「GA-2 跨文档接口已全量一致」或启动真实写路径相关实现。**

---

## 6. 建议的后续动作（供负责人）

| 优先级 | 动作 | 建议任务号 |
|---|---|---|
| P0 | 关闭 C-03（source_env 统一）——直接阻塞 Memory/Trust 防污染过滤实现 | 新任务或并入 GA2-T20/T21 |
| P0 | 关闭 C-01（Risk_Trust 双字段补丁） | GA2-T05 升 v0.2 |
| P1 | 裁决 C-02（Architecture §6） | 负责人 / GA-DEC |
| P1 | 关闭 C-05（引用卫生批量） | GA2-T27 收尾 |
| P2 | D1–D5 可延后项进 Engineering_TODO | 文档维护 |

---

## 7. 变更记录

| 日期 | 版本 | 变更 | 依据 |
|---|---|---|---|
| 2026-09-14 | v0.1 | 首次跨文档接口一致性终审：8 维度矩阵、8 条冲突登记、必改/可延后清单、有条件冻结结论 | GA2-T27；GA-2.0 Baseline GA-DEC-005；GIP_v0.2；JD_v0.2；DPK_v0.1 |

---

**Document Status:** Draft（正文保持审计原貌）  
**关闭附录：** 见文末 §8  
**Owner Action:** 审阅冲突登记 C-01–C-08，裁决 M1–M4 关闭方式；决定是否将本审计结论写入 GA-2.0 基线补充说明  
**Explicit Non-claim:** 本文不修改 GA-1/PROJECT_SPEC，不修改任何现行权威文档正文；所有冲突仅登记与建议，最终以负责人/新 GA-DEC 裁决为准。

---

## 8. 关闭附录（2026-09-14，GA-DEC-006 与后续收尾）

> 本附录**不改写** §1–§7 审计正文；仅登记冲突处理结果，供实现引用。

| 冲突 | 状态 | 处理 |
|---|---|---|
| C-01 | **Closed** | Risk_Trust v0.1.1：review_result 六元含 NO_ACTION_APPROVE；SRA 独占写；关联 v0.2 |
| C-02 | **Closed** | Architecture §6 回写 lifecycle_status + review_result；字段全集以 DPK 为准 |
| C-03 | **Closed** | canonical source_env={LIVE,SHADOW,SIMULATION,FIXTURE,HUMAN}；REAL→LIVE；GIP/Fixture 已归一 |
| C-04 | **Closed** | DPK-I1 指向 GIP §1.1 完整公式 |
| C-05 | **Closed** | 引用卫生批量完成（现行头/索引改 v0.2 或标历史） |
| C-06 | **Closed** | Risk_Trust §10.1 谓词↔G-* 对照表 |
| C-07 | **Closed** | Engineering_TODO 已标承接；Preliminary Answer 作历史快照 |
| C-08 | **Closed** | Memory/参数基因等 Architecture 引用已升 v0.2 |

**实现冻结门槛：** M1–M4 已关闭；在关闭剩余完备性 P0（错误码目录、Skeleton 端口等）后，可按 Module Skeleton 开工 Fixture/影子骨架，仍禁止真实写。

**完备性审计关联：** `GA-2_Completeness_Audit_v0.1.md`；G-03 错误码目录见 `Error_Reason_Code_Catalog_v0.1.md`。
