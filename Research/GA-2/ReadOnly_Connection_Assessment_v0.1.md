# GA-2：真实只读连接评估设计（仅评估，不真实连接）

**文档编号：** GA-2-ROCA-001  
**任务编号：** GA2-T25  
**版本：** v0.1  
**状态：** Draft（**评估设计**；不构成只读连接授权）  
**阶段：** GA-2 Engineering Design  
**输入基线：** `Research/GA-1/GA-1_Theory_v1.0.md`（GA-1.0 / v1.0，Confirmed）  
**主线架构：** `Architecture_Overview_v0.2.md`（Confirmed，GA-DEC-004）  
**工程基线：** `GA-2.0_Baseline_Package.md`（Confirmed，GA-DEC-005）  
**权威契约：** `JD_Adapter_Interface_v0.2.md`（RO-* 清单、G-01–G-09、环境策略）  
**强关联：** `Shadow_Trial_Run_Plan_v0.1.md`（档三 SRC-LIVE-RO）、`Runtime_Envelope_Selfcheck_v0.1.md`、`GA-3_Validation_Protocol_Draft_v0.1.md`（P2 前提）  
**授权依据：** GA-DEC-005 明确 **「真实平台只读连接评估仍须单独授权」**；本文在未授权前提下仅完成**评估设计**  

**作者角色：** Research Engineer 子代理（工程派生；不新增理论主张）  
**约束：** **不创建真实凭证**；**不调用真实 API**；**不配置真实端点白名单**；**不假设已获负责人授权**；一切参数为 Proposed。

---

## 0. 安全边界与范围声明（强制阅读）

### 0.1 一句话

> **本文回答「若未来授权只读连接，我们如何安全、可审计地评估与接入」；不回答「现在可以连接」。**  
> **评估设计 ≠ 授权决定 ≠ 已接入。**

### 0.2 本轮明确不做

| 项 | 说明 |
|---|---|
| 真实连接 | 不访问京准通 / 京东宙斯 / 任何真实端点 |
| 凭证 | 不创建、不示例、不落盘 AppKey / Token / Secret / Cookie |
| 端点与签名终局 | 不锁定真实 URL、OAuth、SDK 版本、签名算法 |
| 账户映射终局 | 不声称已按真实商户完成字段对齐 |
| 写能力装配 | 任何评估/联调阶段写路径必须未装配或硬失败 |
| 修改 GA-1 / PROJECT_SPEC | 纯工程派生 |
| 视为已授权 | 本文**不**触发档位切换，**不**改变 Shadow 试运行默认档 |

### 0.3 本轮明确要做

1. 论证「只读评估 ≠ 已授权连接」的治理含义。  
2. 将数据对象与 JD Adapter v0.2 **只读能力清单（RO-*）**对齐。  
3. 定义安全控制：最小权限、脱敏、审计、禁止写路径装配。  
4. 给出评估检查表与风险登记。  
5. 给出**若未来授权**的分阶段接入建议（每阶段仍需新决策）。

---

## 1. 为何「只读评估」≠「已授权连接」

### 1.1 三层区分（必须写进任何对外表述）

| 层级 | 含义 | 当前状态 | 改变该层需要什么 |
|---|---|---|---|
| **L-EVAL 评估设计** | 文档、检查表、权限矩阵、风险与熔断 | **本文（Draft）** | 负责人评审本设计 |
| **L-AUTHZ 授权决定** | 负责人书面批准「允许创建只读连接/沙箱联调」 | **未发生** | 新 `GA-DEC-NNN`（明确范围、租户、期限、负责人） |
| **L-CONNECT 已连接** | 运行时真实只读端点被装配并产生流量 | **未发生** | L-AUTHZ + 凭证合规 + 启动自检通过 |

**治理含义：**

