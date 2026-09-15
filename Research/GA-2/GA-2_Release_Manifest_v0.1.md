# GA-2 Release Manifest v0.1

**文档编号：** GA-2-MANIFEST-001  
**版本：** v0.1  
**Lifecycle Status:** Draft  
**Review Result:** Pending  
**日期：** 2026-09-15  
**依据：** 外部审计 `output/audit/GA-2_Modification_and_Design_Recommendations_2026-09-15.md` §3.1（GA2-R02）  
**Authorizing Decision:** 无（本 Manifest 为 Draft，不构成发布批准）  
**Authoritative For:** GA-2 权威文档清单、版本锚定与开放项登记（在负责人确认前仅作收敛基线）

---

## 0. 使用说明

1. 本文件是 GA-2 工程设计的**唯一发布清单**。实现者不得同时拼接多份互相冲突的“现行权威”文档。  
2. `Lifecycle Status` 在通过全部 P0 整改与独立复核前，保持 **Draft**；不得写 Final。  
3. `code_revision` 在仓库完成首次可恢复提交前，保持 **UNCOMMITTED**；禁止伪造 git hash。  
4. 全部阈值/默认参数仍为 **Proposed**；本 Manifest 不把任何 Proposed 参数升格为 Confirmed 真值。  
5. 硬约束：不修改 `Research/GA-1/GA-1_Theory_v1.0.md`；不授权真实连接、真实写或 GA-3 实验执行。

---

## 1. Manifest 字段（审计 §3.1）

| 字段 | 值 |
|---|---|
| **release_id** | `GA-2.0-RC1-draft` |
| **manifest_status** | Draft（非 Final；通过前不得改写） |
| **theory_input** | `Research/GA-1/GA-1_Theory_v1.0.md`；项目版本 `GA-1.0`；文件版本 `v1.0`；Lifecycle Status **Confirmed**（GA-DEC-002）；**Git hash：UNCOMMITTED**（仓库无提交，哈希待首次提交后回填） |
| **governance_input** | `PROJECT_SPEC.md`（规范版本 GA-1.0；阶段表述已同步 GA-2 Active）；决策列表：GA-DEC-001…006 **Accepted**；GA-DEC-007 **Proposed**（验证接口预研边界草案，待负责人） |
| **authoritative_docs** | 见 §2（每类仅一个现行权威） |
| **historical_docs** | 见 §3（禁止作为当前实现依据） |
| **schema_versions** | Decision Packet：v0.1 基线 + v0.2 增量（Draft，待合并为自包含现行版）；Runtime Envelope：`Runtime_Envelope_Selfcheck_v0.1`（Draft）；Receipt：GIP/JD v0.2 回执契约（Draft）；Error Catalog：`Error_Reason_Code_Catalog_v0.1`（Draft，KE-* 未并入） |
| **code_revision** | **UNCOMMITTED**（`garp/` 骨架与文档均未形成可恢复 git commit；首次提交由负责人决定，不得代填哈希） |
| **test_evidence** | 命令：`garp` 包内 6 项骨架单测 + `apps/cli/selfcheck.py`（历史记录：PASS）；**未绑定 commit**；未形成审计 §11.3 要求的完整证据包（用例数/失败数/运行时间/Fixture 版本/输出哈希）；**不得作为 GA-2 完整门禁成立证据** |
| **open_items** | 见 §5（阻塞 / 非阻塞分列） |
| **prohibited_scope** | 见 §6 |

---

## 2. Authoritative Docs（每类唯一现行版本）

> 分类遵循审计 §3.1 推荐。在负责人确认前，下列“现行”仅表示**实现时应优先引用**，不表示全部已完成独立评审。

