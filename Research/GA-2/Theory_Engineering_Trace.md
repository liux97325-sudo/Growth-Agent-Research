# GA-2：理论到工程追踪矩阵

**文档编号：** GA-2-TRACE-001  
**版本：** v0.1.3  
**状态：** Draft  
**输入基线：** `Research/GA-1/GA-1_Theory_v1.0.md`（GA-1.0 / v1.0）  
**关联架构：** `Architecture_Overview_v0.2.md`（Confirmed，GA-DEC-004）  
**授权依据：** `GA-DEC-003` + `GA-DEC-004` + `GA-DEC-005`  
**发布清单：** `GA-2_Release_Manifest_v0.1.md`

---

## 1. 使用说明

1. 每一条 GA-1 理论主张/创新点，必须能追到至少一个 GA-2 工程组件或设计任务。  
2. 本矩阵为单向派生：理论 → 工程；工程反馈不得直接改理论。  
3. 状态枚举：`Mapped`（已映射）、`Partial`（部分）、`Open`（未覆盖）、`Out of Scope`（本轮明确不做）。  
4. 后续 GA-3 验证项应引用本矩阵中的工程 ID。  
5. **Code / Test / Evidence 列说明（简表）：** 用于从工程项继续下钻到实现与证据；`—` 表示尚未建立；骨架单测或文档自评 **不得** 单独作为门禁成立证据。

| 列 | 含义 | 合格取值示例 | 不合格示例 |
|---|---|---|---|
| Code | 对应代码路径或端口 | `garp/.../write_gate.py`；`CBAPort` | “见设计文档”（无路径） |
| Test | 可重复测试命令/用例 | `garp` 单测；FX-* Fixture ID | 仅“自评通过” |
| Evidence | 绑定版本的证据引用 | commit + Schema/Fixture 版本 + 输出哈希 | “6 tests PASS”且无 commit |

> 本轮（2026-09-15）仅建立列约定与关键行占位；完整 Code→Test→Evidence 闭环对应 GA2-R12 / 审计第二批，**尚未完成**。

---

## 2. 创新点追踪（GA-INNOV → Engineering）

| 创新编号 | 名称 | 理论章节 | 工程组件 / 设计项 | 工程 ID | 本轮状态 | 备注 |
|---|---|---|---|---|---|---|
| GA-INNOV-001 | Growth Agent Theory | §3.1, §6.1 | 成长闭环架构（执行-反馈-学习-知识-策略）；Trust 权限演进 | ARCH-LOOP, TE | Mapped | 总体架构 §1–5 |
| GA-INNOV-002 | Prediction-driven Decision | §6.2, §8.3 | Forecast Engine；双时间尺度决策 | FE, RE | Mapped | 预测为决策前置 |
| GA-INNOV-003 | Business State Awareness | §6.3, §8.1 | Business Data Validation；State Assembler | BDV, STATE | Mapped | 平台数据不可直信 |
| GA-INNOV-004 | Experience Distillation | §6.4, §9 | Learning Engine；三阶段推理记录 | LE, ME | Mapped | 日志→经验 |
| GA-INNOV-005 | Knowledge Evolution | §6.5, §10.3 | Knowledge Engine 层级（Case→Capability） | KE | Mapped | 知识演化路径 |
| GA-INNOV-006 | Enterprise Knowledge Compounding | §6.6, §10 | 企业知识资产库；基因/规则/标准复用 | KE, RULE/STRAT/CAP | Mapped | 长期复利载体 |
| GA-INNOV-007 | Trust-based Autonomous Growth | §6.7, §11.3 | Trust Engine；权限等级 0–5 | TE | Mapped | 自治受控成长 |
| GA-INNOV-008 | Causal Memory | §9.2 | Memory Engine Causal 子层 | ME | Mapped | O-H-A-R-R 结构 |
| GA-INNOV-009 | Promotion Parameter Genome | §10.2 | 参数基因库；默认策略模板 | KE / GA2-T07 | Mapped（详设 Draft） | `Parameter_Genome_Templates_v0.1.md` |
| GA-INNOV-010 | Enterprise AI Operating System | §12 | CBA + 专业 Agent + 引擎分层 | CBA, L2/L3 | Mapped | 总体分层架构 |

---

## 3. 核心理论模块追踪