1. 写下 RO 清单、权限矩阵、检查表，**不会**使系统获得任何平台权限。  
2. 代码中预留 `LiveTransport` 只读接口占位，**不等于**已装配；默认必须未装配或 Fail-Closed。  
3. 负责人「同意评估」只到 L-EVAL；到 L-AUTHZ 必须新决策，禁止把「看过设计」解释为「可以连」。  
4. GA-DEC-005 已明确该授权缺口；Shadow Trial 档三（SRC-LIVE-RO）同样以 L-AUTHZ 为前提。

### 1.2 只读也危险：必须评估的原因

| 看似无害 | 实际风险 |
|---|---|
| 只是拉指标 | 仍涉及账户数据出域、隐私、商业秘密、日志泄露 |
| 只是沙箱 | 沙箱凭证误用于生产；或生产凭证误入开发机 |
| 只是研究 | 研究仓库若提交明细/密钥，形成长期泄露面 |
| 只是观察 | 高频拉取触发风控/限流，影响商户正常经营 |
| 不写就行 | 只读数据若未过 BDV 直接进决策，会污染信任与知识 |

因此：**授权只读连接是数据与合规决策，不是「先连了再说」的工程默认项。**

---

## 2. 数据对象与 JD Adapter RO 清单对齐

> 资源 ID、语义、消费者以 `JD_Adapter_Interface_v0.2.md` §2.1–2.3 为权威。  
> 本文只增加：**评估阶段的权限/脱敏/频控/必要性分级**。

### 2.1 RO 能力 × 评估分级

| 能力 ID | 抽象资源 | 必要性（Proposed） | 评估阶段最小字段集（示意，非终局） | 脱敏要求 | 频控建议（Proposed） |
|---|---|---|---|---|---|
| RO-CAM-01 | Campaign/Plan 列表与状态 | **P0 必选** | plan_id, status, plan_mode, shop_ref(pseudonym) | 账户名/店主 PII 剥离 | 日级；分页 |
| RO-CAM-02 | AdUnit/Creative 摘要 | P1 可选 | unit_id, creative_id, audit_status | 素材内容默认不取 | 按需 |
| RO-MET-01 | MetricSnapshot（日内） | **P0 必选** | 花费/展现/点击/加购/成交/ROI 等口径字段 + ts | 绝对金额可分桶/哈希后再出研究树 | 小时级；限流元数据必留 |
| RO-MET-02 | MetricSnapshot（日/多日） | **P0 必选** | 7/15/30 日序列 | 同上 | 日级 |
| RO-MET-03 | IntradayCurve | **P0 必选**（FE 双时间尺度） | 分时曲线；粒度 HOUR 优先，MINUTE 按需 | 同上 | 小时级；禁止无界回放 |
| RO-ORD-01 | OrderFact（店铺侧） | P0 若做 BDV 待付款/退款 | 订单状态、实付、退款、是否推广归因 | **强脱敏**：无买家 PII；订单号假名化 | 日级；字段子集 |
| RO-INV-01 | InventoryPosition | P1 决策变量 | 可售/锁定/在途/lead_time | SKU 可映射到内部码 | 日级 |
| RO-BUD-01 | BudgetPosition | **P0 必选** | 日预算、已耗、剩余、账户余额 | 绝对值可相对化 | 日级/小时级 |
| RO-ACT-01 | BusinessEvent | P1 | 活动窗、促销阶段 | 无客户级数据 | 日历驱动 |
| RO-CMP-01 | ComplianceStatus | P0 若涉门禁解释 | 审核、违规、限流提示 | 无额外 PII | 日级 |
| RO-CAT-01 | CategoryCompetition | P2 可选 | 类目压力等弱信号 | 默认不取 | 低频 |
| RO-ACC-01 | AccountQuota | P1 | 余额/信用状态抽象 | 账户标识假名化 | 日级 |

**硬约束：**

