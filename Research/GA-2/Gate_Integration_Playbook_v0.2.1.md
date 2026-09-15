# GA-2：门禁联调手册 v0.2.1（增补与修正）

**文档编号：** GA-2-GATE-002  
**版本：** v0.2.1  
**状态：** Draft（**现行权威增量**）  
**阶段：** GA-2 Engineering Design  
**基线：** `Gate_Integration_Playbook_v0.2.md`（Draft，GA2-T19）  
**对齐契约：** `Decision_Packet_Schema_v0.2.1.md`（DPK-I9…I12 / decision_outcome）  
**审计依据：** `GA-2_Modification_and_Design_Recommendations_2026-09-15.md` §5、§14（GA2-R03/R04/R05）  
**约束：** 不改 GA-1；不改 PROJECT_SPEC；不写真实 API；阈值一律 **Proposed**。

---

## 0. 效力、取代与阅读方式

### 0.1 本文件是什么

本文件是 **GIP v0.2 的权威增补节**，不是全文重写。  
实现时：**v0.2 全文继承**，但下列章节被本文件**显式取代或收紧**：

| v0.2 章节 | v0.2.1 处理 |
|---|---|
| §1.1 双字段可执行判定（混用 `APPROVE`/`NO_ACTION_APPROVE` 为同一可执行集） | **取代** → 本文 §2 双谓词 + §3 `decision_outcome` |
| §4.1 G-01 谓词（`review_result ∈ {APPROVE, NO_ACTION_APPROVE}` 一律可执行） | **取代** → 按动作形态分流 |
| §4.2 组合裁决表行 #1 / #12 / #20 | **收紧** → 本文 §5 补丁表 |
| §9.1 检查清单 G-01 | **取代** → 本文 §7 |
| §10.2 GIP-Q9（Executed 重入） | **部分关闭** → 本文 §6 Executed 重试约束 |

未列出的 v0.2 内容（流水线图、动作×门禁矩阵、ESC-01…10、失败模式、审计字段、Trust 矩阵等）**继续有效**。

### 0.2 为什么必须改

审计 GA2-R03/R04 指出：若 `NO_ACTION_APPROVE` 与 `APPROVE` 共用“可执行”布尔，则：

1. 副作用动作可被 `NO_ACTION_APPROVE` 放行；  
2. NO_ACTION 包的 `allowed=true` 可能被误读为允许 Adapter 写；  
3. REJECT/HOLD 路径可能仍产出“已批准”合成回执。

---

## 1. 冻结执行顺序：G-00 → G-01 … G-09

> **顺序必须固定，不可重排、不可并行短路跳过 Schema。**

```text
G-00  Schema + Envelope Consistency
  → G-01  Lifecycle / Review / Action semantic match
  → G-02  Trust capability
  → G-03  Risk hard block
  → G-04  State drift / staleness
  → G-05  Idempotency
  → G-06  Inventory / Budget revalidation
  → G-07  Runtime mode / dry_run / transport authorization
  → G-08  Frequency and response-window constraint
  → G-09  Plan-mode / action compatibility
  → 终点 A：Adapter submission（仅 PLATFORM_WRITE）
  → 终点 B：synthetic NO_ACTION receipt（仅 SYNTHETIC_NO_ACTION）
```

### 1.1 顺序不变量

| # | 不变量 |
|---|---|
| S1 | Schema/Envelope 不合法时**不得**进入业务门禁（G-00 先于一切） |
| S2 | Shadow / 非 LIVE 写拒绝应早于任何可能产生副作用的 Adapter 调用 |
| S3 | 幂等（G-05）必须在平台提交前 |
| S4 | 最新库存、预算与计划状态（G-04/G-06）必须在写前重验 |
| S5 | NO_ACTION **不绕过 SRA**，但**绕过平台写** |
| S6 | 任一门禁失败即停止后续门禁评估，返回首个 `failed_gate_id`（可选继续跑只读诊断门禁，但不得提交） |

### 1.2 各门禁职责摘要（相对 v0.2 的澄清）

| 门禁 | 输入关注点 | 失败时 `decision_outcome` |
|---|---|---|
| **G-00** | JSON Schema；`schema_version` 支持；request/packet/envelope 三方 `envelope_id` 一致；`tenant_id`/`shop_id` 非空；枚举合法 | `REJECT` |
| **G-01** | 生命周期；**动作形态 × review_result**（DPK-I9…I12）；SRA issuer；Shadow 写 | `REJECT` |
| **G-02** | `trust_actual >= trust_required`（动作类能力域） | `REJECT` 或 `HOLD` |
| **G-03** | `risk.hard_block` 空；`risk_level≠R4`；constraints 满足 | `REJECT` |
| **G-04** | 状态未过期；无 plan/state drift | `REJECT` |
| **G-05** | 幂等键；内容哈希 | 幂等命中 → 原回执语义；冲突 → `REJECT` |
| **G-06** | 库存/预算再验证 | `REJECT` |
| **G-07** | env/mode/adapter_runtime/execution_mode/dry_run 组合 | `REJECT` |
| **G-08** | 频率与响应窗口 | `REJECT` |
| **G-09** | plan_mode × action 兼容 | `REJECT` |