| 理论模块 | 理论章节 | 工程落点 | 状态 |
|---|---|---|---|
| Growth Agent Theory | §6.1 | ARCH-LOOP | Mapped |
| Prediction-driven Decision | §6.2 | FE, RE | Mapped |
| Business State Awareness | §6.3 | BDV, STATE, ADAPT | Mapped |
| Experience Distillation | §6.4 | LE, ME, RFE | Mapped |
| Knowledge Evolution | §6.5 | KE | Mapped |
| Enterprise Knowledge Compounding | §6.6 | KE + 底座分层 | Mapped |
| Trust-based Autonomous Growth | §6.7 | TE, SRA, RKE | Mapped |
| Enterprise Digital Employee | §6.8 | 成熟形态目标；由 Trust/权限演进支撑 | Partial（形态定义在理论，工程只映射成长路径） |

---

## 4. 业务场景机制追踪

| 业务机制 | 理论章节 | 工程落点 | 状态 |
|---|---|---|---|
| 平台数据真实性校验 | §4.1/§8.1 | BDV | Mapped |
| 动态目标函数（低/中高客单） | §4.2/§7.2/§8.2 | OFG | Mapped |
| 种草 vs 收割行为模式 | §4.3/§7.3 | 场景 Agent 策略模式 | Mapped |
| 库存/仓配进入广告决策 | §4.4/§6.3 | STATE + Risk | Mapped |
| 日内预测干预 | §5.1 | FE + RE | Mapped |
| 活动事件感知 | §5.2 | STATE.Event + FE | Mapped |
| 预算生命周期预测 | §5.3 | FE.BudgetLifetime | Mapped |
| 失败即学习事件 | §6.1（交接）/§9.4 | LE Failure Pattern | Mapped |
| 三阶段推理闭环 | §6.4/§9.2 | ME causal + RFE | Mapped |
| 调整响应窗口 | §8.6 | RFE + LE | Mapped |
| 跨计划学习 | §10.1 | LE | Mapped |
| 知识结晶 | §10.3 | KE | Mapped |
| 动态风险基线 | §11.1 | RKE | Mapped |
| 自审批 | §11.2 | SRA | Mapped |
| Trust Score | §11.3 | TE | Mapped |
| 周期反思 | §11.4 | RFE | Mapped |
| 企业 AI OS 结构 | §12 | CBA 分层 | Mapped |

---

## 5. GA-1 研究问题 → 工程回应（首轮）

| 研究问题（理论 §2） | 工程回应组件 | 状态 |
|---|---|---|
| 如何从真实业务环境获得经营经验？ | ADAPT→BDV→ME→LE | Mapped |
| 如何区分有效/噪声/干扰数据？ | BDV + Experience Quality Score（LE/KE） | Partial |
| 如何把一次投放转化为可复用经验？ | Causal Memory + LE distillation | Mapped |
| 如何从多计划总结企业级规律？ | LE Cross-plan + KE | Mapped |
| 如何通过预测驱动提前干预？ | FE + RE | Mapped |
| 如何控制成长试错成本？ | RKE + SRA + TE | Mapped |
| 企业如何建立信任机制？ | TE Trust Score/Level | Mapped |
| 如何从工具成长为决策者？ | 权限等级 0–5 | Mapped |
| 如何形成不可流失知识资产？ | KE 底座 | Mapped |
| 如何成为企业数字员工？ | 综合架构终态（GA-3 验证） | Partial |

---

## 6. 缺口与后续任务

