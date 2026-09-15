# GA-2 Engineering TODO

**状态：** Active（GA-2 Conditional — Design Baseline Not Yet Releasable）  
**解锁决策：** `GA-DEC-003`（Accepted，2026-09-11）  
**主线冻结：** `GA-DEC-004`（Accepted，2026-09-11）  
**工程基线：** `GA-2.0_Baseline_Package.md`（**Confirmed**，GA-DEC-005，2026-09-11）  
**架构主线：** `Architecture_Overview_v0.2.md`（Confirmed）  
**Release Manifest：** `GA-2_Release_Manifest_v0.1.md`（Draft；release_id=`GA-2.0-RC1-draft`；code_revision=UNCOMMITTED）  
**输入基线：** `Research/GA-1/GA-1_Theory_v1.0.md`（GA-1.0 / v1.0）  
**第一验证场：** 京东广告（抖音后置）  
**工程红线：** Shadow/只读优先；写权限单独授权；默认参数一律 Proposed；真实只读连接仍须单独授权（GA2-T25）  
**外部审计：** `output/audit/GA-2_Modification_and_Design_Recommendations_2026-09-15.md`

## 1. 当前说明

GA-2.0-Draft 基线已由负责人选项 A 通过（GA-DEC-005）。2026-09-15 外部审计后进入 **GA-2 收敛轮**：停止横向扩写，优先关闭治理与门禁 P0。工程设计必须单向派生自 GA-1 理论基线。重大架构选择继续写入 `Meeting/Decision_Log.md`；偏离主线需新决策。

## 2. 主线约束（GA-DEC-004 + GA-DEC-005 + 审计收敛令）

1. CBA 为唯一最高协调者。  
2. 第一验证业务域锁定京东广告。  
3. Shadow / 只读优先；真实写操作后置且需单独授权。  
4. 参数、阈值、权重默认值一律 Proposed/Pending。  
5. 详设冲突时以 Architecture v0.2 + GA-DEC-004/005 为准。  
6. 现行门禁：GIP v0.2 + JD v0.2 双字段语义。  
7. P0 未全部关闭前，不确认新 GA-2 正式基线，不批准真实连接，不批准 GA-3 启动。  
8. 不伪造 git hash、测试通过或独立复核结论。

## 3. 任务看板

### 3.1 已完成（第一、二轮）

| 编号 | 任务 | 关联产出 | 状态 |
|---|---|---|---|
| GA2-T01 | 总体系统架构设计 | `Architecture_Overview_v0.2.md` | Done / Confirmed 主线 |
| GA2-T02 | 理论到工程追踪矩阵 | `Theory_Engineering_Trace.md` | Done (Draft) |
| GA2-T03 | 补录 GA-1 研究问题 | `../GA-1/Research_Questions.md` | Done (GA-RQ-001–018) |
| GA2-T04 | Memory/Knowledge 边界 | `Memory_Knowledge_Boundary_v0.1.md` | Done (Draft) |
| GA2-T05 | Risk/Trust/Self-review 闭环 | `Risk_Trust_SelfReview_v0.1.md` | Done (Draft) |
| GA2-T06 | 京东接入层接口规范 | `JD_Adapter_Interface_v0.1.md` | Done；被 v0.2 承接 |
| GA2-T07 | 参数基因与模板 | `Parameter_Genome_Templates_v0.1.md` | Done (Draft) |
| GA2-T08 | 初步答卷 | `GA-2_Preliminary_Answer_2026-09-11.md` | Done |
| GA2-T09 | 架构主线冻结评审 | `GA-DEC-004` | Done / Accepted |
| GA2-T10 | Decision Packet Schema | `Decision_Packet_Schema_v0.1.md` | Done (Draft) |
| GA2-T11 | Shadow Mode 设计稿 | `Shadow_Mode_Design_v0.1.md` | Done (Draft) |
| GA2-T12 | 门禁联调手册 v0.1 | `Gate_Integration_Playbook_v0.1.md` | Done；被 v0.2 承接 |
| GA2-T13 | Forecast Engine 接口 | `Forecast_Engine_Interface_v0.1.md` | Done (Draft) |
| GA2-T14 | 阈值回填方法论 | `Threshold_Calibration_Method_v0.1.md` | Done (Draft) |
| GA2-T18 | JD Adapter v0.2 | `JD_Adapter_Interface_v0.2.md` | Done；关闭 DPK-Q08 |
| GA2-T15 | 预标定实验设计 | `Precalibration_Experiment_Design_v0.1.md` | Done (Draft) |
| GA2-T19 | Gate Playbook v0.2 | `Gate_Integration_Playbook_v0.2.md` | Done；关闭 JD-Q12 |
| GA2-T20 | Fixture 迁移指南 | `Fixture_Migration_Guide_v0.1.md` | Done (Draft) |
| GA2-T21 | Runtime Envelope 自检 | `Runtime_Envelope_Selfcheck_v0.1.md` | Done (Draft) |
| GA2-T17 | GA-2.0 基线打包 | `GA-2.0_Baseline_Package.md` | Done / **Confirmed** |
| GA2-T22 | 完整研究包 | `GA-2_Complete_Review_Package.md` | Done / Review Closed |