1. `ResourceQuery.dry_run` 对只读恒为 `true`（JD v0.2 §2.2）。  
2. 平台口径与店铺口径不得在 Adapter 层直接相减得「真实 ROI」；差额由 BDV 解释（§2.3）。  
3. 只读清单是**唯一**允许的平台触达面；写动作目录不在评估范围内装配。  
4. 订单/库存/活动若来自非广告域，走可插拔 Provider，**不得**假设广告 API 一次返回全部。

### 2.2 与 Decision Packet / 运行时标签的衔接

评估期读到的数据在进入 FE/RE 前必须：

1. 带 `fetched_at`、`source`、`raw_ref`、`validation_state`；  
2. 经 BDV；`validation_state != VALIDATED` 不得进 trusted 视图；  
3. 携带 RuntimeEnvelope：`origin_env` 在授权后只读时为 LIVE（读），但 `execution_mode` 仍只能是只读/影子语义；  
4. **不得**因「只是读」而跳过 SC-A–E 启动自检。

### 2.3 不在评估范围的对象

- 任何写动作：AdjustBid / Budget / CreatePlan / Pause 等。  
- 跨租户合并读数。  
- 买家级明细、支付账号、联系方式。  
- 未在 RO-* 注册的「顺手接口」（禁止发明能力）。

---

## 3. 安全设计

### 3.1 最小权限（Least Privilege）

| 控制项 | 要求 |
|---|---|
| 能力白名单 | 运行时仅注册本阶段批准的 RO-*；未批准资源调用 → 拒绝并审计 |
| 范围收敛 | `scope` 限定 shop / 计划子集 / 时间窗；禁止全账户无界扫描 |
| 字段子集 | `fields[]` 默认最小集；扩展字段需记录必要性 |
| 环境分离 | 评估/沙箱凭证 ≠ 生产凭证；禁止复用 |
| 身份最小化 | 研究进程不持有商户超级账号；只读子账号/角色 |
| 时限 | 授权带有效期；到期自动失效，续期需新决策 |
| 网络出口 | 仅授权域名；出站拦截器 Fail-Closed；默认无白名单 |

### 3.2 脱敏与数据最小化

| 数据类 | 策略（Proposed） |
|---|---|
| PII / 买家 | **默认不取**；若订单事实必需，则假名化 + 去标识字段清单审批 |
| 账户/店铺名称 | 研究树中用 `tenant_pseudo_id` |
| 绝对金额 | 研究报告默认分桶/相对化；原始明细留在企业侧受控库 |
| 密钥/Token | 仅 CredentialProvider 内存态；禁止日志、禁止进 git |
| 研究仓库 | 只提交 Schema、Fixture、聚合结果、审计摘要；**不提交**租户明细默认树 |
| 保留期 | 评估数据保留期 Proposed：验证窗口 + 30 日，或负责人更短指令 |

### 3.3 审计（谁、何时、读了什么、为何）

每次只读连接会话必须可审计：

| 审计项 | 内容 |
|---|---|
| authz_ref | 对应 GA-DEC-NNN |
| principal | 假名化主体 ID + 角色（只读） |
| resources_queried | RO-* ID + scope 哈希 |
| n_records / bytes | 体量 |
| rate_limit_events | 限流与退避 |
| validation_summary | BDV 通过/拒绝计数 |
| envelope | env / mode / dry_run / learning_pool |
| selfcheck_ref | SC-A–E 结果 |
| export_events | 任何落盘/导出路径与脱敏级别 |
| anomaly | 非白名单调用尝试、越权字段请求 |

审计日志本身：**只追加、可校验、与业务库分离**；不得打印密钥与完整账户标识。

### 3.4 禁止写路径装配（硬红线）

即使未来 L-AUTHZ 只读通过，下列必须保持成立：

