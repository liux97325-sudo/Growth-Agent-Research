# GARP 初步答卷：Growth Agent 研究理解与 GA-2 首轮工程研究综述

**文档编号：** GA-2-ANSWER-001  
**日期：** 2026-09-11  
**版本：** v0.1  
**状态：** Draft（供项目负责人评审）  
**作者角色：** MiMo Desktop，Local Research Operations Assistant / 研究执行助手  
**输入基线：** `GA-1_Theory_v1.0.md`（GA-1.0，Confirmed）  
**授权依据：** `GA-DEC-003` + 项目负责人“完全授权开展研究”  
**边界声明：** 本文是工程与研究综合答卷，不是新理论版本；不修改 GA-1；不接入真实广告账户。

---

## 0. 这份答卷回答什么

在完整理解 GARP 后，本答卷给出：

1. **我对项目本质的判断**（不是广告工具，而是什么）；  
2. **GA-2 应该怎么设计**（总体架构与关键机制）；  
3. **首轮工程研究成果**（架构 v0.2 + 四类组件详设）；  
4. **我认为最容易做错的点**；  
5. **建议的下一步路径**。

---

## 1. 我对项目的理解：真正的命题

### 1.1 一句话

企业级 AI 的价值锚点，应从“部署日能力”切换到“部署后成长速度与知识复利”。

### 1.2 项目真正要造的不是什么

- 不是京准通脚本；  
- 不是 LLM+Tool+Workflow 的另一种编排；  
- 不是“AI 在电商中的应用综述”；  
- 不是单次 ROI 优化器。

### 1.3 项目真正要造的是什么

一套能在真实经营里完成：

```text
感知 → 预测 → 决策 → 执行 → 反馈 → 蒸馏 → 知识演化 → 权限生长
```

并把个人运营经验沉淀为企业数字资产的 **Growth Operating System**。

京东广告与抖音运营是**第一验证场**，不是理论天花板。

### 1.4 最小充分判断

| 若缺少… | 系统退化为… |
|---|---|
| 数据真实性校验 | 被平台指标牵着走的自动化 |
| 预测驱动 | 事后救火机器人 |
| 经验蒸馏/知识演化 | 有日志无成长的 Workflow |
| 风险与信任门禁 | 企业不敢用的玩具 |
| 动态目标函数 | 错配 KPI 的优化器 |

---

## 2. GA-2 研究立场

1. **理论单向派生**：一切工程文档可追到 GA-1。  
2. **先闭环，后精巧**：优先打通 Decision Packet 与四回路，而不是先选框架/模型。  
3. **门禁优先于智能**：不能审计、不能风控的动作，再聪明也不上线。  
4. **场景可插拔**：JD/Douyin 做 Domain Agent，核心能力留在 Growth OS Core。  
5. **Draft 诚实标注**：默认参数、公式、状态机均为 Proposed，不冒充已验证结论。

---

## 3. 总体答卷：Growth Agent 架构主张

完整版见 `Research/GA-2/Architecture_Overview_v0.2.md`。

### 3.1 分层

- **L0 企业目标层**：经营目标、预算、风险偏好  
- **L1 Chief Business Agent**：最高协调者  
- **L2 能力引擎层**：Forecast / Reasoning / Memory / Learning / Knowledge / Reflection / Risk / Trust / Self-review + 目标函数生成  
- **L3 领域执行层**：京东广告 Agent、抖音运营 Agent  
- **L4 接入校验层**：Adapter + Validation + State Assembler  
- **L5 数字资产层**：Audit → Episode → Experience → Rule → Strategy → Genome → Capability  

### 3.2 四条主回路（系统发动机）

1. **经营决策回路**：State→Forecast→Reasoning→门禁→执行  
2. **经验蒸馏回路**：Audit→Causal Memory→Reflection→Experience  
3. **知识演化回路**：Experience→Rule→Strategy→Genome→Capability→反哺决策  
4. **信任自治回路**：表现→Trust Score→权限升级→更大动作半径  

> 只做回路 1 = 高级 Workflow。GARP 必须至少闭环 2+3，并随成熟度启动 4。

### 3.3 决策包（Decision Packet）是成长的“最小原子”

没有可审计的决策包，经验蒸馏与信任评分都无从附着。  
字段包括：目标函数快照、状态摘要、预测引用、假设、动作、风险、信任、审批、结果、反思引用。

