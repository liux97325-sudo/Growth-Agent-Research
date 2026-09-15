# GA-3 协议治理边界决策草案（验证接口预研）

**文档编号：** GA-MEET-GA3BOUND-001  
**关联决策：** GA-DEC-007（**Proposed**，待负责人确认）  
**状态：** Draft / Proposed（**不构成已生效授权**）  
**日期：** 2026-09-15  
**提案依据：** 外部审计 `GA-2_Modification_and_Design_Recommendations_2026-09-15.md` §13；现行 `PROJECT_SPEC.md` §3.2 与 `GA-3_Validation_Protocol_Draft_v0.1.md` 的边界张力  
**推荐方案：** **方案 A**  
**作者角色：** Research Engineer 子代理（治理派生；不修改 GA-1；不启动 GA-3）  
**硬约束：** 本草案在负责人 Accept 前 **不生效**；不得把 Proposed 写成 Confirmed；不得据本草案启动任何实验或真实连接。

---

## 1. 背景与冲突

1. `PROJECT_SPEC.md` 长期禁止「启动 GA-3 实验设计或验证」。  
2. `GA-3_Validation_Protocol_Draft_v0.1.md`（GA2-T29）已包含验证问题映射、指标族、对照设计、样本门槛与预注册模板——属于**设计预研**，但字面易被读成“已启动 GA-3”。  
3. 审计要求：在 GA-2 收敛期，工程阶段需要预先设计可观测性与可验证接口；同时必须用正式治理文本消除与 SPEC 的冲突。

---

## 2. 两案对照

| 维度 | 方案 A：允许验证接口预研（推荐） | 方案 B：保持现行禁止范围 |
|---|---|---|
| 对 GA-3 协议草案的处理 | 保留为 GA-2 内的**预注册契约/接口预研材料** | 标为 `Non-authoritative Working Note`，移出权威基线与 TODO Done |
| 允许工作 | 验证接口、日志字段、指标定义、预注册模板、Fixture 可观测字段设计 | 仅文档归档与状态降级 |
| 禁止工作 | 实验执行、真实数据接入、产生验证结论、启动 GA-3 阶段 | 同左，且暂停一切与验证接口相关的设计推进 |
| 统计门槛状态 | 一律保持 **Proposed** | 保持 Draft/无效 |
| 正式 GA-3 | 须 GA-3 解锁决策 + 协议重新评审确认 | 解锁后再迁移修订 |
| 工程影响 | 可提前对齐可观测性与证据字段，降低后续返工 | 可能返工 GA-2 已交付的协议草案结构 |
| 治理成本 | 新增一条明确 GA-DEC | 须从基线清单与 TODO 中剥离 T29 产物 |

---

## 3. 推荐决定（方案 A，待负责人 Accept）

**提议：** 采纳方案 A。在 GA-2 范围内允许「验证接口预研」；继续禁止「GA-3 实验执行」。

### 3.1 允许（在 GA-2 Active 且无真实连接前提下）

1. 设计验证**可观测接口**：事件字段、证据引用、日志 schema、决策包与回执的可追踪锚点。  
2. 维护与修订 `GA-3_Validation_Protocol_Draft_v0.1.md` 作为**预注册契约草稿**（明确标注非实验启动）。  
3. 设计**预注册模板**（问题—对照—主指标—熔断—伦理边界）与报告骨架。  
4. 将 Fixture / Shadow 轨迹设计为可被未来验证复用的证据格式（仍不得接触真实广告数据）。  
5. 在文档中引用 VQ/指标定义，但必须标注 **Proposed**。

### 3.2 禁止（仍然有效，且本决策不得被解释为例外）

1. 启动任何 GA-3 实验臂、样本采集、真实数据接入或验证结论生产。  
2. 将 `Research/GA-3/Validation_TODO.md` 从 Locked 解开。  
3. 真实京东/抖音/ERP 只读或写连接（须单独授权）。  
4. 真实广告写操作。  
5. 把样本量、阈值、窗口、效应量门槛写成 Confirmed / 已验证。  
6. 修改 GA-1 理论基线。  
7. 把「验证接口预研」表述为「已完成 GA-3」或「GA-3 进行中」。

### 3.3 正式 GA-3 入口（未来，非本决策）

进入 GA-3 仍须：

1. GA-2 P0 整改关闭且具备可恢复 git 基线与测试证据；  
2. 新的 GA-DEC 单独解锁 GA-3；  
3. 对协议全文重新评审并升状态；  
4. 数据、伦理、资源与平台授权齐备。

---

## 4. 建议写入 Decision_Log 的条目骨架

> 以下为待确认文本；Accept 后由负责人授权将状态改为 Accepted，并回填确认日期与决策者确认记录。

```text
GA-DEC-007：明确 GA-3 协议与验证接口预研的治理边界
- 日期：2026-09-15
- 状态：Proposed（待负责人）
- 推荐：方案 A
- 决定要点：
  1. 允许在 GA-2 内设计验证接口、日志字段与预注册模板；
  2. 禁止启动 GA-3 实验、接入真实验证数据或产生验证结论；
  3. 全部统计门槛保持 Proposed；
  4. GA-3_Validation_Protocol_Draft_v0.1 降格为预注册契约草稿，非实验启动证明；
  5. 正式 GA-3 协议须在 GA-3 解锁后重新评审确认。
- 编号说明：Engineering_TODO 中 GA2-T33c（Brain 基座确认）原占位“待 GA-DEC-007”
  已因本决策占用 007；Brain 基座确认决策请改用 GA-DEC-008 或更高编号。
```

---

## 5. 若负责人选择方案 B

1. 将 `GA-3_Validation_Protocol_Draft_v0.1.md` 文首状态改为 `Non-authoritative Working Note`。  
2. 从 `GA-2.0_Baseline_Package.md` 权威阅读清单与 Release Manifest authoritative_docs 中移除或降级。  
3. 将 GA2-T29 状态从 Done (Draft) 改为 `Superseded / Non-authoritative`。  
4. 同步收窄 `PROJECT_SPEC.md` §3.1/§3.2 表述，明确禁止任何验证接口预研。  
5. 登记新 Decision_Log 条目（替代本草案）。

---

## 6. 对现行文件的影响（仅在 Accept 后执行）

| 文件 | 预期影响 |
|---|---|
| `Meeting/Decision_Log.md` | GA-DEC-007：Proposed → Accepted |
| `PROJECT_SPEC.md` | §3.1/§3.2 增加验证接口预研允许项；保留 GA-3 执行禁令（本轮已按草案预同步表述，**效力以 Accept 为准**） |
| `Research_Context.md` | 同步 GA-2 Conditional 与 GA-DEC-007 状态 |
| `Research/GA-3/Validation_TODO.md` | 保持 Locked，不修改 |
| `GA-3_Validation_Protocol_Draft_v0.1.md` | 保持 Draft；可补“预注册契约、非启动”元数据（非必须） |

---

## 7. 请负责人裁决

- [ ] **接受方案 A**（推荐）→ GA-DEC-007 = Accepted  
- [ ] 选择方案 B → 按 §5 执行降级  
- [ ] 修改后重提（请注明修改点）

---

**Document Status:** Draft  
**Explicit Non-Claim:** 本文件不授权实验、不授权真实连接、不证明任何 Proposed 统计门槛有效。