> G-00 为 **v0.2.1 显式编号**（v0.2 中 Schema/Envelope 检查分散在 G-01/G-07）。编号 G-00 不改变“G-01…G-09 集合不变”的历史承诺，只把前置一致性检查**固定位次**。

---

## 2. 双谓词（普通动作 vs NO_ACTION）

> **禁止**用单一 `allowed: bool` 混用两条路径。

### 2.1 普通动作可执行谓词

```text
non_no_action_executable(packet, request, envelope) :=
    packet.schema_valid                          # G-00
    AND NOT is_no_action(packet)                 # DPK-I9
    AND packet.status == Self-reviewed           # 受控重试分支见 §6
    AND packet.review.review_result == APPROVE   # DPK-I11：仅 APPROVE
    AND packet.review.issuer_type == SRA
    AND packet.execution_mode == LIVE            # 本轮 FIXTURE/SIMULATION 下由 envelope 矩阵约束
    AND envelope.env 与 packet.execution_mode 一致
    AND envelope 允许该写路径（非 Shadow 写）
    AND request.dry_run == false                 # 仅 LIVE_WRITE 语义；本轮强制 dry_run=true ⇒ 不得 PLATFORM_WRITE
    AND packet.risk.hard_block is empty
    AND trust_actual >= trust_required
    AND state_not_stale
    AND no_state_drift
    AND idempotency_not_conflicting
    AND frequency_window_ok
    AND plan_mode_action_compatible
    AND G-00…G-09 全部通过
```

**本轮（GA-2 Conditional）现实约束：**  
`execution_mode` 仅允许 `SHADOW_READ_ONLY`，因此 `non_no_action_executable` 在当前 envelope 下**恒不得**映射到真实平台写；FIXTURE/SIMULATION 仅允许受控模拟提交，且必须标记 `SIMULATED`。

### 2.2 NO_ACTION 可观察谓词

```text
no_action_observable(packet) :=
    packet.schema_valid
    AND is_no_action(packet)                          # DPK-I9：非空且全 NO_ACTION
    AND packet.status == Self-reviewed
    AND packet.review.review_result == NO_ACTION_APPROVE   # DPK-I10
    AND packet.review.issuer_type == SRA
    AND packet.no_action_reason is not empty
    AND (
          packet.risk.hard_block is empty
          OR hard_block 已显式记录为“维持现状之原因”
        )
    # 不要求 G-02…G-09 的平台写相关项；
    # 不创建任何 Transport 写调用
```

### 2.3 谓词与 outcome 映射

| 谓词结果 | `decision_outcome` | 下一步 |
|---|---|---|
| `non_no_action_executable` | `PLATFORM_WRITE` | Adapter 提交（本轮为受控模拟/Fixture） |
| `no_action_observable` | `SYNTHETIC_NO_ACTION` | 合成 `NOT_APPLICABLE_NO_ACTION` 回执 → 观察 |
| 均不满足且 review=`REJECT`/语义非法/门禁失败 | `REJECT` | 拒绝；审计 |
| review=`HOLD` 或条件性等待 | `HOLD` | 挂起 |
| review=`ESCALATE_HUMAN` | `ESCALATE` | 人类审批 |

### 2.4 禁止单一 `allowed` 布尔

| 禁止写法 | 问题 | 替代 |
|---|---|---|
| `allowed = lifecycle_ok and review_ok` | 将 `NO_ACTION_APPROVE` 与 `APPROVE` 混成“可执行” | 拆双谓词 + `decision_outcome` |
| `if allowed: adapter.write(...)` | NO_ACTION 的 allowed 会导致误写 | `if outcome == PLATFORM_WRITE: write`；`if outcome == SYNTHETIC_NO_ACTION: synthetic_receipt` |
| 把 Shadow 的“可观察”写成 `allowed=true` | 与 DPK-I5 冲突 | Shadow 写路径恒 `REJECT` / 不装配 |

**返回载荷契约（与 DPK v0.2.1 §3.3 一致）：**

```text
GateDecision {
  decision_outcome,
  passed_gate_ids,
  failed_gate_id,
  reason_codes,
  evidence_refs
}
```

---

