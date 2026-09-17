# Changelog

本文件记录 Growth Agent Research Project 的全部可发布变更。格式参考 Keep a Changelog 的分类方法，版本遵循项目 `GA-MAJOR.MINOR` 规范。

## [Unreleased]

### Added

- 新增 `Research_Context.md`，作为阶段上下文快照。
- 新增 `Meeting/MiMo_Project_Understanding_Report_2026-09-11.md`。
- 新增 `Meeting/GA-2_Unlock_Checklist_2026-09-11.md`。
- 新增 `Research/GA-2/Architecture_Overview_v0.1.md` 与 `v0.2.md`（v0.2 为 Confirmed 主线）。
- 新增 `Research/GA-2/Theory_Engineering_Trace.md`（Draft）。
- 新增 `Research/GA-2/Memory_Knowledge_Boundary_v0.1.md`（Draft）。
- 新增 `Research/GA-2/Risk_Trust_SelfReview_v0.1.md`（Draft）。
- 新增 `Research/GA-2/JD_Adapter_Interface_v0.1.md`（Draft）。
- 新增 `Research/GA-2/Parameter_Genome_Templates_v0.1.md`（Draft）。
- 新增 `Research/GA-2/GA-2_Preliminary_Answer_2026-09-11.md`（Draft）。
- 新增 `Research/GA-2/Decision_Packet_Schema_v0.1.md`（Draft）。
- 新增 `Research/GA-2/Shadow_Mode_Design_v0.1.md`（Draft）。
- 新增 `Research/GA-2/Gate_Integration_Playbook_v0.1.md`（Draft）。
- 新增 `Research/GA-2/JD_Adapter_Interface_v0.2.md`（Draft，关闭 DPK-Q08）。
- 新增 `Research/GA-2/Forecast_Engine_Interface_v0.1.md`（Draft）。
- 新增 `Research/GA-2/Threshold_Calibration_Method_v0.1.md`（Draft）。
- 新增 `Research/GA-2/Gate_Integration_Playbook_v0.2.md`（Draft，关闭 JD-Q12）。
- 新增 `Research/GA-2/Fixture_Migration_Guide_v0.1.md`（Draft）。
- 新增 `Research/GA-2/Runtime_Envelope_Selfcheck_v0.1.md`（Draft）。
- 新增 `Research/GA-2/Precalibration_Experiment_Design_v0.1.md`（Draft）。
- 新增 `Research/GA-2/GA-2.0_Baseline_Package.md`（Confirmed，GA-DEC-005）。
- 新增 `Research/GA-2/GA-2_Complete_Review_Package.md`（Review Closed，选项 A）。
- 新增 `Research/GA-2/Reasoning_Engine_Interface_v0.1.md`（Draft）。
- 新增 `Research/GA-2/Learning_Reflection_Runtime_v0.1.md`（Draft）。
- 新增 `Research/GA-2/Shadow_Trial_Run_Plan_v0.1.md`（Draft）。
- 新增 `Research/GA-2/Cross_Document_Consistency_Audit_v0.1.md`（含 §8 关闭附录，C-01–C-08 Closed）。
- 新增 `Research/GA-2/Module_Skeleton_Design_v0.1.md`（Draft；CBAPort/OFGPort、EnvLabel+HUMAN）。
- 新增 `Research/GA-2/GA-3_Validation_Protocol_Draft_v0.1.md`（Draft，未启动 GA-3）。
- 新增 `Research/GA-2/ReadOnly_Connection_Assessment_v0.1.md`（Draft，未授权真实连接）。
- 新增 `Research/GA-2/Brain_Model_Training_Finetune_Plan_v0.1.md`（Draft；GA2-T33 2B 大脑模型训练微调计划）。
- 新增 `Research/GA-2/Brain_Model_Training_Feasibility_Foresight_v0.1.md`（Draft；GA2-T34 自进化与自我数据蒸馏可行性前瞻）。
- 新增 `Research/GA-2/GA-2_Completeness_Audit_v0.1.md`（Draft；综合 7.3/10）。
- 新增 `Research/GA-2/CBA_OFG_Interface_v0.1.md`（Draft）。
- 新增 `Research/GA-2/Error_Reason_Code_Catalog_v0.1.md`（Draft）。
- 新增 `Research/GA-2/Knowledge_Evolution_Runtime_v0.1.md`（Draft）。
- 新增 `Research/GA-2/Trust_Autonomy_Runtime_v0.1.md`（Draft）。
- 新增 `Research/GA-2/Decision_Packet_Schema_v0.2.md`（Draft）。
- 新增 `Research/GA-2/Decision_Packet_Schema_v0.2.1.md`（Draft 权威增量：DPK-I9…I12、动作—审批对应、decision_outcome）。
- 新增 `Research/GA-2/Gate_Integration_Playbook_v0.2.1.md`（Draft 权威增补：G-00…G-09、双谓词、Executed 重试）。
- 新增 `Research/GA-2/Error_Reason_Code_Catalog_v0.1.1.md`（Draft 门禁 outcome 增量：GATE-1006…1009/2008、ADAPT-2006/2007、DP-1005）。
- 新增 `Research/GA-2/Brain_Foundation_Decision_Proposal_v0.1.md`（Draft）。
- 新增 `Research/GA-2/GA-2_Release_Manifest_v0.1.md`（Draft；GA-2.0-RC1-draft；UNCOMMITTED）。
- 新增 `Meeting/GA-3_Protocol_Boundary_Decision_Draft.md`（方案 A 推荐）。
- 新增 `Research/GA-2/GA-2_Completeness_Audit_v0.2.md`（综合 **8.2/10**）。
- 新增 `garp/tests/unit/test_negative_gates.py`（审计 §11.2 负向套件）。
- 新增 `garp/packages/garp_runtime/bootstrap/credentials.py`（证据式凭证观察）。
- 新增 `Figures/Mermaid/Figure-004_Growth_Agent_Architecture.mmd`。
- 补录 `Research/GA-1/Research_Questions.md` 为 GA-RQ-001–018。
- 决策日志：`GA-DEC-003`–`006` Accepted；`GA-DEC-007` Proposed（GA-3 边界方案 A）。
- 会议日志：`GA-MTG-20260627-01`、`GA-MTG-20260911-01`–`08`、`GA-MTG-20260914-01`–`02`、`GA-MTG-20260915-01`。