---

## 4. 首轮组件详设摘要

> 下列四份为并行详设文档（Draft），本节为综合摘要；细节以各文档为准。

### 4.1 Memory / Knowledge / Reflection / Learning 边界

**核心判断：**

- **Memory** 存“发生了什么、当时为什么这么判断”（因果事件）；  
- **Reflection** 负责“复盘触发与结论”；  
- **Learning** 负责“从复盘与跨计划对比提炼候选经验”；  
- **Knowledge** 负责“结晶为规则/策略/基因/能力并治理复用”。

**最容易犯的错：** 把向量库直接当 Knowledge Engine，导致噪声经验污染策略。

### 4.2 Risk / Trust / Self-review

**核心判断：**

- Risk 给风险等级与限额；  
- Trust 给能力半径（Level 0–5）；  
- Self-review 给终审状态机（APPROVE/REVISE/HOLD/REJECT/ESCALATE_HUMAN）。  

**门禁顺序：** Reasoning → Risk → Trust Capability → Self-review → Execute。  
**升权逻辑：** 无稳定达成率与风控表现，不升权。

### 4.3 京东接入层（仅抽象契约）

**核心判断：**

- Adapter 与 Core 隔离；  
- 先只读（指标/计划/库存/预算），后写操作且写操作必须过门禁；  
- Validation 覆盖待付款、退款、跨计划归因、自然与推广耦合；  
- 种草/收割在行为模式与调整频率上接口化区分。  

**安全边界：** 本轮无真实凭证、无真实调用。

### 4.4 参数基因与默认策略模板

**核心判断：**

- Genome 是可实例化的参数包，不是散落的 excel；  
- 按「价格带 × 计划类型 × 生命周期 × 活动状态」选择模板；  
- 目标函数权重模板直接服务 Objective Function Generator；  
- 所有默认数值标 **Proposed**，待历史优秀计划回灌后标定。  

---

## 5. 业务理解如何进入工程（防止理论被做薄）

| 业务洞察（来自 GA-1） | 工程落点 |
|---|---|
| 平台成交额 ≠ 真实成交额 | Business Data Validation 一票否决脏数据 |
| 低客单 vs 中高客单目标不同 | Objective Function Generator 模板 |
| 种草要探索放量，收割要稳定 | Domain Agent 行为模式 + 调整频率约束 |
| 库存/入仓是广告决策变量 | State Assembler + Risk 联动 |
| 上午差不代表全天差/大促要事件感知 | Forecast + Event Awareness |
| 预算有生命周期 | Budget Lifetime Prediction |
| 10 个新计划跑通 3 个不算 AI 失败 | Failure Pattern 必入库 |
| 调整后有响应窗口 | Reflection 校验 Adjustment Response Window |
| 最优动作有时是不调整 | NO_ACTION 合法输出 |

---

## 6. 我认为当前最大的风险（按杀伤力排序）

### R1 把项目做回“广告自动化工作流”
**症状：** 只有调价规则和 dashboard，没有知识升级与信任生长。  
**对策：** 用“四回路是否闭环”作为架构评审一票否决项。

### R2 Memory 与 Knowledge 混层
**症状：** 一次失败经验直接变成全局策略。  
**对策：** 强制 Quality Score + Evolution State Machine。

### R3 门禁事后补
**症状：** 先做聪明动作，后补风控。  
**对策：** Decision Packet 作为执行前置必填。

### R4 过早接真实账户
**症状：** 试错成本外溢，企业信任归零。  
**对策：** Shadow/只读优先；写权限走 Trust Level 与单独授权。

### R5 参数默认值被当成真理
**症状：** 模板数字没有历史支撑却被写死。  
**对策：** 全部 Proposed；预标定流程可追溯。

### R6 理论被工程文档“静默改写”
**症状：** 为实现方便改 Growth Agent 定义。  
**对策：** 单向派生 + Trace 矩阵；冲突停写并升级决策。

---

## 7. 建议的 GA-2 执行路线（我的方案）

```mermaid
flowchart LR
    A[架构 v0.2 评审] --> B[决策包与数据 Schema 冻结]
    B --> C[门禁状态机冻结]
    C --> D[JD 只读接口契约]
    D --> E[参数基因目录]
    E --> F[影子运行设计稿]
    F --> G[GA-2.0 工程基线]
    G --> H[GA-3 验证设计]
```

