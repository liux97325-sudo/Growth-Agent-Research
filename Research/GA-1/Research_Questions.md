# GA-1 研究问题

## 1. 管理规则

研究问题编号格式为 `GA-RQ-NNN`。每个问题必须记录来源、状态、关联理论或创新，以及预期处理阶段。  
状态枚举：`Open`、`Under Review`、`Answered`、`Deferred`、`Closed`。

说明：本索引依据 `GA-1_Theory_v1.0.md` §2 与 §16 单向补录，供 GA-2 工程追踪与 GA-3 验证引用；不新增理论主张。

## 2. 研究问题索引

| 编号 | 问题 | 来源 | 状态 | 关联项 | 目标阶段 | 备注 |
|---|---|---|---|---|---|---|
| GA-RQ-001 | AI Agent 如何从真实业务环境中获得经营经验？ | Theory §2.1 | Open | GA-INNOV-003/004；ADAPT/BDV/ME/LE | GA-2 设计 + GA-3 验证 | 工程映射见 Trace |
| GA-RQ-002 | AI Agent 如何区分有效数据、噪声数据与干扰数据？ | Theory §2.2 | Open | GA-INNOV-003；BDV；Experience Quality Score | GA-2 + GA-3 | 校验与质量评分 |
| GA-RQ-003 | AI Agent 如何将一次投放行为转化为可复用经验？ | Theory §2.3 | Open | GA-INNOV-004/008；LE/ME | GA-2 + GA-3 | 经验蒸馏 |
| GA-RQ-004 | AI Agent 如何从多个计划中总结出企业级经营规律？ | Theory §2.4 | Open | GA-INNOV-005/006/009；LE/KE | GA-2 + GA-3 | 跨计划学习 |
| GA-RQ-005 | AI Agent 如何通过预测驱动提前干预经营状态？ | Theory §2.5 | Open | GA-INNOV-002；FE/RE | GA-2 + GA-3 | 含预算寿命预测 |
| GA-RQ-006 | AI Agent 如何在成长过程中控制试错成本？ | Theory §2.6 | Open | GA-INNOV-007；RKE/SRA | GA-2 + GA-3 | 风险基线 |
| GA-RQ-007 | 企业如何建立对 AI Agent 的信任机制？ | Theory §2.7 | Open | GA-INNOV-007；TE | GA-2 + GA-3 | Trust Score |
| GA-RQ-008 | AI Agent 如何从工具、助手、执行者逐步成长为经营决策者？ | Theory §2.8 | Open | GA-INNOV-001/007；权限等级 | GA-2 + GA-3 | 权限演进 |
| GA-RQ-009 | AI Agent 如何形成企业不可流失的知识资产？ | Theory §2.9 | Open | GA-INNOV-005/006；KE | GA-2 + GA-3 | 知识复利 |
| GA-RQ-010 | Growth Agent 如何最终成为企业数字员工？ | Theory §2.10 | Open | GA-INNOV-001/010 | GA-3 主验证 | 终态命题 |
| GA-RQ-011 | Growth Agent 是否能提升预测准确率？ | Theory §16.1 | Open | GA-INNOV-002 | GA-3 | 验证入口 |
| GA-RQ-012 | Growth Agent 是否能提升 ROI 并降低无效花费？ | Theory §16.2–16.3 | Open | 场景 Agent | GA-3 | 验证入口 |
| GA-RQ-013 | Growth Agent 是否能减少人工运营成本？ | Theory §16.4 | Open | 自治路径 | GA-3 | 验证入口 |
| GA-RQ-014 | Growth Agent 是否能提升计划成功率？ | Theory §16.5 | Open | 参数基因/策略 | GA-3 | 验证入口 |
| GA-RQ-015 | Growth Agent 是否能通过反思持续改进？ | Theory §16.6 | Open | RFE/LE | GA-3 | 验证入口 |
| GA-RQ-016 | Growth Agent 是否能形成可复用经营知识？ | Theory §16.7 | Open | KE | GA-3 | 验证入口 |
| GA-RQ-017 | Growth Agent 是否优于传统规则系统或普通人工运营？ | Theory §16.8–16.9 | Open | 对照实验设计 | GA-3 | 需基线方案 |
| GA-RQ-018 | Growth Agent 是否具备长期商业价值？ | Theory §16.10 | Open | 知识复利/成本 | GA-3 | 终局评估 |

## 3. 问题记录模板

### GA-RQ-NNN：问题标题

- **问题：** 待填写
- **提出日期：** YYYY-MM-DD
- **来源：** 待填写
- **状态：** Open
- **关联理论：** 待填写
- **关联创新：** 待填写
- **处理记录：** 待填写
- **结论或延期理由：** 待填写

## 4. 同步说明

- **2026-09-11：** 由 MiMo 依据理论基线补录 GA-RQ-001 至 018；状态统一 Open。  
- 未修改理论；未新增理论问题表述之外的主张。  
- GA-2 工程任务可通过 `Theory_Engineering_Trace.md` 回引本表。  