## 3. 动作—审批对应（与 DPK I9–I12 对齐）

| 动作形态 | 唯一允许 review_result | Gate 行为 | Receipt |
|---|---|---|---|
| 非空且全 NO_ACTION | `NO_ACTION_APPROVE` | `no_action_observable` → `SYNTHETIC_NO_ACTION` | `NOT_APPLICABLE_NO_ACTION`，`synthetic=true` |
| 至少一个非 NO_ACTION | 可执行时仅 `APPROVE` | `non_no_action_executable` → `PLATFORM_WRITE` 或门禁失败 | 平台/`SIMULATED`；禁止 NO_ACTION 合成 |
| 任意 | `REVISE`/`HOLD`/`REJECT`/`ESCALATE_HUMAN` | 不进入写/合成批准路径 | 不得 approved 回执 |

**G-01 伪逻辑（取代 v0.2 §3.2）：**

```text
G-01(packet, request):
  if not is_no_action(packet) and request.intends_no_action_synthetic:
      return REJECT(GATE-1006)            # 形态与请求不一致
  if is_no_action(packet):
      if packet.review_result != NO_ACTION_APPROVE:
          return REJECT(GATE-1007)
      if empty(packet.no_action_reason):
          return REJECT(GATE-1009)
      return PASS_TO_NO_ACTION_PATH       # 不进入平台写 G-02…G-09 写分支
  else:
      if packet.review_result != APPROVE:
          return REJECT(GATE-1006)        # 含 NO_ACTION_APPROVE 串用
      if packet.execution_mode == SHADOW_READ_ONLY and intends_platform_write:
          return REJECT(SHADOW_WRITE_FORBIDDEN)
      return PASS_TO_WRITE_GATES          # 继续 G-02…G-09
```

---

## 4. Envelope 与 G-00/G-07 衔接摘要

本文件不重写 Runtime Envelope 全文；门禁侧必须：

1. Request 内 envelope 与 Transport 初始化 envelope **同 ID、同哈希**，否则 G-00 失败；  
2. Packet 的 `execution_mode`/`packet_kind` 与 envelope **双向一致**；  
3. 非 LIVE 组合不得映射 `PLATFORM_WRITE`；  
4. 任何中间层不得重新生成 envelope 洗掉 `source_env`。

---

## 5. 组合裁决表补丁（取代 v0.2 关键行）

| # | 动作形态 | LS | RR | v0.2 行为 | **v0.2.1 行为** |
|---|---|---|---|---|---|
| 1′ | 至少一个副作用 | Self-reviewed | APPROVE | 执行 G-01–G-09 | **不变**：全检 → `PLATFORM_WRITE` 或失败 |
| 12′ | 全 NO_ACTION | Self-reviewed | NO_ACTION_APPROVE | 合成回执 | **不变并强化**：`SYNTHETIC_NO_ACTION`；禁止 Transport 写 |
| 12a | 全 NO_ACTION | Self-reviewed | APPROVE | （未单列） | **`REJECT` `GATE-1007`** |
| 12b | 至少一个副作用 | Self-reviewed | NO_ACTION_APPROVE | （易被 §1.1 放行） | **`REJECT` `GATE-1006`/`GATE-2008`** |
| 12c | 全 NO_ACTION | Self-reviewed | REJECT/HOLD/REVISE/ESCALATE | 不触发写 | **禁止 approved 合成回执**；outcome 按 RR |
| 20′ | 至少一个副作用 | Executed | APPROVE | 幂等重入 | **仅**满足 §6 重试约束才可重入；否则 `REJECT` |
| 20a | 全 NO_ACTION | Executed | NO_ACTION_APPROVE | — | **禁止再次“执行”**；只允许审计/查询原合成回执 |

---

## 6. Executed 重试约束（收紧 GIP-Q9）

> **默认：`Executed` 不应再次可写。**  
> 仅当同时满足下列全部条件时，允许**平台超时类**受控重试：

| # | 约束 |
|---|---|
| R1 | 相同 `idempotency_key` |
| R2 | 相同 packet `revision` 与 action 内容哈希（目标、数值、动作类型均不变） |
| R3 | 上次 Receipt 状态属于可重试集合：`TIMEOUT` / `UNKNOWN`（**不含** `ACCEPTED` / `REJECTED_BY_PLATFORM` / `REJECTED_BY_GATE`） |
| R4 | 不允许改变 target / change / action_type / action_class |
| R5 | 记录 `retry_count`、`previous_receipt_id`、`retry_reason` |
| R6 | 达到重试上限（**Proposed**：`max_retry=2`）后转 `HOLD` 或 `ESCALATE`，不得无限重试 |
| R7 | NO_ACTION 包**永不**进入写重试 |
| R8 | Shadow 包**永不**因重试进入真实写 |