| 阶段 | 产出 | 成功标准 |
|---|---|---|
| S1 | 架构 Confirmed | 负责人签字/决策记录 |
| S2 | Schema + Decision Packet | 可序列化样例 + 追踪完整 |
| S3 | 门禁状态机 | 全动作路径可解释可拒绝 |
| S4 | Adapter 契约 | 脏数据规则可单测（模拟数据） |
| S5 | Genome 模板 | 可按四维分类实例化 |
| S6 | Shadow Mode 设计 | 为 GA-3 留验证钩子，无真实写 |

---

## 8. 本轮已交付清单

| 类型 | 路径 | 状态 |
|---|---|---|
| 架构 | `Research/GA-2/Architecture_Overview_v0.2.md` | Draft |
| 架构 v0.1 | `Research/GA-2/Architecture_Overview_v0.1.md` | Draft（被 v0.2 承接） |
| 追踪 | `Research/GA-2/Theory_Engineering_Trace.md` | Draft |
| Memory/Knowledge 边界 | `Research/GA-2/Memory_Knowledge_Boundary_v0.1.md` | Draft |
| Risk/Trust/Self-review | `Research/GA-2/Risk_Trust_SelfReview_v0.1.md` | Draft |
| 京东接入契约 | `Research/GA-2/JD_Adapter_Interface_v0.1.md` | Draft（被 v0.2 承接） |
| 参数基因模板 | `Research/GA-2/Parameter_Genome_Templates_v0.1.md` | Draft |
| 图 | `Figures/Mermaid/Figure-004_Growth_Agent_Architecture.mmd` | Draft |
| 本答卷 | `Research/GA-2/GA-2_Preliminary_Answer_2026-09-11.md` | Draft |
| 治理 | DEC-003 Accepted；会议/变更日志 | 已记录 |

### 8.1 四份详设交叉风险（汇总）

| ID | 风险 | 影响 | 建议裁决点 |
|---|---|---|---|
| X1 | 质量分/Trust/Risk 阈值均未历史标定 | 被当成“已验证真值”误用 | 全部 Proposed；预标定门禁 |
| X2 | Experience 双重归属（LE 过程 vs KE 中间态） | 职责漂移 | 以 Memory_Knowledge_Boundary 不变式为准 |
| X3 | 参数基因与 Strategy 边界 | Schema 二次迁移 | T09 评审裁决 |
| X4 | 收割托管计划写权限边界 | 门禁语义不清 | JD 问题单 + Risk 协同 |
| X5 | SIMULATION 回执污染 Memory | 学到假经验 | Adapter 环境标签 + Learning 过滤 |
| X6 | 失败永久保存 vs 理论“不必全部永久保存” | 成本/治理冲突 | 热/温/冷分层：降权非无痕删除 |

---

## 9. 需要你拍板的 5 件事

1. **架构 v0.2 是否按此方向冻结为 GA-2 主线？** —— **已确认：是**（GA-DEC-004）  
2. **CBA 是否确认为唯一最高协调者？** —— **已确认：是**  
3. **第一验证场是否锁定京东广告，抖音后置？** —— **已确认：是**  
4. **是否同意“先只读影子模式，写权限后置”作为工程红线？** —— **已确认：同意**  
5. **参数默认值是否全部按 Proposed 管理，待历史数据预标定？** —— **已确认：是**  

> 确认日期：2026-09-11。详见 `Meeting/Decision_Log.md` GA-DEC-004。

---

## 10. 结论

GARP 的成败，不取决于第一版 Agent 会不会调 API，而取决于：

> 是否把真实经营反馈，持续转化为可治理、可复用、可复利的企业知识，并在风险受控前提下扩大自治半径。

GA-1 已经把“为什么”讲清楚。  
GA-2 首轮答卷给出“怎么搭”的工程骨架：**四回路 + 决策包 + 门禁 + 场景隔离 + 参数基因**。  

下一步应评审冻结骨架，再进入数据 Schema 与门禁状态机的可执行基线，而不是直接堆功能。

---

**Document Status:** Draft  
**Next Action:** 项目负责人评审本答卷与 Architecture v0.2  
