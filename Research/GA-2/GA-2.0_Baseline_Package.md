# GA-2.0 工程基线打包说明

**文档编号：** GA-2-BASELINE-001  
**版本：** v0.1  
**状态：** **Confirmed**（GA-DEC-005，2026-09-11）  
**日期：** 2026-09-11  
**依据：** GA-DEC-003（解锁）+ GA-DEC-004（主线冻结）+ GA-DEC-005（基线确认）  
**输入理论基线：** `Research/GA-1/GA-1_Theory_v1.0.md`（GA-1.0，Confirmed）  
**基线标签：** `GA-2.0-Draft-20260911`  
**负责人结论：** 审阅选项 A——基线通过  

---

## 1. 基线定位

本包是 **GA-2 Engineering Design 的第一份可审阅工程基线草稿**，不是代码实现，也不是 GA-3 验证结果。

目标：

> 将 GA-1 理论收敛为可追踪、可门禁、可影子运行、可继续实现的工程设计集合。

---

## 2. 基线清单（权威阅读顺序）

| 顺序 | 文档 | 状态 | 角色 |
|---|---|---|---|
| 0 | `GA-2_Complete_Review_Package.md` | Review Closed | **审阅入口总览** |
| 1 | `Architecture_Overview_v0.2.md` | **Confirmed** | 架构主线 |
| 2 | `Theory_Engineering_Trace.md` | Draft | 理论→工程追踪 |
| 3 | `Decision_Packet_Schema_v0.1.md` | Draft | 成长最小原子 |
| 4 | `Forecast_Engine_Interface_v0.1.md` | Draft | 预测契约 |
| 5 | `Reasoning_Engine_Interface_v0.1.md` | Draft | **基线后扩展** 推理契约与场景骨架 |
| 6 | `Memory_Knowledge_Boundary_v0.1.md` | Draft | 记忆/知识边界 |
| 7 | `Risk_Trust_SelfReview_v0.1.md` | Draft | 风控信任审批 |
| 8 | `Gate_Integration_Playbook_v0.2.md` | Draft | 门禁联调（现行） |
| 9 | `JD_Adapter_Interface_v0.2.md` | Draft | 京东接入（现行） |
| 10 | `Shadow_Mode_Design_v0.1.md` | Draft | 影子运行 |
| 11 | `Shadow_Trial_Run_Plan_v0.1.md` | Draft | **基线后扩展** 无写试运行计划 |
| 12 | `Runtime_Envelope_Selfcheck_v0.1.md` | Draft | 运行时防误装配 |
| 13 | `Learning_Reflection_Runtime_v0.1.md` | Draft | **基线后扩展** 回路 B 编排 |
| 14 | `Parameter_Genome_Templates_v0.1.md` | Draft | 参数基因 |
| 15 | `Threshold_Calibration_Method_v0.1.md` | Draft | 阈值标定方法 |
| 16 | `Precalibration_Experiment_Design_v0.1.md` | Draft | 预标定实验 |
| 17 | `Fixture_Migration_Guide_v0.1.md` | Draft | 样例迁移 |
| 18 | `Cross_Document_Consistency_Audit_v0.1.md` | Draft + §8 Closed | 终审；C-01–C-08 已关闭 |
| 19 | `Module_Skeleton_Design_v0.1.md` | Draft | 实现骨架（含 CBA/OFG Port） |
| 20 | `GA-3_Validation_Protocol_Draft_v0.1.md` | Draft | 验证协议草案（未启动 GA-3） |
| 21 | `ReadOnly_Connection_Assessment_v0.1.md` | Draft | 只读评估设计（未授权连接） |
| 22 | `GA-2_Completeness_Audit_v0.1.md` | Draft | 七维完备性审计 |
| 23 | `CBA_OFG_Interface_v0.1.md` | Draft | CBA/OFG 接口详设 |
| 24 | `Error_Reason_Code_Catalog_v0.1.md` | Draft | 全局错误码目录 |

**历史承接（非现行权威）：**  
`Architecture_Overview_v0.1.md`、`JD_Adapter_Interface_v0.1.md`、`Gate_Integration_Playbook_v0.1.md` —— 仅作演进记录，现行语义以 v0.2 及双字段模型为准。