```text
1. LiveTransport 仅实例化 read 能力；write 方法缺失或硬失败包装
2. execution_mode=SHADOW_READ_ONLY 时，G-01 返回 SHADOW_WRITE_FORBIDDEN
3. 非 LIVE 或影子包强制 dry_run=true（G-07）
4. CredentialProvider 对 write scope 不提供密钥
5. DI 容器中不得存在「默认可写」的 Adapter Bean
6. 启动自检 SC-C1/C2 探针：写路径必须被拒绝且不触达网络
7. 出现平台样式写 ACK → Trip-Abort + 告警（一票否决级）
```

**只读授权永不隐含写授权。** 写路径评估/授权是另一份文档与另一个 GA-DEC。

### 3.5 运行时自检扩展（对 SRC-LIVE-RO）

在既有 SC-A–E 上增加（Proposed）：

| 检查 ID | 检查项 | 通过条件 | 失败动作 |
|---|---|---|---|
| SC-RO1 | 仅读能力面 | 容器中 write 能力未注册或 Fail-Closed | abort |
| SC-RO2 | scope 白名单 | 实际 scope ⊆ 授权 scope | 拒绝查询 + 审计 |
| SC-RO3 | 凭证角色 | 凭证声明只读 scope；无 write claim | abort |
| SC-RO4 | 端点白名单 | 目标主机在授权列表 | abort |
| SC-RO5 | 脱敏管道在位 | 原始载荷出研究边界前经过脱敏器 | abort 导出 |
| SC-RO6 | 审计 sink 可写 | 审计不可用则拒绝开始拉取 | abort |
| SC-RO7 | 限流退避 | 超限自动退避；禁止硬闯 | 冻结本会话 |
| SC-RO8 | BDV 门 | raw 指标不得直通 FE/RE | abort 决策链路 |

---

## 4. 评估检查表（供负责人 / 安全评审勾选）

> 状态建议：`N/A | Open | Pass | Fail`。任一 **Hard** 项 Fail → 不得进入 L-AUTHZ。

### 4.1 治理与授权

| # | 检查项 | 级别 | 状态 |
|---|---|---|---|
| C1 | 明确本次评估只到 L-EVAL，未默认 L-AUTHZ | Hard | |
| C2 | 范围：租户、shop、时间窗、RO-* 子集已书面化 | Hard | |
| C3 | 授权期限与负责人已指定 | Hard | |
| C4 | 与 GA-3 协议 P2 的依赖关系已说明 | Soft | |
| C5 | 退出/吊销流程已定义 | Hard | |

### 4.2 权限与凭证

| # | 检查项 | 级别 | 状态 |
|---|---|---|---|
| C6 | 只读子账号/角色；无 write scope | Hard | |
| C7 | 凭证不进 git / 日志 / 截图 | Hard | |
| C8 | 沙箱与生产凭证物理/逻辑分离 | Hard | |
| C9 | CredentialProvider 空对象默认拒绝 | Hard | |
| C10 | 轮换与吊销演练文档化 | Soft | |

### 4.3 数据与脱敏

| # | 检查项 | 级别 | 状态 |
|---|---|---|---|
| C11 | 字段最小集评审通过 | Hard | |
| C12 | PII/买家字段默认排除或已假名化 | Hard | |
| C13 | 研究仓库不提交租户明细 | Hard | |
| C14 | 保留期与删除流程明确 | Soft | |
| C15 | BDV 校验规则对真实口径已映射草案 | Hard | |

### 4.4 技术与运行时

| # | 检查项 | 级别 | 状态 |
|---|---|---|---|
| C16 | LiveTransport 仅读装配；写硬失败 | Hard | |
| C17 | SC-RO1…RO8 设计评审通过 | Hard | |
| C18 | 网络出口白名单 Fail-Closed | Hard | |
| C19 | 限流/重试/退避策略明确 | Soft | |
| C20 | 审计 sink 与留存策略明确 | Hard | |
| C21 | 故障演练：越权、超限、坏数据、审计中断 | Hard | |

### 4.5 与影子/验证的关系

