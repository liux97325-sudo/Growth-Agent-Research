# Research Context

**Current Project:** Growth Agent Research Project（GARP）  
**Current Version:** GA-2.0-conditional（理论输入仍锁定 GA-1.0）  
**Current Stage:** GA-2 Engineering Design — **Conditional：Design Baseline Not Yet Releasable**（Active，尚未形成可发布 RC）  
**Next Stage:** GA-3 Validation（仍 Locked；仅允许在 GA-DEC-007 Accepted 后做验证接口预研）  
**Primary Theory Source of Truth:** `Research/GA-1/GA-1_Theory_v1.0.md`  
**Primary Governance Spec:** `PROJECT_SPEC.md`  
**Primary Domain:** Enterprise AI / E-commerce Operational Decision-Making  
**Primary Platforms (Validation Scenarios):** JD.com（京准通广告）and Douyin  
**Core Scenario Experience:** JD Jingzhuntong advertising API + Quantitative Agent practice  

## 1. Stage Snapshot

| Item | Value |
|---|---|
| Theory baseline | `Research/GA-1/GA-1_Theory_v1.0.md`，状态 Confirmed，版本 v1.0 / GA-1.0 |
| Formal decisions (Accepted) | GA-DEC-001…006 |
| Formal decisions (Proposed) | GA-DEC-007（GA-3 验证接口预研边界；草案见 `Meeting/GA-3_Protocol_Boundary_Decision_Draft.md`；**待负责人**） |
| GA-2 local status | **Conditional — Design Baseline Not Yet Releasable**（文档收敛允许；真实连接/写/GA-3 执行禁止；RC 未形成） |
| Engineering baseline | GA-2.0-Draft-20260911（**Confirmed**，GA-DEC-005） |
| Release Manifest | `Research/GA-2/GA-2_Release_Manifest_v0.1.md`（Draft；release_id=`GA-2.0-RC1-draft`；code_revision=UNCOMMITTED） |
| GA-3 local status | Locked（实验执行禁止；接口预研待 GA-DEC-007） |
| Handoff date | 2026-09-11（MiMo Desktop 接手） |
| GA-2 first-wave scope | 总体系统架构 + 理论到工程追踪矩阵 |
| External audit | `output/audit/GA-2_Modification_and_Design_Recommendations_2026-09-15.md` |

## 2. Current Priority

1. 保持 GA-1 理论基线稳定，不反向修改。  
2. **GA-2 收敛轮（审计第一批 P0）：** 权威清单、状态冲突、T34 重号、GA-3 边界决策草案。  
3. 关闭 GA2-R01…R07 等治理项；禁止横向扩写新模块。  
4. 在 P0 全部关闭并具备可恢复 git 基线与测试证据前，**不确认 GA-2 RC，不批准真实连接，不批准 GA-3 启动**。  
5. 允许：文档收敛、Fixture、契约测试、无网络影子骨架、验证接口预研（待 GA-DEC-007）。  
6. 禁止：真实连接、真实写、GA-3 实验执行、Proposed 参数升格表述。

## 3. Do Not Modify Without Explicit Approval

- `Research/GA-1/GA-1_Theory_v1.0.md`（理论真相源；如需新版本须新建文件并由负责人授权）  
- `PROJECT_SPEC.md`（治理规范；变更须重大决策记录）  
- 已确认创新编号与主研究命题  
- 未经确认的真实广告/电商/ERP API 接入与操作脚本  

## 4. Working Roles

| Role | Owner |
|---|---|
| Research Architect | ChatGPT / GPT Thinking |
| Research Engineer | Codex |
| Local Research Operations Assistant | MiMo Desktop |
| Project Owner / Final Decision | 用户（研究负责人） |

## 5. Derived Material Rule

`Paper/`、`Figures/`、`Glossary.md`、`Innovation_List.md`、会议与决策日志均为派生材料；与理论基线冲突时，只修正派生材料。GA-2 工程文档同样为派生材料。

## 6. Last Sync

- **2026-09-15（治理整改第一批）：** 外部审计后建立 `GA-2_Release_Manifest_v0.1.md`（Draft / UNCOMMITTED）；统一 Architecture/Baseline 文末状态为 Confirmed；ROADMAP 删除过期待审表述；本文件同步 **GA-2 Conditional**；Engineering_TODO 修复 T34 重号并登记 GA2-R01…R15；Theory_Engineering_Trace 同步 T27 等；新建 GA-3 边界决策草案 + Decision_Log GA-DEC-007（Proposed）；PROJECT_SPEC 阶段改为 GA-2 Active。**未做 git commit；未改 GA-1。**  
- **2026-09-14（收口轮）：** 回路 C/D 运行时、DPK v0.2、Brain 建议书、garp/ 骨架（6 测试+selfcheck PASS）；完备性 **8.2/10**。  
- **2026-09-14（冲突关闭+完备审计）：** C-01–C-08 全关；完备性 7.3/10；补 CBA/OFG、错误码目录、Skeleton 端口；source_env 归一。  
- **2026-09-11（终审修复）：** T27–T29/T25 完成；GA-DEC-006 关闭 C-01/02/03；canonical source_env。  
- **2026-09-11（基线确认后）：** GA-DEC-005 Accepted；GA-2.0-Draft Confirmed。  
- **2026-09-11（基线打包）：** Gate v0.2 / Fixture / Runtime Envelope / 预标定实验完成。  
- **2026-09-11（第三轮）：** JD Adapter v0.2；Forecast；阈值方法论。  
- **2026-09-11（主线冻结）：** GA-DEC-004 Accepted。  
- **2026-09-11（首轮研究）：** 架构 v0.2 + 四类组件详设 + 初步答卷。  
- **2026-09-11（解锁）：** GA-DEC-003 Accepted。  
- **2026-09-11：** 建立本文件。  