| 类别 | 现行权威文件 | 当前 Lifecycle | 备注 |
|---|---|---|---|
| Architecture | `Research/GA-2/Architecture_Overview_v0.2.md` | **Confirmed**（GA-DEC-004） | 架构主线；文末 Draft 冲突已清理 |
| Engineering Baseline Package | `Research/GA-2/GA-2.0_Baseline_Package.md` | **Confirmed**（GA-DEC-005） | 标签 `GA-2.0-Draft-20260911`；标签名含 Draft 不等于文档未确认 |
| Decision Packet | `Decision_Packet_Schema_v0.1.md` + `Decision_Packet_Schema_v0.2.md`（增量） | Draft + Draft | **待合并**为自包含现行版（GA2-R02/审计 §4.1）；合并前实现须同时对照两份，禁止只读其一 |
| Gate | `Gate_Integration_Playbook_v0.2.md` | Draft | 双字段语义现行；GA-DEC-005 确认其为现行门禁权威 |
| Adapter | `JD_Adapter_Interface_v0.2.md` | Draft | 京东域现行；v0.1 历史 |
| Runtime Envelope | `Runtime_Envelope_Selfcheck_v0.1.md` | Draft | 组合矩阵与证据式自检待 P1 修订 |
| Risk / Trust / SRA | `Risk_Trust_SelfReview_v0.1.md` | Draft | 能力域 Trust、升权/冻结/回滚待 P1 |
| CBA / OFG | `CBA_OFG_Interface_v0.1.md` | Draft | |
| Forecast / Reasoning | `Forecast_Engine_Interface_v0.1.md` / `Reasoning_Engine_Interface_v0.1.md` | Draft | |
| Memory / Knowledge / Learning | `Memory_Knowledge_Boundary_v0.1.md` / `Learning_Reflection_Runtime_v0.1.md` / `Knowledge_Evolution_Runtime_v0.1.md` | Draft | |
| Trust Autonomy | `Trust_Autonomy_Runtime_v0.1.md` | Draft | 回路 D |
| Shadow | `Shadow_Mode_Design_v0.1.md` / `Shadow_Trial_Run_Plan_v0.1.md` | Draft | |
| Error Catalog | `Error_Reason_Code_Catalog_v0.1.md` | Draft | KE-* 并入待 T43 |
| Fixture / Test | `Fixture_Migration_Guide_v0.1.md` + `garp/` | Draft / Skeleton | 机器可运行目录与证据清单不完整 |
| Module Skeleton | `Module_Skeleton_Design_v0.1.md` | Draft | |
| Theory→Engineering Trace | `Theory_Engineering_Trace.md` | Draft | T27 已关闭；Code/Test/Evidence 列已说明 |
| Engineering TODO | `Engineering_TODO.md` | Active | 含 GA2-R01…R15 整改清单 |
| Completeness Audit | `GA-2_Completeness_Audit_v0.2.md` | Draft | 8.2/10；非独立证据 |
| GA-3 Protocol Working Note | `GA-3_Validation_Protocol_Draft_v0.1.md` | Draft | **非 GA-3 启动**；边界待 GA-DEC-007 |
| Governance Spec | `PROJECT_SPEC.md` | Active | 阶段已同步 GA-2 Active |
| Stage Roadmap | `ROADMAP.md` | Active | |
| Decision Log | `Meeting/Decision_Log.md` | Active | |
| Release Manifest | 本文件 | Draft | |

---

## 3. Historical Docs（禁止作为当前实现依据）

| 文件 | 承接关系 | 处理 |
|---|---|---|
| `Architecture_Overview_v0.1.md` | 被 v0.2 承接 | 仅演进记录 |
| `JD_Adapter_Interface_v0.1.md` | 被 v0.2 承接 | 仅演进记录 |
| `Gate_Integration_Playbook_v0.1.md` | 被 v0.2 承接 | 仅演进记录 |
| `GA-2_Completeness_Audit_v0.1.md` | 被 v0.2 承接 | 仅演进记录 |
| `Cross_Document_Consistency_Audit_v0.1.md` | 终审报告；C-01–C-08 Closed | 过程证据，非契约权威 |
| `GA-2_Complete_Review_Package.md` | 审阅入口；Review Closed | 过程材料 |
| `GA-2_Preliminary_Answer_2026-09-11.md` | 决策输入 | 过程材料 |
| `Brain_*` 相关文档 | 脑基/训练前瞻 | **不在本轮治理范围**；不得当作 GA-2.0-RC1 权威契约 |