| # | 检查项 | 级别 | 状态 |
|---|---|---|---|
| C22 | 只读数据不直接升 live Trust | Hard | |
| C23 | 不把只读联调成功表述为「系统已验证」 | Hard | |
| C24 | 档位切换条件（Trial §4.2）已引用 | Soft | |
| C25 | GA-3 P2 使用 SRC-LIVE-RO 的前提已单列决策 | Hard | |

---

## 5. 风险登记

| 风险 ID | 风险 | 影响 | 缓解 | 残余 |
|---|---|---|---|---|
| RO-R01 | 凭证泄露（repo/日志/截图） | 账户数据全量暴露 | 禁止落盘；扫描钩子；轮换 | 中（人为失误） |
| RO-R02 | 只读凭证被误用于写 | 未授权投放 | scope 无 write；写路径硬失败；SC-RO3 | 低（多层） |
| RO-R03 | 沙箱/生产混淆 | 错误结论或误操作 | 环境标签 + 启动自检 | 低 |
| RO-R04 | 高频拉取触发平台风控 | 影响商户经营 | 频控、退避、日切片上限 | 中 |
| RO-R05 | 原始数据含 PII 进研究树 | 合规/隐私事件 | 脱敏闸 SC-RO5；导出审批 | 中 |
| RO-R06 | BDV 未就绪导致脏数据进 FE | 错误决策与知识污染 | SC-RO8；validation_state 门 | 中 |
| RO-R07 | 「评估通过」被口头解释为已授权 | 治理失守 | L-EVAL/L-AUTHZ/L-CONNECT 三分；新 DEC | 中（沟通） |
| RO-R08 | 审计不可用仍拉取 | 不可追责 | SC-RO6 Fail-Closed | 低 |
| RO-R09 | 字段超集导致数据最小化失败 | 过度采集 | fields[] 白名单 + 评审 | 低 |
| RO-R10 | 供应商侧变更导致契约漂移 | 静默错误 | raw_ref + 版本指纹 + 告警 | 中 |
| RO-R11 | 单点研究者持有凭证 | 人员风险 | 角色账号、可吊销、双人知情 | 中 |
| RO-R12 | 只读结果外传为「已验证 ROI」 | 决策误导 | 报告 explicit_non_claim；VA-E02 | 中 |

---

## 6. 若未来授权：建议分阶段接入（每阶段仍需新决策）

```text
R0  评估设计完成（本文）→ 负责人评审
R1  权限与合规预审（无连接）
      · 字段/脱敏/保留期/责任人
      · 产出：数据保护说明 + 权限矩阵
R2  L-AUTHZ：新 GA-DEC 批准「只读沙箱连接」
      · 范围、期限、shop、RO-* 子集、审计要求
R3  技术就绪
      · CredentialProvider（只读 scope）
      · SC-RO1…RO8 全绿（对沙箱）
      · 演练：越权/限流/写探针/审计中断
R4  受限联调（沙箱或最小 shop）
      · 仅 RO-CAM/MET/BUD 子集；短窗口
      · 产出：RO Connectivity Report（聚合，无明细入库）
R5  评估扩面
      · 增加 RO-ORD/INV 等 Provider；BDV 对齐
      · 仍无写；不升 live Trust
R6  并入 Shadow Trial 档三 / GA-3 P2
      · 须引用已存在的 R2 决策；范围未覆盖则新 DEC
R7  （范围外）任何写路径 / Live-Write
      · 独立文档 + 独立 GA-DEC + Trust 达标 + 人工否决保留
```

**每阶段退出条件（Proposed）：**

| 阶段 | 退出条件 |
|---|---|
| R1 | 检查表 C1–C15 无 Hard Fail |
| R2 | GA-DEC Accepted；范围清单附件化 |
| R3 | SC-RO 全绿；写探针拒绝且零网络写 |
| R4 | 审计完整；零 PII 泄露事件；限流稳定 |
| R5 | BDV 对真实口径映射评审通过 |
| R6 | Trial/GA-3 门禁同时满足 |

