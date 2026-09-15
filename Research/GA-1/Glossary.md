# GA-1 统一术语表

## 1. 使用规则

本文件是从 `GA-1_Theory_v1.0.md` 派生的术语检索与统一使用索引，不是理论定义来源。GA-1 理论文件是术语含义的最高依据；本文件与其冲突时，只能修正本文件，不得反向修改理论。状态为 `Pending Review` 的条目不得作为已确认理论引用。

## 2. 状态说明

- `Canonical Name`：规范名称已登记。
- `Pending Review`：文档使用范围已给出，理论内涵仍待 GA-1 评审。
- `Confirmed`：理论定义已由正式决策确认，或已完整出现在 `GA-1_Theory_v1.0.md` 并经 2026-09-11 交接确认同步。

## 3. 规范术语

| 编号 | 规范术语 | 统一中文名 | 文档使用定义（源自理论基线） | 禁止替代写法 | 状态 | 来源章节 |
|---|---|---|---|---|---|---|
| GA-TERM-001 | Growth Agent | 成长型 AI Agent / 成长型智能体 | 一种能够在真实业务环境中持续执行经营任务，并基于真实经营反馈完成经验提取、知识更新、策略修正和自主优化，从而实现经营决策能力持续提升的企业级智能体。与传统 Agent 的本质区别不在是否调用工具，而在是否具备持续实践、真实反馈学习、经验蒸馏、知识演化、预测驱动决策、风险受控成长、企业专属知识沉淀与权限随信任提升等能力。 | 未经批准的其他英文名或中文译名；不得写成普通 Workflow Agent | Confirmed | §3.1、§6.1 |
| GA-TERM-002 | Enterprise Digital Employee | 企业数字员工 | Growth Agent 的成熟形态；不是简单软件工具或一次性部署程序，而是能在企业内部长期积累业务经验、形成企业知识资产，并逐步承担经营决策职能的数字化经营主体。成长路径：Tool → Assistant → Operator → Decision Maker → Enterprise Digital Employee。 | Digital Worker 等未登记名称 | Confirmed | §3.2、§6.8 |
| GA-TERM-003 | Knowledge Evolution | 知识演化 | 知识成长不是简单数据累积，而是从原始数据逐步演化为经营能力：Raw Data → Business Case → Experience → Operational Rule → Strategy → Capability。 | Knowledge Growth 等 | Confirmed | §6.5、§10.3 |
| GA-TERM-004 | Experience Distillation | 经验蒸馏 | 将原始经营日志转化为可复用经营经验的过程；目标不是保存更多指标，而是解释为何变化、为何有效/失败，以及下次如何调整。典型拆解：调整前、调整中、调整后、反思、知识化。 | Experience Extraction 等 | Confirmed | §6.4、§9 |
| GA-TERM-005 | Business State Awareness | 经营状态感知 | Agent 决策前对真实经营状态的理解与校验；须综合推广花费、真实成交、库存、生命周期、活动周期、预算、审核合规、计划稳定性、类目竞争与企业经营目标等，而不是直接相信平台返回指标。 | Business Awareness 等 | Confirmed | §6.3、§8.1 |
| GA-TERM-006 | Prediction-driven Decision | 预测驱动决策 | 从 Reaction-driven Decision 升级为预测未来经营状态并提前干预的决策方式；预测对象包括 CTR、CPC、CVR、ROI、GMV、加购、预算耗尽时间、库存、日内走势、活动周期、计划稳定性与生命周期趋势等。 | Predictive Decision 等 | Confirmed | §6.2、§8.3 |
| GA-TERM-007 | Chief Business Agent | 首席经营智能体 | 企业 AI Operating System 结构中的最高协调者，负责企业级经营目标协调；下接 Planning / Forecast / Advertising / Content / Inventory / Pricing / Risk / Review / Learning / Knowledge 等专业 Agent。 | Master Agent、Main Agent、Chief Agent（未加 Business 时须澄清） | Confirmed | §12 |
| GA-TERM-008 | Learning Engine | 学习引擎 | 交接与理论入口中列出的 GA-2 工程组件之一，对应经验学习与成长判断能力；具体接口与实现属 GA-2 设计范围。 | Learner 等 | Confirmed（概念登记） | §15；交接文档 GA-2 清单 |
| GA-TERM-009 | Memory Engine | 记忆引擎 | 交接与理论入口中列出的 GA-2 工程组件之一；理论侧对应长期经营记忆、Permanent Knowledge Unit 与 Causal Memory。 | Memory Module 等 | Confirmed（概念登记） | §9、§15 |
| GA-TERM-010 | Knowledge Engine | 知识引擎 | 交接与理论入口中列出的 GA-2 工程组件之一；理论侧对应经验蒸馏、知识演化、知识结晶与企业经营标准沉淀。 | Knowledge Module 等 | Confirmed（概念登记） | §6.4–6.5、§10、§15 |
| GA-TERM-011 | Forecast Engine | 预测引擎 | 交接与理论入口中列出的 GA-2 工程组件之一；理论侧对应预测驱动决策中的未来状态输出（走势、预算生命周期、ROI/CVR 等）。 | Prediction Engine 等 | Confirmed（概念登记） | §6.2、§15 |
| GA-TERM-012 | Reflection Engine | 反思引擎 | 交接与理论入口中列出的 GA-2 工程组件之一；理论侧对应 Weekly Reflection Engine 与调整后复盘机制。 | Reflective Engine 等 | Confirmed（概念登记） | §11.4、§15 |
| GA-TERM-013 | Risk Engine | 风险引擎 | 交接与理论入口中列出的 GA-2 工程组件之一；理论侧对应 Dynamic Risk Baseline 与试错成本控制。 | Risk Module 等 | Confirmed（概念登记） | §11.1、§15 |
| GA-TERM-014 | Trust Engine | 信任引擎 | 交接与理论入口中列出的 GA-2 工程组件之一；理论侧对应 Trust Score 与权限随信任逐步提升。 | Trust Module 等 | Confirmed（概念登记） | §6.7、§11.3、§15 |
| GA-TERM-015 | Self-review Agent | 自审批 Agent | 在新建或修改计划前进行风控预审批的 Agent；审批依据包括历史优秀/失败模型、库存、预算、审核合规、生命周期、企业目标、置信度与 Trust Score。 | Review-only Bot 等 | Confirmed | §11.2 |
| GA-TERM-016 | Promotion Parameter Genome | 商品推广参数基因 | 不同商品类型对应的推广参数组合模板，如初始预算、ROI、出价、人群溢价、种草/收割比例、预期指标、风险基线与调整频率。 | Parameter Template（作为同义替代时须关联本编号） | Confirmed | §10.2 |
| GA-TERM-017 | Causal Memory | 因果记忆 | 不只记录发生了什么，还记录为什么发生、为什么这样判断/调整、为何成功或失败、下次如何避免、是否可迁移。 | Event Log（仅事件日志不等于因果记忆） | Confirmed | §9.2 |
| GA-TERM-018 | Continuous Business Decision-Making | 连续经营决策 | 企业在动态市场环境下，围绕经营目标持续进行感知、预测、判断、执行、反馈和修正的过程；电商广告与运营属于此类问题，而非单次任务执行。 | One-shot Task Execution | Confirmed | §3.3 |

## 4. 变更流程

新增或修改本索引时，必须注明 `GA-1_Theory_v1.0.md` 中的来源位置、影响文档和评审记录；变更确认后同步更新 `Appendix/Acronyms.md`、`Appendix/Symbols.md` 及所有引用处。不得通过术语维护反向改变理论。

## 5. 同步说明

- 2026-09-11：由 MiMo Desktop 依据 `GA-1_Theory_v1.0.md` 刷新定义与状态。  
- GA-TERM-001 至 006、008 至 014：由 Pending Review 更新为 Confirmed（理论基线中已有完整概念表述）。  
- GA-TERM-007：将 Chief Agent 明确为理论中的 Chief Business Agent。  
- 新增 GA-TERM-015 至 018，均直接来自理论基线，不新增理论。  
- 工程引擎类术语标记为 “Confirmed（概念登记）”，实现细节仍待 GA-2。  