失败码：`ADAPT-2006`（约束不满足）；超限：`ADAPT-2007` 或 `GATE-2004`（按是否 HOLD）。

---

## 7. 实现检查清单增量（取代 v0.2 §9.1 相关项）

### 7.1 Adapter / Gate

- [ ] G-00：Schema + envelope 一致性先于业务门禁  
- [ ] 实现 `is_no_action`：`bool(actions) and all(class == NO_ACTION)`，空列表为 False  
- [ ] 实现双谓词 `non_no_action_executable` / `no_action_observable`  
- [ ] 返回 `decision_outcome`，**不**返回可被误读的 bare `allowed`  
- [ ] 副作用动作 + `NO_ACTION_APPROVE` → `REJECT`（`GATE-1006`）  
- [ ] 全 NO_ACTION + `APPROVE` → `REJECT`（`GATE-1007`）  
- [ ] 全 NO_ACTION + 缺 `no_action_reason` → `REJECT`（`GATE-1009`）  
- [ ] 空 actions → `REJECT`（`GATE-1008`）  
- [ ] NO_ACTION 路径：零 Transport 写；Receipt `synthetic=true` 且 `platform_ack_ref=null`  
- [ ] Shadow 写硬拒绝与 RR 无关  
- [ ] Executed 重试满足 §6 R1–R8  
- [ ] 所有拒绝写 TRACE + 规范 `reason_codes`

### 7.2 SRA

- [ ] `review.issuer_type == SRA`（HUMAN_* 经 SRA 映射）  
- [ ] 写 `NO_ACTION_APPROVE` 前断言 `is_no_action`  
- [ ] 写 `APPROVE` 前断言 `not is_no_action`  
- [ ] `risk.hard_block` 非空禁止 `APPROVE`（继承）；NO_ACTION 时 hard_block 可作为维持原因显式记录  

---

## 8. 错误码 / outcome 映射（对齐 Error Catalog v0.1.1）

| 场景 | reason_code | decision_outcome |
|---|---|---|
| Schema/Envelope 非法 | `GATE-1008` / `DP-1001` / `ENV-1003` | `REJECT` |
| 生命周期不可执行 | `GATE-1002` | `REJECT` |
| 副作用动作 + NO_ACTION_APPROVE | `GATE-1006` / `GATE-2008` | `REJECT` |
| NO_ACTION + APPROVE | `GATE-1007` | `REJECT` |
| 空 actions | `GATE-1008` | `REJECT` |
| 缺 no_action_reason | `GATE-1009` | `REJECT` |
| 合法 NO_ACTION 批准 | `GATE-2007` | `SYNTHETIC_NO_ACTION` |
| Trust 不足 | `GATE-2001` | `REJECT` 或 `HOLD` |
| hard_block / R4 | `GATE-1005` / `GATE-2002` | `REJECT` |
| Shadow 写 | `GATE-1004` / `ADAPT-2001` | `REJECT` |
| HOLD 审批 | `GATE-2004` | `HOLD` |
| ESCALATE | `GATE-2006` | `ESCALATE` |
| Executed 重试约束失败 | `ADAPT-2006` | `REJECT` |
| Executed 禁止改写 | `ADAPT-2007` | `REJECT` |

---

## 9. 待决问题

| ID | 问题 | v0.2.1 处理 | 阻塞 |
|---|---|---|---|
| GIP-Q9 | Executed 重入语义 | **部分关闭**：§6 约束；部分失败仍进 Receipt，不重写 RR | 否 |
| GIP-Q11（新） | G-00 与 G-07 的 envelope 检查边界是否在实现中合并组件 | 逻辑顺序固定 G-00 先；组件可同进程 | 否 |
| GIP-Q12（新） | `max_retry=2` 等数值 | **Proposed**，待 GA2-T07 | 否 |

---

## 10. 变更记录

| 日期 | 版本 | 变更 | 依据 |
|---|---|---|---|
| 2026-09-15 | v0.2.1 | 固化 G-00…G-09；双谓词；废止单一 allowed；动作—审批对应；Executed 重试约束；组合裁决补丁；错误码映射 | 审计 §5/§14；DPK v0.2.1；GIP v0.2 |

---

**Document Status:** Draft（现行权威增补）  
**Authoritative For:** 门禁顺序、双谓词、decision_outcome、NO_ACTION/写路径分流、Executed 重试  
**Owner Review:** 待项目负责人 / Research Architect  
**Explicit Non-claim:** 不改 GA-1；无真实 API；阈值 Proposed；本文件不构成 Confirmed GA-DEC。
