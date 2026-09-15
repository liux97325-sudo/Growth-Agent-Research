# Decision Log

## 1. 管理规则

重大设计决策编号格式为 `GA-DEC-NNN`。记录一经确认不得覆盖；后续变更通过新决策注明替代关系。

## 2. 决策索引

| 编号 | 日期 | 标题 | 状态 | 决策者 | 替代关系 |
|---|---|---|---|---|---|
| GA-DEC-007 | 2026-09-15 | 明确 GA-3 协议与验证接口预研的治理边界（方案 A 推荐） | **Proposed** | 待负责人 | 在 GA-DEC-005/006 之上裁决协议边界；**未 Accept 前不生效** |
| GA-DEC-006 | 2026-09-11 | 关闭跨文档终审必改项并规范 source_env | Accepted | Project Owner（完全批准下一步研究） | 在 GA-DEC-005 之上做一致性补丁 |
| GA-DEC-005 | 2026-09-11 | 确认 GA-2.0-Draft 工程基线并进入下一设计轮 | Accepted | Project Owner | 在 GA-DEC-004 之上确认基线包 |
| GA-DEC-004 | 2026-09-11 | 冻结 GA-2 架构主线与四项工程原则 | Accepted | Project Owner | 在 GA-DEC-003 之上冻结主线 |
| GA-DEC-003 | 2026-09-11 | 准备进入 GA-2 工程设计（阶段解锁） | Accepted | Project Owner | 补充 GA-DEC-001/002 的阶段门禁执行 |
| GA-DEC-002 | 2026-06-27 | 确立 GA-1 Theory v1.0 为最高理论依据 | Accepted | Project Owner | 补充 GA-DEC-001 |
| GA-DEC-001 | 2026-06-27 | 建立 GARP 研究仓库治理基线 | Accepted | Project Owner | — |

## 3. GA-DEC-007：明确 GA-3 协议与验证接口预研的治理边界（Proposed）

- **日期：** 2026-09-15
- **状态：** **Proposed（待负责人确认；Accept 前不构成生效授权）**
- **决策者：** 待 Project Owner
- **草案全文：** `Meeting/GA-3_Protocol_Boundary_Decision_Draft.md`
- **背景：**
  1. `PROJECT_SPEC.md` 禁止「启动 GA-3 实验设计或验证」。  
  2. `GA-3_Validation_Protocol_Draft_v0.1.md`（GA2-T29）已含假设、指标、对照与预注册结构，与 SPEC 字面存在边界张力。  
  3. 外部审计（2026-09-15）§13 要求负责人在方案 A/B 中裁决，推荐方案 A。
- **推荐方案（A）：允许验证接口预研，禁止实验执行**
  1. 允许在 GA-2 内设计验证可观测接口、日志字段、预注册模板与报告骨架。  
  2. 不允许启动实验、接入真实验证数据或产生验证结论。  
  3. 全部统计门槛、样本量、窗口保持 **Proposed**。  
  4. `GA-3_Validation_Protocol_Draft_v0.1.md` 定位为预注册契约草稿，**不是** GA-3 启动证明。  
  5. 正式 GA-3 协议必须在 GA-3 解锁后重新评审确认。
- **方案 B（备选，若负责人否决 A）：** 将协议标为 `Non-authoritative Working Note`，移出权威基线与 TODO Done，GA-3 解锁后再迁移。
- **编号占用说明：** Engineering_TODO 中 GA2-T33c（Brain 基座确认）原占位“待 GA-DEC-007”已因本条目占用 007；Brain 基座确认请改用 **GA-DEC-008 或更高**编号，不得复用 007。
- **禁止（无论 A/B）：** 修改 GA-1；真实连接；真实写；把 Proposed 参数写成 Confirmed；在 Accept 前按本草案执行任何“已授权”表述。
- **后续动作：** 负责人勾选草案 §7 裁决项 → 本条状态改为 Accepted 或替换为方案 B 条目 → 同步 SPEC/Context/Todo 状态。

## 4. GA-DEC-006：关闭跨文档终审必改项并规范 source_env

- **日期：** 2026-09-11
- **状态：** Accepted
- **决策者：** Project Owner（授权“完全批准下一步研究”覆盖本轮终审修复）
- **背景：** `Cross_Document_Consistency_Audit_v0.1.md` 登记 8 条冲突；必改 C-01/C-02/C-03 阻塞实现前全量冻结。
- **决定：**
  1. **C-02 关闭：** Architecture v0.2 §6 回写 `lifecycle_status` + `review_result` 双字段与可执行公式（不改变主线结构，仅契约对齐）。
  2. **C-01 关闭：** `Risk_Trust_SelfReview_v0.1.md` §6 明确 review_result 枚举含 `NO_ACTION_APPROVE`、SRA 独占写、与 lifecycle 分离。
  3. **C-03 规范：** **canonical `source_env` ∈ {FIXTURE, SIMULATION, SHADOW, LIVE}**（以 JD v0.2 为准）；GIP 中 `source=REAL` 作为 **LIVE 别名**，实现须归一，禁止双轨过滤。
  4. 实现前仍须消化审计其余中低项；在 M1–M4 全关前 **不得** 宣称全量一致或做真实写路径。