**降级/吊销：** 任一 Hard 检查失败、审计中断、凭证疑似泄露、负责人指令 → 立即吊销凭证并冻结会话；恢复须重新 R3。

---

## 7. 产出物模板（仅骨架，不填写真实账户）

### 7.1 只读连接评估报告（授权后才写）

```markdown
# 真实只读连接评估报告（模板）

- report_id: RO-CONN-RPT-{yyyymmdd}-{seq}
- authz_ref: GA-DEC-____
- scope: { tenant_pseudo_id, shops[], resources[], time_range }
- status: SANDBOX_ONLY | STAGING_READ
- explicit_non_claim: 非生产写；未授权自动执行；未证明 live 最优

## 1. 授权范围与期限
## 2. 检查表结果（C1–C25）
## 3. 自检记录（SC-A–E + SC-RO1…RO8）
## 4. 拉取统计（资源、条数、限流、错误）
## 5. BDV 校验摘要
## 6. 脱敏与导出审计
## 7. 事件与熔断
## 8. 结论：可维持 / 需收窄 / 建议吊销
## 9. 附件（审计摘要、配置指纹；无密钥）
```

### 7.2 权限矩阵（授权附件）

| RO-* | 字段子集 | 时间粒度 | 频控 | 脱敏 | 是否进入研究树 |
|---|---|---|---|---|---|
| … | … | … | … | … | … |

---

## 8. 待决问题

| ID | 问题 | 建议 | 阻塞 |
|---|---|---|---|
| RO-Q1 | 平台只读 API 的官方限流与合规条款？ | 授权前由负责人/法务确认；本文不假设 | R1 |
| RO-Q2 | 企业侧订单 Provider 是否必须？ | 若验证含 BDV 待付款/退款则必须；否则 P1 | R5 |
| RO-Q3 | 绝对金额是否允许离开企业网？ | 默认否；仅聚合/相对化出域 | R1 |
| RO-Q4 | 审计保留期？ | Proposed：授权期 + 90 日或依法规取严 | R2 |
| RO-Q5 | 是否允许第三方评测接触只读数据？ | 默认否；若允许须新 DEC + 脱敏加严 | R2 |
| RO-Q6 | 抖音域是否共用本文框架？ | 框架共用；清单与合规另文 | 后置 |

---

## 9. 与既有文档的接口

| 文档 | 本文关系 |
|---|---|
| JD_Adapter_Interface v0.2 | RO-* 权威清单；禁止发明能力；环境策略 |
| Shadow_Trial_Run_Plan | 档三 SRC-LIVE-RO 准入；不代替其授权 |
| Runtime_Envelope_Selfcheck | SC-A–E 基座；本文增 SC-RO* |
| GA-3 Validation Protocol Draft | P2 依赖本评估与授权；无授权则降级历史证据 |
| Gate_Integration_Playbook v0.2 | 写硬拒绝语义（即使只读评估期） |
| Decision_Log | 任何 L-AUTHZ 必须新 GA-DEC |

---

## 10. 变更记录

| 日期 | 版本 | 变更 | 依据 |
|---|---|---|---|
| 2026-09-14 | v0.1 | 首次建立真实只读连接评估设计：评估≠授权、RO 清单对齐、最小权限/脱敏/审计/禁写装配、检查表与风险、分阶段接入建议 | GA2-T25；GA-DEC-005；JD Adapter v0.2；Shadow Trial；Runtime Envelope |

---

**Document Status:** Draft  
**Next Review:** Project Owner /（如涉及数据合规）安全或法务评审  
**Explicit Non-claim:** 本文**未授权**任何真实连接；**未创建**凭证；**未调用**真实 API；**未装配**写路径；**未修改** GA-1 / PROJECT_SPEC。评估完成**不等于**授权；授权完成**不等于**可写。一切参数为 **Proposed**。