### 3.2 已完成（GA-DEC-005 后设计轮）

| 编号 | 任务 | 关联产出 | 状态 |
|---|---|---|---|
| GA2-T23 | Reasoning Engine 接口与场景骨架 | `Reasoning_Engine_Interface_v0.1.md` | Done (Draft) |
| GA2-T24 | Learning/Reflection 运行时编排 | `Learning_Reflection_Runtime_v0.1.md` | Done (Draft) |
| GA2-T26 | Shadow 试运行计划（无写） | `Shadow_Trial_Run_Plan_v0.1.md` | Done (Draft) |
| GA2-T27 | 跨文档接口一致性终审 | `Cross_Document_Consistency_Audit_v0.1.md` + §8 关闭附录 | Done；C-01–C-08 **全部 Closed** |
| GA2-T28 | 模块边界与代码骨架 | `Module_Skeleton_Design_v0.1.md`（含 CBAPort/OFGPort、EnvLabel+HUMAN） | Done (Draft) |
| GA2-T29 | GA-3 验证协议草案 | `GA-3_Validation_Protocol_Draft_v0.1.md` | Done (Draft)；未启动 GA-3 |
| GA2-T25 | 真实只读连接**评估设计** | `ReadOnly_Connection_Assessment_v0.1.md` | Done (Draft)；**未授权真实连接** |
| GA2-T33 | 2B 大脑模型训练微调计划 | `Brain_Model_Training_Finetune_Plan_v0.1.md` | Done (Draft)；待负责人确认 Hybrid RE 与基座 |
| GA2-T34 | 模型训练可行性前瞻报告（自进化/蒸馏） | `Brain_Model_Training_Feasibility_Foresight_v0.1.md` | Done (Draft)；待负责人确认 M-B3 与双轨进化；**编号唯一保留** |
| GA2-T30 | 审计剩余冲突关闭 C-04–C-08 | XDCA §8；GIP/Fixture source_env 归一；引用卫生 | Done |
| GA2-T44 | 完备性审计 v0.1 | `GA-2_Completeness_Audit_v0.1.md` | Done (Draft)；综合 7.3/10；**编号迁移**：原误登记为第二个 GA2-T34 → 2026-09-15 改为 T44（见 §4.1） |
| GA2-T35 | CBA + OFG 接口详设 | `CBA_OFG_Interface_v0.1.md` | Done (Draft) |
| GA2-T36 | 全局错误码目录 | `Error_Reason_Code_Catalog_v0.1.md` | Done (Draft) |
| GA2-T31 | Fixture 影子代码骨架落地 | `garp/`（契约/门禁/envelope/FixtureTransport/自检/6 单测 PASS） | Done (Skeleton) |
| GA2-T37 | 知识演化回路运行时（回路 C） | `Knowledge_Evolution_Runtime_v0.1.md` | Done (Draft) |
| GA2-T38 | 信任自治回路运行时（回路 D） | `Trust_Autonomy_Runtime_v0.1.md` | Done (Draft) |
| GA2-T39 | DPK Schema v0.2 | `Decision_Packet_Schema_v0.2.md` | Done (Draft)；derivation_trace optional |
| GA2-T33c | Brain 基座确认建议书 | `Brain_Foundation_Decision_Proposal_v0.1.md` | Done (Draft)；待 **GA-DEC-008 或更高**（007 已预留给 GA-3 边界草案） |
| GA2-T40 | 完备性审计 v0.2 收口 | `GA-2_Completeness_Audit_v0.2.md` | Done；综合 **8.2/10** |

### 3.3 仍开放 / 后置

| 编号 | 任务 | 说明 | 状态 |
|---|---|---|---|
| GA2-T16 | 抖音 Domain Agent 占位细化 | 京东主线稳定后 | Deferred |
| GA2-T25b | 真实只读连接实施 | **须新 GA-DEC 单独授权** | Blocked by 授权 |
| GA2-T32 | GA-3 启动决策 | 协议草案后；边界见 GA-DEC-007 Proposed | Locked by 阶段门禁 |
| GA2-T33b | Brain 契约 Fixture 包 + Post-Validator | 待 BRAIN-Q01/02 与 GA-DEC-008+ | Pending |
| GA2-T41 | 完整 G-01–G-09 硬闸实现深化 | 当前 write_gate 为子集 | Open |
| GA2-T42 | FX-01… 全量 Fixture 样例数据 | 影子试运行前置 | Open |
| GA2-T43 | KE-* 并入 Error Catalog | 回路 C 建议码 | Partial（ERR v0.1.1 有门禁增量） |
| GA2-T45 | P0 代码门禁修复与负向测试 | `garp/` write_gate/packet/SRA/自检；28 tests | Done (Code) |
| GA2-T46 | P0 契约：DPK v0.2.1 / GIP v0.2.1 / ERR v0.1.1 | DPK-I9–I12；G-00…G-09；outcome 码 | Done (Draft 权威增量) |