- **影响：** 架构 §6、Risk/Trust §6、后续 GIP/JD/Fixture 实现引用；审计报告可标 C-01/C-02/C-03 已决议关闭。
- **禁止：** 不修改 GA-1；不因本决策授权真实 API。

## 5. GA-DEC-005：确认 GA-2.0-Draft 工程基线并进入下一设计轮

- **日期：** 2026-09-11
- **确认日期：** 2026-09-11
- **状态：** Accepted
- **决策者：** Project Owner
- **确认记录：** 负责人在审阅包选项中选择 **A（基线通过）**。
- **背景：**
  1. 已提交 `GA-2_Complete_Review_Package.md` 与 `GA-2.0_Baseline_Package.md`（Draft）。
  2. 架构主线 v0.2 已由 GA-DEC-004 冻结。
  3. 联调级文档（Gate v0.2 / JD v0.2 / Shadow / Envelope / 标定实验）已齐。
- **决定：**
  1. 确认 **GA-2.0-Draft** 为当前工程基线（`GA-2.0_Baseline_Package.md` 状态升为 **Confirmed**，标签 `GA-2.0-Draft-20260911` 继续有效）。
  2. 确认基线不变量：治理 / 架构 / 门禁 / 运行时四类不变量继续强制。
  3. 授权进入下一设计轮（仍属 GA-2，不启动 GA-3，不授权真实写）：
     - Reasoning Engine 接口详设
     - Learning / Reflection 运行时编排
     - Shadow 试运行方案（无写）
  4. 真实平台只读连接评估 **仍须单独授权**，本决策不包含该授权。
  5. 现行门禁权威保持：`Gate_Integration_Playbook_v0.2.md` + `JD_Adapter_Interface_v0.2.md` 双字段语义。
- **允许操作：**
  - 在基线约束下继续工程设计文档、追踪矩阵更新、模拟/fixture 实验设计。
- **禁止操作：**
  - 修改 GA-1 理论基线；
  - 启动 GA-3；
  - 真实广告写操作；
  - 把 Proposed 参数表述为已验证真值；
  - 未经新决策接入真实账户只读连接。
- **影响：**
  - `GA-2.0_Baseline_Package.md` → Confirmed
  - `GA-2_Complete_Review_Package.md` 审阅结论关闭
  - 后续设计引用本基线标签
- **后续动作：** 启动 GA2-T23 / T24 / T26；保持严格记录。

## 6. GA-DEC-004：冻结 GA-2 架构主线与四项工程原则

- **日期：** 2026-09-11
- **确认日期：** 2026-09-11
- **状态：** Accepted
- **决策者：** Project Owner
- **确认记录：** 项目负责人对初步答卷五项问题逐条确认：
  1. 架构 v0.2 **可以冻结为主线**；
  2. CBA **确认为**唯一最高协调者；
  3. 第一验证场**锁定京东广告**，抖音后置；
  4. **同意**「先只读影子模式，写权限后置」为工程红线；
  5. 参数默认值**全部按 Proposed** 管理，待历史数据预标定。
- **背景：**
  1. GA-2 已由 GA-DEC-003 解锁并完成首轮综合研究。
  2. 交付 `Architecture_Overview_v0.2.md`、四类组件详设与 `GA-2_Preliminary_Answer_2026-09-11.md`。
  3. 需要将研究方向收敛为可执行工程基线，避免多路线漂移。
- **决定：**
  1. 以 `Research/GA-2/Architecture_Overview_v0.2.md` 为 **GA-2 架构主线**（状态升为 Confirmed）。
  2. 确认 CBA 为唯一最高协调者；专业引擎与 Domain Agent 均通过 CBA 协调（引擎间允许受控直连，但不得绕过门禁执行动作）。
  3. 第一验证业务域锁定 **京东广告**；抖音运营 Agent 仅保留架构占位，详设后置。
  4. 工程红线：**Shadow / 只读优先**；任何真实写操作须单独授权 + Trust Level + Self-review。
  5. 参数基因、风险阈值、Trust 权重、质量分阈值等默认数值一律 **Proposed/Pending**，禁止表述为已验证真值。
  6. 后续详设必须引用主线与本决策；偏离主线需新决策。
- **允许操作：**
  - 在主线约束下开展 Decision Packet Schema、Shadow Mode、门禁联调、京东只读契约细化、参数预标定方法设计。
- **禁止操作：**
  - 修改 GA-1 理论基线；
  - 启动 GA-3；
  - 无单独授权接入真实京东/抖音写操作或创建可执行投放脚本；
  - 把 Proposed 参数写成 Confirmed 真值。
- **影响文件：**
  - `Architecture_Overview_v0.2.md` → Confirmed（主线）
  - `GA-2_Preliminary_Answer_2026-09-11.md` 决策项关闭
  - `Engineering_TODO.md` 任务优先级重排
  - 后续 T10/T11 详设