---

## 4. 版本锚定约定

1. 首次 git 提交信息建议：`pre-remediation snapshot`；标签建议：`ga2-pre-remediation-20260915`。  
2. 提交后回填本文件 `code_revision` 与 `theory_input` 哈希，并 bump Manifest 版本。  
3. 每个 P0 整改项单独提交；禁止压成单次“大爆炸”提交。  
4. 测试证据必须绑定：commit、Python/OS、命令、用例数、失败数、Fixture 版本、Schema 版本、输出哈希。  
5. 在 Manifest 升为 Confirmed 前，`release_id` 不得去掉 `-draft` 后缀，也不得对外称 “GA-2.0 正式基线 / RC 通过”。

---

## 5. Open Items

### 5.1 阻塞项（关闭前不得宣称 GA-2 RC）

| ID | 事项 | 对应整改 |
|---|---|---|
| BLK-01 | Git 基线不存在（无 commit / 无标签） | GA2-R01 |
| BLK-02 | Decision Packet v0.1/v0.2 未合并为自包含权威 | GA2-R02 |
| BLK-03 | NO_ACTION 与普通动作审批串用未修复（代码） | GA2-R03 |
| BLK-04 | NO_ACTION 被拒仍可能出合法回执 | GA2-R04 |
| BLK-05 | G-01–G-09 可执行谓词未冻结唯一化 | GA2-R05 |
| BLK-06 | GA-3 协议与 SPEC 边界冲突（GA-DEC-007 仍 Proposed） | GA2-R06 |
| BLK-07 | 自检/测试证据不足（6 tests 不构成全门禁证明） | GA2-R10 / R11 |

### 5.2 非阻塞项（不阻塞文档收敛，但阻塞 RC）

| ID | 事项 | 对应整改 |
|---|---|---|
| OPEN-01 | 状态字段统一与元数据块覆盖全部 GA-2 文档 | GA2-R07（本轮部分完成） |
| OPEN-02 | 机器可读 JSON Schema 与校验器 | GA2-R08 |
| OPEN-03 | FX-01…FX-18 全量 Fixture | GA2-R09 |
| OPEN-04 | 端到端可重放测试 | GA2-R11 |
| OPEN-05 | 理论—工程—代码—测试—证据追踪闭环 | GA2-R12 |
| OPEN-06 | 错误码统一与 KE-* 并入 | GA2-R13 / T43 |
| OPEN-07 | 可观测性与数据治理规范 | GA2-R14 |
| OPEN-08 | 独立复核与 GA-2 RC 审议 | GA2-R15 |

---

## 6. Prohibited Scope（本 release 明确禁止）

1. 真实京东/抖音/ERP/财务 API 连接（只读亦须单独 GA-DEC）。  
2. 任何真实广告写操作或可产生平台副作用的脚本。  
3. 启动或执行 GA-3 实验；把验证协议草案当作已验证结论。  
4. 将 Proposed / Pending 阈值、权重、样本量表述为 Confirmed 或已验证真值。  
5. 修改 GA-1 理论基线正文。  
6. 伪造 git hash、测试通过记录或“独立复核”结论。  
7. 在 Manifest 未 Confirmed 前对外宣称 GA-2.0 正式发布或 RC 通过。

---

## 7. 变更记录

| 日期 | 版本 | 变更 | 依据 |
|---|---|---|---|
| 2026-09-15 | v0.1 | 首次建立 Draft Manifest；release_id=GA-2.0-RC1-draft；code_revision=UNCOMMITTED | 审计 §3.1 / GA2-R02；第一批 P0 治理项 |

---

**Document Status:** Draft  
**Owner Action:** 确认权威清单与 open items 后，方可将本 Manifest 升为 Under Review / Confirmed；在此之前禁止写 Final。
