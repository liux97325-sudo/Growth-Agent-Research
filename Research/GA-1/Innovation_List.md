# GA-1 创新点清单

## 1. 管理规则

- 编号格式：`GA-INNOV-NNN`，编号一经分配不得复用。
- 状态枚举：`Proposed`、`Under Review`、`Confirmed`、`Deferred`、`Rejected`。
- “已验证”枚举：`No`、`Partial`、`Yes`；当前 GA-1 阶段不得标记为 `Yes`。
- 本文件为从 `Research/GA-1/GA-1_Theory_v1.0.md` §13 单向派生的索引，不是理论定义来源。
- 与理论基线冲突时，只修正本文件。
- 新增记录使用 `Templates/Innovation_Template.md`。

## 2. 创新点索引

| 编号 | 名称 | 提出时间 | 理论说明 | 状态 | 关联章节 | 是否已验证 | 未来计划 |
|---|---|---|---|---|---|---|---|
| GA-INNOV-001 | Growth Agent Theory | 2026-06-27（基线确立）/ 交接确认 2026-09-11 | 提出成长型 AI Agent 理论，将 AI 从任务工具重新定义为可成长的企业数字员工。 | Confirmed | `GA-1_Theory_v1.0.md` §3.1、§6.1、§13 | No | 在 GA-2 映射为可实现成长机制；GA-3 验证持续成长价值 |
| GA-INNOV-002 | Prediction-driven Decision | 2026-09-11（自理论基线同步） | 提出预测驱动决策机制，使 Agent 从响应历史结果转向预测未来状态。 | Confirmed | `GA-1_Theory_v1.0.md` §6.2、§13 | No | GA-2 设计 Forecast Engine；GA-3 验证预测准确率 |
| GA-INNOV-003 | Business State Awareness | 2026-09-11（自理论基线同步） | 提出经营状态感知模型，强调广告决策必须融合真实成交、库存、活动、预算与平台归因偏差。 | Confirmed | `GA-1_Theory_v1.0.md` §6.3、§7、§8.1、§13 | No | GA-2 设计数据校验与状态融合；GA-3 验证决策稳健性 |
| GA-INNOV-004 | Experience Distillation | 2026-09-11（自理论基线同步） | 提出经验蒸馏框架，将经营日志转化为可复用经验。 | Confirmed | `GA-1_Theory_v1.0.md` §6.4、§9、§13 | No | GA-2 设计 Knowledge/Learning Engine 蒸馏流程 |
| GA-INNOV-005 | Knowledge Evolution | 2026-09-11（自理论基线同步） | 提出知识演化路径：Data → Case → Experience → Rule → Strategy → Capability。 | Confirmed | `GA-1_Theory_v1.0.md` §6.5、§10、§13 | No | GA-2 设计知识层级与升级规则；GA-3 验证知识资产沉淀 |
| GA-INNOV-006 | Enterprise Knowledge Compounding | 2026-09-11（自理论基线同步） | 提出企业知识复利理论，强调 Growth Agent 能形成不可流失的企业知识资产。 | Confirmed | `GA-1_Theory_v1.0.md` §6.6、§10、§13 | No | GA-2 设计企业级知识资产结构；GA-3 评估长期复利价值 |
| GA-INNOV-007 | Trust-based Autonomous Growth | 2026-09-11（自理论基线同步） | 提出基于信任的自治成长机制，通过验证逐步提升 Agent 权限。 | Confirmed | `GA-1_Theory_v1.0.md` §6.7、§11、§13 | No | GA-2 设计 Trust Engine 与权限分级；GA-3 验证风险受控自治 |
| GA-INNOV-008 | Causal Memory | 2026-09-11（自理论基线同步） | 提出因果记忆机制，保存判断原因、动作依据与结果反思。 | Confirmed | `GA-1_Theory_v1.0.md` §9.2、§13 | No | GA-2 设计 Memory Engine 因果结构 |
| GA-INNOV-009 | Promotion Parameter Genome | 2026-09-11（自理论基线同步） | 提出商品推广参数基因模型，为不同类型商品建立参数模板。 | Confirmed | `GA-1_Theory_v1.0.md` §10.2、§13 | No | GA-2 做参数预标定与默认策略模板 |
| GA-INNOV-010 | Enterprise AI Operating System | 2026-09-11（自理论基线同步） | 提出企业 AI 操作系统设想，将多个专业 Agent 组织为统一经营系统。 | Confirmed | `GA-1_Theory_v1.0.md` §12、§13 | No | GA-2 设计总体架构；GA-3 验证多 Agent 协同价值 |

## 3. 状态变更记录

| 日期 | 创新编号 | 原状态 | 新状态 | 决策记录 | 说明 |
|---|---|---|---|---|---|
| 2026-09-11 | GA-INNOV-002 至 GA-INNOV-010 | — | Confirmed | GA-DEC-002 + `GA-1_Theory_v1.0.md` §13 | 依据理论基线单向同步，不新增理论主张 |
| 2026-09-11 | GA-INNOV-001 | Confirmed | Confirmed | GA-DEC-002 | 补全理论说明与关联章节，替换初始化占位表述 |
| 2026-06-27 | GA-INNOV-001 | — | Confirmed | Bootstrap specification | 按用户提供的示例状态初始化；未补写理论内容 |

## 4. 同步说明

- 2026-09-11 由 Local Research Operations Assistant（MiMo Desktop）根据 `GA-1_Theory_v1.0.md` §13 补全索引。  
- 未修改理论基线；未新增理论；未删除既有编号。  
- “是否已验证”全部保持 `No`，待 GA-3 验证后由负责人更新。  