- **后续动作：** 启动 GA2-T10 Decision Packet 与 GA2-T11 Shadow Mode 设计。

## 7. GA-DEC-003：准备进入 GA-2 工程设计（阶段解锁）

- **日期：** 2026-09-11
- **确认日期：** 2026-09-11
- **状态：** Accepted
- **决策者：** Project Owner
- **确认记录：** 用户于对话中明确授权 MiMo Desktop 执行阶段解锁并开始下一步研究。
- **背景：**
  1. `GA-1_Theory_v1.0.md` 已作为理论基线被 GA-DEC-002 确认，文档状态 Confirmed，Next Stage 标明 GA-2 Engineering Design。
  2. 交接文档 `MiMo_Desktop_GARP_Handoff_v1.0.md`（2026-09-11）声明 GA-1 理论设想完成，准备进入 GA-2 工程设计与参数预标定。
  3. 本地派生材料已按理论基线完成首轮同步（Innovation List 001–010、Glossary、Research_Context、Meeting Log）。
  4. 当前阻塞点仅在治理门禁：SPEC/ROADMAP/Engineering_TODO 仍禁止或锁定 GA-2，且无正式启动决策。
- **提议决定：**
  1. 批准 GA-1 阶段完成，输入基线锁定为 `Research/GA-1/GA-1_Theory_v1.0.md`（GA-1.0 / v1.0）。
  2. 批准启动 GA-2 Engineering Design。
  3. GA-2 第一轮范围限定为：Growth Agent 总体系统架构设计（含组件边界与理论追踪），暂不进入具体算法实现与真实 API 联调。
  4. GA-2 产出须单向派生自 GA-1 理论基线，不得反向修改 `GA-1_Theory_v1.0.md`。
  5. 确认后同步更新下列文件的锁定语句：
     - `PROJECT_SPEC.md` §3.1/§3.2（允许 GA-2 设计；仍禁止 GA-3 与无授权真实账户操作）
     - `ROADMAP.md` GA-2 状态（Locked → Active）
     - `Research/GA-2/Engineering_TODO.md`（状态与解锁记录）
     - `README.md` 阶段说明
     - `Research_Context.md` 阶段字段
- **允许操作（确认后）：**
  - 架构、组件、接口、数据与运行设计文档草稿
  - 理论到工程的追踪矩阵
  - 参数预标定方案与默认策略模板设计
  - 日志/知识库/数据结构设计
- **禁止操作（仍然有效）：**
  - 反向修改 GA-1 理论基线
  - 启动 GA-3 实验验证
  - 未经单独授权接入真实京东/抖音/ERP/财务 API 或执行真实广告操作
  - 将 GA-2 工作伪装为 GA-1 文档整理
- **影响：**
  - 治理文件与交接文档阶段表述对齐
  - 后续 GA-2 文档统一放入 `Research/GA-2/`
  - 重大架构选择继续走 `GA-DEC-NNN`
- **依赖检查：** 见 `Meeting/GA-2_Unlock_Checklist_2026-09-11.md`（结论：解锁后可启动；研究问题补录列为 GA-2 启动后首批任务）
- **生效：** 自 2026-09-11 起，GA-2 Engineering Design 进入 Active。
- **后续动作：** 按清单更新 SPEC/ROADMAP/Engineering_TODO/README/Research_Context；开始 GA-2 总体架构设计并保持严格记录。

## 8. GA-DEC-002：确立 GA-1 Theory v1.0 为最高理论依据

- **日期：** 2026-06-27
- **状态：** Accepted
- **背景：** 项目负责人提供完整的 `GA-1_Growth_Agent_Theory_v1.0.md` 作为正式理论文件。
- **决定：** 将其原文置于 `Research/GA-1/GA-1_Theory_v1.0.md`，作为后续全部 GA-1 相关工作的最高理论依据。
- **允许操作：** 格式化、保持原意的扩写、图表化和论文结构化。
- **禁止操作：** 任何下游文档、工程设计、验证结果或协作过程反向修改理论基线。
- **影响：** Glossary、Innovation List、Research Questions、Related Work、Figures 和 Paper 均为单向派生材料；冲突时修正派生材料。
- **后续版本：** 如需发展新理论，必须经项目负责人明确授权后创建新版本文件，不覆盖 v1.0。

## 9. GA-DEC-001：建立 GARP 研究仓库治理基线

- **日期：** 2026-06-27
- **状态：** Accepted
- **背景：** 项目需要可长期维护、可持续迭代的统一研究基础工程。
- **决定：** 以 `PROJECT_SPEC.md` 为最高规范，以 `Research/` 为唯一真相源，采用 GA-1 → GA-2 → GA-3 阶段路线，并对后续阶段设置正式入口门禁。
- **影响：** Paper 与 Figures 只能从 Research 派生；当前禁止 GA-2 设计、GA-3 验证和论文正文写作。
- **依据：** Project Bootstrap Specification。
- **后续动作：** 由研究负责人提供并评审 GA-1 权威理论内容。