**基线后扩展说明：** T23/T24/T26/T27/T28/T29/T25 在 GA-DEC-005/006 授权轮次产出，不改变 GA-2.0-Draft 已确认的四类不变量；实现前建议关闭审计剩余中低项（GA2-T30）。

---

## 3. 基线不变量（实现前必须成立）

### 3.1 治理不变量

1. 不修改 GA-1 理论基线。  
2. 不接真实广告写操作，除非新决策单独授权。  
3. 全部阈值/默认参数 = Proposed，禁止当已验证真值。  

### 3.2 架构不变量

1. CBA 唯一最高协调者。  
2. 四回路：决策 / 蒸馏 / 知识 / 信任。  
3. Memory 不得直接改策略。  

### 3.3 门禁不变量

1. 可执行判定：`lifecycle_status ∈ {Self-reviewed, Executed}` ∧ `review_result ∈ {APPROVE, NO_ACTION_APPROVE}`。  
2. `review_result` 仅 SRA 可写。  
3. Risk 硬红线优先；Shadow 写路径硬拒绝。  
4. `NO_ACTION` 必须成包并过 SRA。  

### 3.4 运行时不变量

1. `RuntimeEnvelope` 强制透传；默认只读/影子档。  
2. `env≠LIVE` 不得计入 live Trust，不得自动晋升企业规则。  
3. 启动自检失败必须硬失败，禁止静默降级到写通道。  

---

## 4. 基线已覆盖 / 未覆盖

### 4.1 已覆盖

- 总体架构与组件边界  
- Decision Packet 契约与样例  
- Forecast 对象目录  
- Memory/Knowledge 演化状态机  
- Risk/Trust/Self-review 与门禁联调  
- 京东只读/写抽象契约（v0.2）  
- Shadow Mode 与 Runtime Envelope  
- 参数基因与阈值标定方法/实验设计  
- Fixture 迁移  

### 4.2 明确未覆盖（下一基线）

- Reasoning Engine 接口详设  
- Learning/Reflection 运行时编排与任务队列  
- 真实平台只读连接评估（需授权）  
- 可运行代码 / 模型训练  
- 抖音 Domain 详设  
- GA-3 验证协议全文  

---

## 5. 建议的实现前检查清单（负责人可用）

- [ ] 已阅读 Complete Review Package  
- [ ] 确认 Architecture v0.2 主线仍有效  
- [ ] 确认双字段语义（GIP v0.2 + JD v0.2）为唯一现行门禁语义  
- [ ] 确认 Shadow 只读红线  
- [ ] 确认不伪造历史标定结果  
- [ ] 确认实现阶段仍禁止真实写，除非新 GA-DEC  

---

## 6. 版本与后续

| 项 | 值 |
|---|---|
| 本基线标签 | GA-2.0-Draft-20260911（**标签名含 Draft 不等于文档未确认**） |
| 确认决策 | **GA-DEC-005**（Accepted，2026-09-11；负责人选项 A 基线通过） |
| 确认后授权 | Reasoning 接口、Learning/Reflection 编排、Shadow 试运行（仍属 GA-2；不启动 GA-3、不授权真实写） |
| 后续收敛 | 外部审计后进入 GA-2 收敛轮；权威清单见 `GA-2_Release_Manifest_v0.1.md`（Draft） |
| RC 条件 | P0 整改关闭 + 独立复核 + 测试证据绑定 commit，才可审议 GA-2.0-RC |

---

**Document Status:** Confirmed（与文首一致；Authorizing Decision = GA-DEC-005）  
**Lifecycle Status:** Confirmed  
**Review Result:** Approved（负责人选项 A）  
**Authoritative For:** GA-2.0-Draft 工程基线清单与四类不变量（标签 `GA-2.0-Draft-20260911`）  
**Owner Action:** 无需再次审阅基线通过性；后续动作是监督 GA2-R01…R15 整改关闭与 RC 审议。  
**2026-09-15 治理清理：** 删除文末过期 Draft/待审标记，与 GA-DEC-005 Confirmed 对齐。