### Changed

- `LICENSE`：改为 **Apache License 2.0**（完全开源，允许商用）。
- `README.md`：重写为全英文详细介绍（架构图、四回路、门禁、骨架、治理与诚实状态）。
- `Architecture_Overview_v0.2.md` §6：回写 lifecycle_status + review_result；packet_kind 冻结为 `standard`/`shadow_decision`。
- `Risk_Trust_SelfReview_v0.1.md` v0.1.1：review_result 六元含 NO_ACTION_APPROVE；SRA 独占写；G-* 对照表。
- canonical `source_env` = LIVE | SHADOW | SIMULATION | FIXTURE | **HUMAN**；REAL→LIVE 归一；GIP/Fixture 已改写。
- Module Skeleton：EnvLabel+HUMAN；CBAPort/OFGPort；packet_kind 注释。
- `PROJECT_SPEC.md`：允许 GA-2 工程设计（范围见 GA-DEC-003）；继续禁止 GA-3 与无授权真实 API。
- `ROADMAP.md`：GA-2 状态 Locked → Active。
- `Research/GA-2/Engineering_TODO.md`：解锁并登记任务。
- `README.md`：阶段说明更新为 GA-2 Active。
- `Research_Context.md`：阶段字段更新为 GA-2 Engineering Design（Active）。
- 按 `GA-1_Theory_v1.0.md` §13 单向同步 `Innovation_List.md` 至 GA-INNOV-010。
- 按理论基线刷新 `Glossary.md` 定义、来源章节与 Confirmed 状态，并补充 GA-TERM-015 至 018。
- 以项目负责人提供的完整文档替换 `GA-1_Theory_v1.0.md` 初始化占位内容。
- 确立 `GA-1_Theory_v1.0.md` 为所有 GA-1 相关工作的最高理论依据。
- 建立理论到术语、图表和论文结构的单向派生规则，禁止反向修改理论基线。

### Notes

- **Git 基线：** root commit `eda70ad`（2026-09-15）；tag `ga2-p0-remediation-20260915`；关闭 GA2-R01。
- 阶段切换依据：`GA-DEC-003` Accepted（2026-09-11）。
- 架构主线冻结依据：`GA-DEC-004` Accepted；`Architecture_Overview_v0.2.md` = Confirmed 主线。
- 工程基线确认：`GA-DEC-005` Accepted；`GA-2.0_Baseline_Package.md` = Confirmed。
- 一致性补丁：`GA-DEC-006`；XDCA §8 关闭 C-01–C-08。
- 完备性：v0.2 综合 **8.2/10**；四回路均有接口+运行时；Fixture 骨架可跑。
- 主线约束：CBA 唯一最高协调者；第一验证场=京东；Shadow/只读红线；默认参数一律 Proposed。
- 现行门禁：GIP v0.2.1（相对 v0.2 的权威增补）+ JD v0.2；动作—审批语义以 DPK v0.2.1 为准。
- 现行 Decision Packet 阅读方式：v0.1 字段主体 + v0.2 objective 增量 + v0.2.1 权威增量（合并阅读）。
- 阶段表述：**GA-2 Conditional — Design Baseline Not Yet Releasable**（审计 2026-09-15）。
- 未修改 `GA-1_Theory_v1.0.md`。
- GA-3 仍 Locked；真实写禁止；真实只读连接实施仍须单独授权；Brain 训练待 GA-DEC-008+。
- `code_revision` 仍为 UNCOMMITTED；R01 须负责人首次 git 提交。

## [GA-1.0] - 2026-06-27

### Added

- 初始化研究仓库目录、最高规范和维护流程。
- 建立 GA-1 理论文档、术语、创新点、研究问题和相关工作占位体系。
- 建立会议、决策、论文占位、附录和模板体系。
- 建立 `Figure-001` 至 `Figure-003` Mermaid 图源。
- 建立 GA-2 与 GA-3 阶段入口占位，并锁定当前阶段边界。