| 缺口 | 对应 TODO | 说明 | 状态 | Code | Test | Evidence |
|---|---|---|---|---|---|---|
| 参数基因详设 | GA2-T07 | 字段、校验、默认模板目录 | Draft 已产出 | — | — | 文档 Draft |
| Memory/Knowledge 数据模型 | GA2-T04 | Schema、状态机、读写边界 | Draft 已产出 | — | — | 文档 Draft |
| 审批状态机细节 | GA2-T05 | Risk/Trust/Self-review 闭环 | Draft 已产出 | 部分骨架 | 6 单测（子集） | UNCOMMITTED |
| 平台接口规范 | GA2-T06/T18 | 京东域抽象契约，先只读；v0.2 双字段 | Draft 已产出 | `adapter/` 骨架 | FixtureTransport | UNCOMMITTED |
| 研究问题正式编号 | GA2-T03 | GA-RQ-001–018 | 已补录 | — | — | 文档 |
| Decision Packet 可序列化样例 | GA2-T10/T39 | v0.1 基线 + v0.2 增量（待合并） | Draft 已产出 | `packet` 契约骨架 | 部分单测 | UNCOMMITTED |
| Shadow Mode 设计 | GA2-T11/T26 | 设计 + 无写试运行计划 | Draft 已产出 | — | — | 文档 Draft |
| 门禁联调手册 | GA2-T12/T19 | Risk×Trust×G-01–G-09；v0.2 双字段 | Draft 已产出 | `write_gate.py` 子集 | 子集单测 | UNCOMMITTED；完整 G-00–G-09 仍 Open（T41） |
| Runtime Envelope 自检 | GA2-T21 | 防影子污染 | Draft 已产出 | `boot_selfcheck` 类 | selfcheck CLI | 历史 PASS；证据包不完整（GA2-R10） |
| Fixture 迁移 | GA2-T20/T42 | v0.1→v0.2；全量 FX-* | Draft 已产出；FX 全量 Open | `fixture_transport.py` | 部分 | UNCOMMITTED |
| 预标定实验 | GA2-T15 | 复用 TCAL | Draft 已产出 | — | — | 文档；参数 Proposed |
| Reasoning 接口 | GA2-T23 | 五场景骨架 + NO_ACTION | Draft 已产出 | — | — | 文档 Draft |
| Learning/Reflection 编排 | GA2-T24 | 回路 B 运行时 | Draft 已产出 | — | — | 文档 Draft |
| 知识演化 / 信任自治运行时 | GA2-T37/T38 | 回路 C / D | Draft 已产出 | — | — | 文档 Draft |
| CBA/OFG 接口 | GA2-T35 | 协调与目标函数 | Draft 已产出 | Port 骨架 | — | 文档 Draft |
| 错误码目录 | GA2-T36/T43 | 全局目录；KE-* 待并入 | Draft 已产出；T43 Open | — | — | 文档 Draft |
| 模块骨架 | GA2-T28/T31 | 边界 + garp/ 落地 | Done (Draft/Skeleton) | `garp/` | 6 单测 PASS（历史） | **无 commit** |
| 跨文档一致性终审 | GA2-T27 | C-01–C-08 关闭附录 | **Done；C-01–C-08 Closed** | — | — | XDCA §8 |
| 完备性审计 | GA2-T44/T40 | v0.1→v0.2；8.2/10 | Done (Draft)；**非独立证据** | — | — | 自评文档 |
| GA-3 协议草案 | GA2-T29 | 预注册契约；非启动 | Done (Draft)；边界待 GA-DEC-007 | — | — | 文档 Draft |
| 技术栈 | 后置 | 不阻塞架构评审 | Open | — | — | — |
| 端到端可重放 / 负向全量 | GA2-R03…R11 | 审计第二批 | Open | 待实现 | 待实现 | 待绑定 commit |

---

## 7. 变更记录

| 日期 | 版本 | 变更 | 依据 |
|---|---|---|---|
| 2026-09-11 | v0.1 | 首次建立；覆盖 GA-INNOV-001–010 与核心业务机制 | GA-DEC-003；GA-1 Theory v1.0 |
| 2026-09-11 | v0.1.1 | 缺口状态更新：T03–T07 详设 Draft 已产出；补 T10/T11 | 组件详设并行完成 |
| 2026-09-11 | v0.1.2 | 补 T12–T21、T23/T24/T26；基线 Confirmed 后扩展 | GA-DEC-005 |
| 2026-09-15 | v0.1.3 | **治理同步：** T27 由 Open 改为 Done/Closed；补 T28–T43（含 T44 编号迁移）；增加 Code/Test/Evidence 列说明 | 外部审计 GA2-R07/R12；`GA-2_Release_Manifest_v0.1.md` |

---

**Document Status:** Draft（与文首一致）  
**Lifecycle Status:** Draft  
**Authoritative For:** GA-1 理论主张/创新点 → GA-2 工程落点追踪（下钻证据列待闭环）  
**Owner Review:** GA-2.0 基线已 Confirmed；本矩阵待 Code/Test/Evidence 闭环与独立复核后升 Under Review  
**Explicit Non-Claim:** 本表“Draft 已产出 / Done”仅表示产物存在，不表示门禁实现完整、测试充分或 RC 通过。