## 4. 整改清单登记（审计 2026-09-15，GA2-R01…R15）

> 状态枚举：`Open` / `In Progress` / `Done (Governance)` / `Done` / `Blocked`。  
> **Done (Governance)** 仅表示文档/治理产物已生成；不等于测试通过或独立复核通过。  
> 治理整改完成后仍禁止真实连接与 GA-3 执行。

| 整改 ID | 优先级 | 事项 | 登记状态 | 本轮治理动作 / 关联产物 |
|---|---|---|---|---|
| GA2-R01 | P0 | 建立可恢复版本基线 | **Open**（Blocked by 负责人首次提交） | Manifest 已记 `code_revision=UNCOMMITTED`；不代提交、不伪造 hash |
| GA2-R02 | P0 | 统一 GA-2 权威清单 | **Done (Governance)** | 新建 `GA-2_Release_Manifest_v0.1.md`；每类唯一现行版本已列 |
| GA2-R03 | P0 | 修复 NO_ACTION/写动作审批串用 | **Done (Code)** | `packet.is_no_action`/`is_writable` 修复；DPK-I9–I11 契约；负向测试 28/28 |
| GA2-R04 | P0 | 修复 NO_ACTION 被拒仍出合法回执 | **Done (Code)** | write_gate 按 outcome 分支；REJECT/HOLD/REVISE 不出 approved 合成回执 |
| GA2-R05 | P0 | 冻结完整可执行谓词 | **Done (Document) / 部分 Code** | GIP v0.2.1 固化 G-00…G-09 与双谓词；代码实现 G-01/Shadow/NO_ACTION 子集，G-02–G-09 仍骨架 |
| GA2-R06 | P0 | 裁决 GA-3 草案治理边界 | **Done (Governance) / 待负责人 Accept** | `Meeting/GA-3_Protocol_Boundary_Decision_Draft.md` + Decision_Log GA-DEC-007 **Proposed** |
| GA2-R07 | P1 | 清理状态、版本和任务编号 | **Done (Governance)** | Architecture/Baseline 文末状态统一；ROADMAP/Context/SPEC 同步；T34 重号→T44；Trace 同步 |
| GA2-R08 | P1 | 交付真实机器可读 Schema | Open | 非本轮 |
| GA2-R09 | P1 | 补齐全量 Fixture | Open | 非本轮 |
| GA2-R10 | P1 | 自检由声明式改为证据式 | **Partial (Code)** | SC-A5/SC-B3 改为观察凭证提供者与 LiveTransport；其余检查仍偏声明 |
| GA2-R11 | P1 | 建立端到端可重放测试 | Open | 非本轮 |
| GA2-R12 | P1 | 更新理论—工程—测试追踪 | **Done (Governance) 部分** | Trace 增加 Code/Test/Evidence 列说明；完整证据链仍缺 git |
| GA2-R13 | P1 | 统一错误码 | **Partial** | ERR v0.1.1 门禁 outcome 增量；KE 全量与 HTTP 映射仍 Open |
| GA2-R14 | P2 | 补齐可观测性与数据治理 | Open | 非本轮 |
| GA2-R15 | P2 | 形成 GA-2 Release Candidate | Open | Manifest 保持 Draft / `-RC1-draft`；须独立复核 |

### 4.1 编号迁移记录

| 迁移前 | 迁移后 | 原因 | 日期 | 迁移依据 |
|---|---|---|---|---|
| GA2-T34（完备性审计 v0.1，与模型可行性前瞻重号） | **GA2-T44** | 审计 GA2-R07：T34 必须唯一；保留模型可行性前瞻为 T34 | 2026-09-15 | 外部审计 §3.3-6 |
| （占位）GA-DEC-007 = Brain 基座确认 | **GA-DEC-008 或更高** | 007 已用于 GA-3 边界 Proposed | 2026-09-15 | Decision_Log GA-DEC-007 编号占用说明 |

> 外部引用若仍写“第二个 T34 / 完备性审计 T34”，一律改读 T44。

## 5. 变更约束

1. 新文档放入 `Research/GA-2/`，文件名 `Pascal_Case.md`。  
2. 文首标注状态：`Draft` / `Under Review` / `Confirmed`；文末必须与文首一致，禁止文首 Confirmed 文末 Draft。  
3. 未确认内容不得表述为理论结论或已验证参数。  
4. 与理论基线冲突时，修改工程文档，不修改理论。  
5. 偏离 Architecture v0.2 主线须先写新 `GA-DEC-NNN`。  
6. 不伪造 git hash；`code_revision` 未提交前写 UNCOMMITTED。
