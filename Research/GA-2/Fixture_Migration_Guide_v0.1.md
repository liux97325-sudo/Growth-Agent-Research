# GA-2：Fixture / 样例 v0.1 → v0.2 迁移说明

**文档编号：** GA-2-FIXMIG-001  
**任务编号：** GA2-T20  
**版本：** v0.1  
**状态：** Draft  
**阶段：** GA-2 Engineering Design  
**权威契约：** `Decision_Packet_Schema_v0.1.md`（GA2-T10）  
**源接口：** `JD_Adapter_Interface_v0.1.md`（GA2-T06，历史，已被 v0.2 承接）  
**目标接口：** `JD_Adapter_Interface_v0.2.md`（GA2-T18，含 §10 迁移对照）  
**关联：** `Gate_Integration_Playbook_v0.2.md`、`Shadow_Mode_Design_v0.1.md`  
**作者角色：** Research Engineer 子代理  
**约束：** 不改 GA-1；不接真实 API；所有阈值与默认值一律 **Proposed**。本文档仅服务 **本地 Fixture / 测试样例 / Mock 决策包** 的字段迁移，不触达任何真实广告账户。

---

## 0. 为什么需要本指南

JD Adapter v0.1 的 `DecisionPackage.status` **混用**了「包生命周期」与「审批结果」两个语义（`DRAFT / PENDING_REVIEW / APPROVE / REVISE / HOLD / REJECT / ESCALATE_HUMAN`）。  
v0.2 与 `Decision_Packet_Schema_v0.1` 对齐后改为**双字段**：

- `lifecycle_status`：`Draft → Self-reviewed → Executed → Observed → Reflected → Archived / Superseded`
- `review_result`：`APPROVE / NO_ACTION_APPROVE / REVISE / HOLD / REJECT / ESCALATE_HUMAN`

若旧 Fixture 未迁移而直接喂给 v0.2 Adapter：

1. **G-01 全量拒绝**——旧包没有 `lifecycle_status` / `review_result`，`G-01` 伪逻辑会返回 `DECISION_PACKAGE_INVALID`；
2. **Shadow 路径误判**——旧包缺少 `packet_kind` / `execution_mode`，无法区分 Shadow 写禁令；
3. **NO_ACTION 语义丢失**——旧包没有 `action_class=NO_ACTION` + `no_action_reason`，收割稳定性样例无法过 DPK-I2/I4；
4. **学习污染**——回执缺少 `source_env` 与 `SIMULATED` / `NOT_APPLICABLE_NO_ACTION`，Shadow/Fixture 样本可能被误计入 Trust T2/T8。

本指南给出：字段映射、迁移规则、样例对照、G-01/G-07 校验清单、双读窗口与回滚、待决问题。

---

## 1. 字段映射表（v0.1 → v0.2）

> 与 `JD_Adapter_Interface_v0.2.md` §10 一致；冲突时以该文 + `Decision_Packet_Schema_v0.1` 为准。

### 1.1 DecisionPackage 顶层与子对象

| v0.1 字段 / 取值 | v0.2 字段 / 取值 | 迁移动作 |
|---|---|---|
| `status: DRAFT` | `lifecycle_status: Draft` | 直接改名；`review_result` 留空（Draft 期允许） |
| `status: PENDING_REVIEW` | `lifecycle_status: Draft` | 生命周期仍为 Draft；审批过程态不进包 status；可选在 `tags` 加 `"pending_review"` |
| `status: APPROVE` | `lifecycle_status: Self-reviewed` + `review_result: APPROVE` | **拆分**；可执行前置 |
| `status: REVISE` | `lifecycle_status: Self-reviewed` + `review_result: REVISE` | 可选 `revision+1` 回 Draft |
| `status: HOLD` | `lifecycle_status: Self-reviewed` + `review_result: HOLD` | 挂起；不进入 Executed |
| `status: REJECT` | `lifecycle_status: Self-reviewed` + `review_result: REJECT`；随后 `→ Archived` | 失败包必须保留（DPK-I6），禁止物理删除 |
| `status: ESCALATE_HUMAN` | `lifecycle_status: Self-reviewed` + `review_result: ESCALATE_HUMAN` | 等待 HUMAN_*；`review.human_ticket_id` 可填 |
| （无） | `review_result: NO_ACTION_APPROVE` | 收割 NO_ACTION 专用审批结果 |
| （无） | `lifecycle_status: Executed / Observed / Reflected / Archived / Superseded` | 执行后生命周期；旧 Fixture 若已有回执可推断到 Executed 及以后 |
| `risk_level`（顶层） | `risk.risk_level` + `risk.hard_block` + `risk.constraints` + `risk.reason_codes` + `risk.baseline_version` | 子对象化；缺失 `hard_block=[]`、`constraints={}` |
| `trust_level_required`（顶层） | `trust.trust_required` + `trust.trust_actual`（+ 可选 `trust_score_snapshot` / `version`） | 旧值写入 `trust_required`；`trust_actual` 缺失时 **Proposed** 先拷贝 `trust_required` 并打 `tags:["trust_actual_imputed"]` |
| `self_review_result_ref`（顶层） | `review.review_result` + `review.approved_by` + `review.predicate_trace` + `review.reason_codes` + `review.review_event_id` | 从「引用」到「内联结果」；旧 ref 可写入 `review.human_ticket_id` 或 notes |
| `objective_weights_ref` | `objective_snapshot`（`template_id` / `weights` / `lifecycle_bias` / `explanation`） | 若旧包只有 ref，`template_id` 填 ref，`weights` 用对应 Parameter Genome 模板补全（**Proposed**） |
| （无） | `packet_kind` | Fixture 默认 `shadow_decision`（本轮唯一允许） |
| （无） | `execution_mode` | Fixture 默认 `SHADOW_READ_ONLY` |
| （无） | `schema_version` | 建议 bump 至 `"0.2.0"`；旧值若无则填 `"0.1.0"` 并保留迁移审计 |
| （无） | `state_digest` / `forecast_ref` / `hypothesis`（完整） | 决策输入最小契约；旧包缺失时用 Fixture 占位对象并打 `tags:["migrated_v01"]` |
| （无） | `action_receipts[]` / `outcome_ref` / `reflection_ref` / `causal_ids` | 执行后回填槽；旧包若有 receipt 则按 action_id 对齐写入 |
| `approved_by`（若有，顶层） | `review.approved_by` | 迁入子对象 |

### 1.2 ActionReceipt.status

| v0.1 | v0.2 | 迁移动作 |
|---|---|---|
| `ACCEPTED` | `ACCEPTED` | 保留；若 Fixture 来源，**Proposed** 改写为 `SIMULATED` + `audit.source_env=FIXTURE` |
| `REJECTED_BY_PLATFORM` | `REJECTED_BY_PLATFORM` | 保留 |
| `REJECTED_BY_GATE` | `REJECTED_BY_GATE` | 保留 |
| `TIMEOUT` | `TIMEOUT` | 保留 |
| `UNKNOWN` | `UNKNOWN` | 保留 |
| （无） | `SIMULATED` | Shadow / Fixture 模拟回执 |
| （无） | `NOT_APPLICABLE_NO_ACTION` | NO_ACTION 合成回执 |

### 1.3 AbstractActionRequest 增量

| v0.1 | v0.2 | 说明 |
|---|---|---|
| （无 `action_class`） | 必填 `action_class` ∈ `KEYWORD_BID / AUDIENCE_PREMIUM / BUDGET / ROI_TARGET / PLAN_CONTROL / CREATE_PLAN / NO_ACTION` | 从 `action_type` 推导（见 §2.3） |
| `decision_package_id` | 同名；G-01 改读双字段 | 注释更新，字段名不变 |

### 1.4 门禁语义（迁移时须同步解读）

| 门禁 | v0.1 | v0.2（迁移后） |
|---|---|---|
| **G-01** | `status == APPROVE` | `lifecycle_status ∈ {Self-reviewed, Executed}` **且** `review_result ∈ {APPROVE, NO_ACTION_APPROVE}`；`execution_mode=SHADOW_READ_ONLY` → 写路径硬拒绝（`SHADOW_WRITE_FORBIDDEN`） |
| **G-07** | `dry_run == true` | 同；并覆盖 `execution_mode=SHADOW_READ_ONLY` 或 Runtime ≠ LIVE |
| G-02 | Trust ≥ 门槛 | 同；改读 `trust.trust_required/actual` |
| G-03 | Risk 允许 | 同；改读 `risk.hard_block` + `risk.constraints`；`R4` 默认拒 |
| G-04–G-06, G-08–G-09 | 不变 | **不变** |

> Gate_Integration_Playbook 中 `DP.status==APPROVE` 的表述，在 v0.2 语境下应读作上述 G-01 双条件（JD-Q12）。

---

## 2. 迁移规则

### 2.1 通用原则

1. **只迁移本地 Fixture / Mock / 测试样例**；不触达真实平台。  
2. **禁止静默丢字段**：无法映射的 v0.1 字段移入 `migration.legacy` 保留，供审计。  
3. **禁止伪造 PASS**：缺失 Risk/Trust/Review 时打 gap / `unknown`，不得填成全绿。  
4. **Shadow 优先**：本轮所有迁移后 Fixture 的 `execution_mode` 一律 `SHADOW_READ_ONLY`。  
5. **阈值 Proposed**：迁移中推断出的幅度、频率、置信度均为 **Proposed**，不得当作实测。

### 2.2 迁移伪逻辑

```text
migrate_v01_to_v02(old):
  new = {
    schema_version: "0.2.0",
    decision_id: old.decision_id,
    revision: old.revision ?? 1,
    migration: { from_schema: "0.1", migrated_at: now, legacy: {} }
  }

  // 1) status 双字段拆分（核心）
  switch old.status:
    DRAFT | PENDING_REVIEW:
      new.lifecycle_status = "Draft"
      new.review_result = null
      if old.status == PENDING_REVIEW: new.tags += ["pending_review"]
    APPROVE:
      new.lifecycle_status = "Self-reviewed"
      new.review_result = infer_no_action(old) ? "NO_ACTION_APPROVE" : "APPROVE"
    REVISE | HOLD | REJECT | ESCALATE_HUMAN:
      new.lifecycle_status = "Self-reviewed"
      new.review_result = map(old.status)
      if old.status == REJECT: new.tags += ["reject_pattern_candidate"]
    default / unknown:
      new.lifecycle_status = "Draft"          // 保守：不可执行
      new.tags += ["unknown_v01_status"]
      new.migration.legacy.status = old.status
      // 不得进入 G-01 放行

  // 2) 若旧包已有 action_receipts / outcome，则推断执行后生命周期
  if has_receipts(old) and new.lifecycle_status in {Self-reviewed}:
    if has_outcome(old): new.lifecycle_status = "Observed"
    elif has_reflection(old): new.lifecycle_status = "Reflected"
    else: new.lifecycle_status = "Executed"

  // 3) Shadow 一等字段
  new.packet_kind = "shadow_decision"         // Fixture 默认
  new.execution_mode = "SHADOW_READ_ONLY"

  // 4) 子对象补全（见 §2.4 / §2.5）
  new.risk = migrate_risk(old)
  new.trust = migrate_trust(old)
  new.review = migrate_review(old)            // Self-reviewed 起必填
  new.objective_snapshot = migrate_objective(old)

  // 5) proposed_actions 补 action_class；NO_ACTION 补 no_action_reason
  new.proposed_actions = old.proposed_actions.map(migrate_action)
  if all_NO_ACTION(new.proposed_actions) and not new.no_action_reason:
    new.no_action_reason = "MIGRATED_FROM_V01: reason missing; Proposed placeholder"
    new.tags += ["no_action_reason_imputed"]

  // 6) 回执：Shadow/Fixture 来源打标
  if new.action_receipts:
    for r in new.action_receipts:
      r.audit = r.audit ?? {}
      r.audit.decision_id = new.decision_id
      r.audit.source_env = r.audit.source_env ?? "FIXTURE"
      if r.status == "ACCEPTED" and is_fixture(old):
        r.status = "SIMULATED"                 // 防污染

  // 7) 审计标签
  new.tags = unique((old.tags ?? []) + ["migrated_v01", "shadow"])
  return new
```

### 2.3 未知枚举处理

| 情形 | 策略 | 备注 |
|---|---|---|
| `old.status` 不在 v0.1 枚举内 | `lifecycle_status=Draft`；`tags+=["unknown_v01_status"]`；原值进 `migration.legacy.status` | **保守不可执行**；G-01 必拒 |
| `action_type` 无法映射到 `action_class` | `action_class` 置空并 `tags+=["action_class_unknown"]`；整包不可进入 Executed | 防止假门禁白名单通过 |
| `risk_level` 非 `R0–R4` | `risk.risk_level="R4"`（最严）；`tags+=["risk_level_imputed"]` | **Proposed** |
| `review_result` 未知 / 空但 `lifecycle_status=Self-reviewed` | 回退 `lifecycle_status=Draft`；`tags+=["review_result_missing"]` | 与 G-01 对齐：Self-reviewed 必有 review |
| `execution_mode` / `packet_kind` 缺失 | 强制 `shadow_decision` + `SHADOW_READ_ONLY` | Schema required |
| `validation_confidence` 缺失 | `state_digest.validation_confidence="LOW"`；`gap_flags+=["LOW_VALIDATION_CONFIDENCE"]` | 不得伪 HIGH |

### 2.4 缺失 review 的补全策略

| 情形 | 策略 | 说明 |
|---|---|---|
| 旧 `status=APPROVE` 且无 `self_review_result_ref` | `review.review_result=APPROVE`；`approved_by="AGENT"`；`predicate_trace=[]`；`reason_codes=["MIGRATED_NO_TRACE"]`；`review_event_id="REV-MIG-"+decision_id` | 可执行但审计降级；**Proposed** |
| 旧 `status=APPROVE` 且 `proposed_actions` 全为 NO_ACTION | `review_result=NO_ACTION_APPROVE` | 对齐 DPK-I2 / §5.3 |
| 旧有 review ref 但无 predicate_trace | 保留 ref 到 `review.human_ticket_id` 或 `migration.legacy.review_ref`；`predicate_trace=[]` + `reason_codes+=["TRACE_UNAVAILABLE"]` | 禁止伪造 CHK_* 全 pass |
| 旧 `status=REJECT/HOLD/REVISE/ESCALATE` | 按 §1.1 映射；**不**补成 APPROVE | 失败包保留（DPK-I6） |
| 旧 `status=DRAFT` | 不写 `review`（Draft 允许空） | Self-reviewed 起必填 |

### 2.5 Shadow 标签补全策略

迁移后 Fixture **必须**带齐下列标签，否则 Shadow Mode 联调与防污染审计失败：

| 字段 | 迁移后取值 | 依据 |
|---|---|---|
| `packet_kind` | `shadow_decision` | Schema required；本轮唯一允许 |
| `execution_mode` | `SHADOW_READ_ONLY` | GA-DEC-004 红线 |
| `tags` | 至少含 `"shadow"` 与 `"migrated_v01"` | Schema §2.7；本指南 |
| `adapter_runtime_mode` | `FIXTURE_ONLY` 或 `SIMULATION` | JD v0.2 §7.1 |
| `action_receipts[].status` | 非 NO_ACTION 的 Fixture 回执 → `SIMULATED`；NO_ACTION → `NOT_APPLICABLE_NO_ACTION` | 防止 ACCEPTED 污染 |
| `action_receipts[].audit.source_env` | `FIXTURE` 或 `SHADOW` | JD v0.2 §4.9；JD-Q10 |
| `shadow.learning_pool`（若补） | `isolated`（默认 Proposed） | Schema §7.3 |
| Trust 计分 | **默认不计入** T2/T8 | Shadow_Mode_Design §5；JD-Q10 |

**禁止：**

1. 把迁移后 SIMULATED 回执表述为「平台已执行」。  
2. 把 `tags=["shadow"]` 的经验/规则直接晋升企业规则池（需特批通道，见 Shadow §5.4）。  
3. 因为是 Fixture 就把 BDV 校验结果伪造成 `PASS`。

### 2.6 NO_ACTION 特例

收割 NO_ACTION 样例（FX-02）迁移时必须同时满足：

1. `proposed_actions` 含 `action_class=NO_ACTION`（由 `WA-CLS-01` 推导）。  
2. `no_action_reason` 非空；缺失时用 §2.2 占位并打 `no_action_reason_imputed`。  
3. `review_result=NO_ACTION_APPROVE`（不是普通 `APPROVE`）。  
4. `action_receipts[].status=NOT_APPLICABLE_NO_ACTION`。  
5. 仍走完整生命周期：`Draft → Self-reviewed → Executed(合成回执) → Observed → Reflected`（DPK-I2）。  
6. `proposed_actions` 不得为空数组以外的「无动作却无 NO_ACTION 类」（DPK-I4）。

---

## 3. 迁移前后 JSON 样例

> 样例为本地 Fixture / 设计样例，数值一律 **Proposed**，非企业真值。  
> 对应 JD §2.4 `FX-01` / `FX-02` 与 Decision_Packet_Schema §8.1 / §8.2。

### 3.1 样例 A：种草干预（FX-01）

#### A.1 迁移前（v0.1 风格，节选）

```json
{
  "decision_id": "DP-JD-20260911-0001",
  "schema_version": "0.1.0",
  "revision": 1,
  "status": "APPROVE",
  "plan_mode": "SEEDING",
  "plan_id": "PLAN-8821",
  "objective_weights_ref": "JD-MHB-SEED-GROW@0.1.0",
  "observations": {
    "window": {"start": "2026-09-11T09:00:00+08:00", "end": "2026-09-11T11:00:00+08:00"},
    "metric": "impressions|clicks|ctr",
    "delta": "impressions -38%, clicks -35%, ctr -5% vs 7d same-slot"
  },
  "hypothesis": "核心关键词竞争增强，展现能力下降",
  "evidence_refs": ["VM-20260911-0900", "VM-20260911-1100"],
  "proposed_actions": [
    {
      "action_id": "ACT-001",
      "action_type": "WA-BID-01",
      "decision_package_id": "DP-JD-20260911-0001",
      "plan_mode": "SEEDING",
      "target": {"plan_id": "PLAN-8821", "keyword_id": "KW-core-001"},
      "change": {"field": "bid", "from_value": 4.20, "to_value": 4.70, "relative_pct": 0.12},
      "rationale_ref": "hypothesis",
      "dry_run": true
    }
  ],
  "expected_response_window": {"min_minutes": 120, "max_minutes": 360, "metric_hint": ["impressions", "clicks"]},
  "risk_level": "R2",
  "trust_level_required": 2,
  "self_review_result_ref": "REV-20260911-0001",
  "approved_by": "AGENT",
  "created_at": "2026-09-11T11:10:00+08:00",
  "decided_at": "2026-09-11T11:12:30+08:00"
}
```

#### A.2 迁移后（v0.2，节选；关键 diff 标注）

```json
{
  "decision_id": "DP-JD-20260911-0001",
  "schema_version": "0.2.0",
  "revision": 1,
  "lifecycle_status": "Self-reviewed",
  "review_result": "APPROVE",
  "packet_kind": "shadow_decision",
  "execution_mode": "SHADOW_READ_ONLY",
  "domain": "JD_AD",
  "tenant_id": "TEN-DEMO",
  "shop_id": "SHOP-DEMO-01",
  "episode_id": "EP-DEMO-0007",

  "objective_snapshot": {
    "template_id": "T-MHB-SEED",
    "weights": {"ctr": 0.31, "clicks": 0.23, "add_cart": 0.17, "impressions": 0.13, "cpc": 0.10, "gmv_roi": 0.06},
    "lifecycle_bias": "lifecycle_grow",
    "explanation": "中高客单×种草×成长放量（Proposed，由 objective_weights_ref 补全）"
  },

  "state_digest": {
    "state_id": "STATE-20260911-1100",
    "as_of": "2026-09-11T11:00:00+08:00",
    "hash": "sha256:migrated",
    "plan_mode": "SEEDING",
    "lifecycle_phase": "growth",
    "inventory_risk": "OK",
    "gap_flags": [],
    "validation_confidence": "HIGH"
  },

  "forecast_ref": {
    "forecast_id": "FC-20260911-1030-01",
    "horizon": "to_18:00",
    "confidence": 0.72,
    "summary": {"impression_trend": "down_vs_baseline", "ctr_trend": "down"},
    "based_on_validated_ids": ["VM-20260911-0900", "VM-20260911-1100"]
  },

  "genome_ref": "JD-MHB-SEED-GROW@0.1.0",

  "hypothesis": {
    "observation": {
      "window": {"start": "2026-09-11T09:00:00+08:00", "end": "2026-09-11T11:00:00+08:00"},
      "metric": "impressions|clicks|ctr",
      "delta": "impressions -38%, clicks -35%, ctr -5% vs 7d same-slot",
      "baseline_ref": "BASE-7D-SLOT",
      "state_id": "STATE-20260911-1100"
    },
    "cause_claim": "核心关键词竞争增强，展现能力下降",
    "confidence": 0.68
  },

  "proposed_actions": [
    {
      "action_id": "ACT-001",
      "action_type": "WA-BID-01",
      "action_class": "KEYWORD_BID",
      "target": {"plan_id": "PLAN-8821", "keyword_id": "KW-core-001"},
      "change": {"field": "bid", "from_value": 4.20, "to_value": 4.70, "relative_pct": 0.12},
      "priority": 1,
      "rationale_ref": "hypothesis#cause_claim"
    }
  ],

  "expected_response_window": {"min_minutes": 120, "max_minutes": 360, "metric_hint": ["impressions", "clicks"]},

  "risk": {
    "risk_level": "R2",
    "hard_block": [],
    "constraints": {"max_bid_delta_pct": 0.15, "max_daily_adjust_count": 4, "min_response_window_minutes": 120},
    "reason_codes": ["SEEDING_PLAN", "MIGRATED_V01"],
    "baseline_version": "RB-2026W37-01"
  },

  "trust": {
    "trust_required": 2,
    "trust_actual": 2,
    "trust_score_snapshot": null,
    "version": null
  },

  "review": {
    "review_result": "APPROVE",
    "approved_by": "AGENT",
    "predicate_trace": [],
    "reason_codes": ["MIGRATED_NO_TRACE"],
    "review_event_id": "REV-MIG-DP-JD-20260911-0001"
  },

  "executor": "JDA-01",
  "adapter_runtime_mode": "FIXTURE_ONLY",

  "migration": {
    "from_schema": "0.1",
    "migrated_at": "2026-09-12T10:00:00+08:00",
    "legacy": {"status": "APPROVE", "risk_level": "R2", "trust_level_required": 2, "objective_weights_ref": "JD-MHB-SEED-GROW@0.1.0"}
  },
  "tags": ["shadow", "seeding", "migrated_v01", "FX-01"]
}
```

**A 迁移要点：** `status=APPROVE` → 双字段；`risk/trust/review` 子对象化；补 `action_class=KEYWORD_BID`；补 `packet_kind/execution_mode`；`predicate_trace` 为空但显式标注 `MIGRATED_NO_TRACE`（不伪造）。

---

### 3.2 样例 B：收割 NO_ACTION（FX-02）

#### B.1 迁移前（v0.1 风格，节选）

```json
{
  "decision_id": "DP-JD-20260911-0002",
  "schema_version": "0.1.0",
  "revision": 1,
  "status": "APPROVE",
  "plan_mode": "HARVEST",
  "plan_id": "PLAN-9012",
  "objective_weights_ref": "JD-MHB-HARVEST-MATURE@0.1.0",
  "observations": {
    "metric": "trusted_roi",
    "delta": "within p40–p60 of 14d band; no material deterioration"
  },
  "hypothesis": "系统托管学习中；当前波动属正常噪声",
  "proposed_actions": [
    {
      "action_id": "ACT-001",
      "action_type": "WA-CLS-01",
      "decision_package_id": "DP-JD-20260911-0002",
      "plan_mode": "HARVEST",
      "target": {"plan_id": "PLAN-9012"},
      "rationale_ref": "stability_first",
      "dry_run": true
    }
  ],
  "expected_response_window": {"min_minutes": 0, "max_minutes": 1440, "metric_hint": ["trusted_roi", "spend"]},
  "risk_level": "R1",
  "trust_level_required": 0,
  "self_review_result_ref": "REV-20260911-0002",
  "approved_by": "AGENT",
  "created_at": "2026-09-11T14:00:00+08:00",
  "decided_at": "2026-09-11T14:01:00+08:00"
}
```

> 注意：v0.1 把 NO_ACTION 也标成了 `status=APPROVE`，且**没有** `no_action_reason` / `action_class`——这正是迁移时最容易漏、导致 DPK-I2/I4 失败的点。

#### B.2 迁移后（v0.2，节选）

```json
{
  "decision_id": "DP-JD-20260911-0002",
  "schema_version": "0.2.0",
  "revision": 1,
  "lifecycle_status": "Self-reviewed",
  "review_result": "NO_ACTION_APPROVE",
  "packet_kind": "shadow_decision",
  "execution_mode": "SHADOW_READ_ONLY",
  "domain": "JD_AD",
  "shop_id": "SHOP-DEMO-01",
  "episode_id": "EP-DEMO-0008",

  "objective_snapshot": {
    "template_id": "T-MHB-HARVEST",
    "weights": {"gmv_roi": 0.31, "add_cart": 0.23, "ctr": 0.17, "clicks": 0.13, "cpc": 0.10, "impressions": 0.06},
    "explanation": "中高客单×收割×成熟：成交与稳定性优先（Proposed）"
  },

  "state_digest": {
    "state_id": "STATE-20260911-1400",
    "plan_mode": "HARVEST",
    "lifecycle_phase": "mature",
    "inventory_risk": "OK",
    "gap_flags": [],
    "validation_confidence": "HIGH"
  },

  "forecast_ref": {
    "forecast_id": "FC-20260911-1330-02",
    "horizon": "to_day_end",
    "confidence": 0.80,
    "summary": {"roi_band": "within_baseline", "improvement_if_adjust": "below_noise_threshold", "stability_score": "high"},
    "based_on_validated_ids": ["VM-20260911-1400"]
  },

  "hypothesis": {
    "observation": {
      "metric": "trusted_roi",
      "delta": "within p40–p60 of 14d band; no material deterioration",
      "baseline_ref": "BASE-14D"
    },
    "cause_claim": "系统托管学习中；当前波动属正常噪声，无显著恶化证据",
    "confidence": 0.77
  },

  "proposed_actions": [
    {
      "action_id": "ACT-001",
      "action_type": "WA-CLS-01",
      "action_class": "NO_ACTION",
      "target": {"plan_id": "PLAN-9012"},
      "priority": 1,
      "rationale_ref": "stability_first"
    }
  ],

  "no_action_reason": "MIGRATED_FROM_V01: reason missing in v0.1 fixture; Proposed placeholder. CHK_STAB：成熟收割+prefer_stability，预测改进小于噪声阈值；避免打断系统学习（架构 P5）",

  "expected_response_window": {"min_minutes": 0, "max_minutes": 1440, "metric_hint": ["trusted_roi", "spend"]},

  "risk": {
    "risk_level": "R1",
    "hard_block": [],
    "constraints": {"max_bid_delta_pct": 0.10, "max_daily_adjust_count": 1, "min_response_window_minutes": 1440},
    "reason_codes": ["HARVEST_STABLE", "MIGRATED_V01"],
    "baseline_version": "RB-2026W37-01"
  },

  "trust": {
    "trust_required": 0,
    "trust_actual": 3,
    "trust_score_snapshot": null
  },

  "review": {
    "review_result": "NO_ACTION_APPROVE",
    "approved_by": "AGENT",
    "predicate_trace": [],
    "reason_codes": ["MIGRATED_NO_TRACE"],
    "review_event_id": "REV-MIG-DP-JD-20260911-0002"
  },

  "executor": "JDA-01",
  "adapter_runtime_mode": "FIXTURE_ONLY",

  "action_receipts": [
    {
      "receipt_id": "RCPT-NOACT-0002",
      "action_id": "ACT-001",
      "status": "NOT_APPLICABLE_NO_ACTION",
      "idempotency_key": "DP-JD-20260911-0002:ACT-001",
      "submitted_at": "2026-09-11T14:01:00+08:00",
      "audit": {
        "decision_id": "DP-JD-20260911-0002",
        "causal_memory_pending": true,
        "source_env": "FIXTURE"
      }
    }
  ],

  "migration": {
    "from_schema": "0.1",
    "migrated_at": "2026-09-12T10:00:00+08:00",
    "legacy": {"status": "APPROVE", "risk_level": "R1", "trust_level_required": 0}
  },
  "tags": ["shadow", "harvest", "no_action", "no_action_reason_imputed", "migrated_v01", "FX-02"]
}
```

**B 迁移要点：** 旧 `status=APPROVE` **不可**机械映射为 `review_result=APPROVE`——当 `action_type=WA-CLS-01` / 全 NO_ACTION 时，应升为 `NO_ACTION_APPROVE`；补 `action_class` + `no_action_reason` + `NOT_APPLICABLE_NO_ACTION` 回执。

---

## 4. 校验清单：迁移后 G-01 / G-07 应通过的条件

> 本清单供 Fixture 回归测试与 Adapter 联调使用。全部通过才允许该 Fixture 进入 G-02…G-09 后续门禁。

### 4.1 G-01（决策包有效且可执行）

| # | 检查项 | 通过条件 | 失败原因码 |
|---|---|---|---|
| 1 | 包存在 | `decision_package_id` 可加载 | `DECISION_PACKAGE_INVALID` |
| 2 | 生命周期 | `lifecycle_status ∈ {Self-reviewed, Executed}`（或迁移推断的 Executed/Observed/Reflected） | `DECISION_PACKAGE_INVALID` |
| 3 | 审批结果 | `review_result ∈ {APPROVE, NO_ACTION_APPROVE}` | `DECISION_PACKAGE_INVALID` |
| 4 | 双字段一致 | `lifecycle_status=Self-reviewed` ⇒ `review.review_result` 非空且与顶层 `review_result` 一致 | `DECISION_PACKAGE_INVALID` |
| 5 | Shadow 写拦截 | 若 `execution_mode=SHADOW_READ_ONLY`：写路径返回 `SHADOW_WRITE_FORBIDDEN`（可选生成 `SIMULATED` 回执供审计） | `SHADOW_WRITE_FORBIDDEN` |
| 6 | NO_ACTION 成包 | 全 NO_ACTION 时：`action_class=NO_ACTION` + `no_action_reason` 非空 + `review_result=NO_ACTION_APPROVE` + 合成回执 | `DECISION_PACKAGE_INVALID` / DPK-I2/I4 |
| 7 | 不得全量拒绝 | 迁移后 Fixture **不应**因缺少 v0.1 单字段 `status` 而被 G-01 拒；旧字段若残留应被忽略或进 `migration.legacy` | — |
| 8 | risk.hard_block | 若非空，即使 review 标了 APPROVE，G-03 仍应拒（跨门禁一致性） | `HARD_BLOCK` |
| 9 | validation_confidence | `LOW` 时 Reasoning 不得输出写动作；Adapter 可二次拒绝 | `DECISION_PACKAGE_INVALID` |

**G-01 伪逻辑（迁移后应满足）：**

```text
PASS iff:
  packet exists
  AND lifecycle_status in {Self-reviewed, Executed, Observed, Reflected}
  AND review_result in {APPROVE, NO_ACTION_APPROVE}
  AND (execution_mode != SHADOW_READ_ONLY  OR  请求为只读/审计 SIMULATED)
```

### 4.2 G-07（dry_run / 环境政策）

| # | 检查项 | 通过条件 | 失败原因码 |
|---|---|---|---|
| 1 | dry_run | 所有写请求 `dry_run=true` | `DRY_RUN_REQUIRED` |
| 2 | Runtime | `adapter_runtime_mode ∈ {FIXTURE_ONLY, SIMULATION}`；非 LIVE | `DRY_RUN_REQUIRED` |
| 3 | execution_mode | `SHADOW_READ_ONLY` 时强制 dry_run；写路径硬失败 | `DRY_RUN_REQUIRED` / `SHADOW_WRITE_FORBIDDEN` |
| 4 | LiveTransport | 未装配 / 硬失败；凭证源不存在 | 启动自检失败 |
| 5 | 回执来源 | 回执必须带 `audit.source_env ∈ {FIXTURE, SHADOW, SIMULATION, LIVE, HUMAN}`；**Fixture 回归套件中禁止出现 LIVE**（LIVE 仅用于真机只读评估，且须 T25b 授权） | 审计不合规 |

### 4.3 Fixture 回归通过标准（整包）

1. **Schema 校验**：通过 `Decision_Packet_Schema_v0.1` JSON Schema 草案（或等价校验器）。  
2. **G-01 双条件**：对「应放行」样例（A/B）不返回 `DECISION_PACKAGE_INVALID`（Shadow 写除外）。  
3. **G-07**：所有 `dry_run=true`；无真实出口。  
4. **NO_ACTION**：样例 B 生成 `NOT_APPLICABLE_NO_ACTION`，而非 `ACCEPTED`。  
5. **Shadow 防污染**：`tags` 含 `shadow`；`source_env` 正确；不计入 Trust T2/T8。  
6. **失败包保留**：若含 v0.1 `REJECT` 样例，迁移后仍可检索（DPK-I6），不可被静默删除。  
7. **未知枚举保守**：故意构造的未知 `status` 样例，G-01 **必须拒绝**（反向测试）。

---

## 5. 回滚策略与双读窗口

### 5.1 适用场景

实现期可能出现：部分服务/测试仍读 v0.1 单字段，部分已切 v0.2 双字段。本节给出 **Proposed** 的并存策略，供实现评审确认。

### 5.2 双读窗口（Dual-Read）

| 阶段 | 写侧 | 读侧 | Fixture 策略 |
|---|---|---|---|
| **T0 冻结前** | 仍写 v0.1 `status` | 只读 v0.1 | 旧 Fixture 原样 |
| **T1 迁移期（双读）** | 新写双字段；**兼容镜像**同步写旧 `status`（只读别名，不参与门禁） | 优先读双字段；缺失时 fallback 旧 `status` 并打 `legacy_read` 日志 | 本指南脚本批量迁移；新旧各存一份 |
| **T2 切换期** | 只写双字段 | 只读双字段；旧 `status` 仅审计 | 旧 Fixture 标记 `deprecated` |
| **T3 关闭** | 禁止旧字段 | 禁止 fallback | 旧 Fixture 移入 `legacy/` 归档目录 |

**双读规则（T1）：**

1. **权威源**：双字段永远权威；旧 `status` 仅作 fallback 与审计。  
2. **冲突即拒**：若双字段与旧 `status` 推断结果不一致 → 标 `tags+=["schema_conflict"]`，G-01 拒绝（不猜）。  
3. **Shadow 优先**：双读期所有新包强制 `execution_mode=SHADOW_READ_ONLY`。  
4. **可观测**：每次 fallback 记 metrics `fixture_legacy_status_reads`，作为 T3 关闭条件（连续 N 日为 0，**Proposed**）。

### 5.3 回滚策略

| 触发条件 | 回滚动作 | 数据处置 |
|---|---|---|
| 迁移脚本批量失败率 > 阈值（**Proposed** 5%） | 停止迁移；保留 v0.1 Fixture 原样 | 迁移产物移入 `migrated_staging/`，不覆盖原文件 |
| G-01 在「应放行」样例上全量拒绝 | 回退读路径到 v0.1 fallback；排查映射 bug | 双字段产物保留，标 `g01_regression` |
| G-07 / Shadow 红线被突破（出现非 dry_run 或写路径放行） | **立即熔断**写路径；Runtime 强制 `FIXTURE_ONLY` | 相关回执进 Failure Pattern；禁止静默删除 |
| Schema 校验器与文档冲突 | 以 `Decision_Packet_Schema_v0.1` 为准修订脚本；不改 Schema 绕过 | 冲突样例进待决问题 |
| 实现评审未通过 | 整包回滚至 v0.1 Fixture；保留迁移报告 | 归档，不删除 |

**回滚原则：**

1. **可逆**：迁移脚本必须「读旧写新、不覆盖源文件」；源 Fixture 不可变。  
2. **可审计**：每次迁移写 `migration.migrated_at` / `from_schema` / `legacy` 快照。  
3. **不倒灌**：回滚后不得把已迁移的 v0.2 回执再写回 v0.1 结构（语义有损）。  
4. **红线优先**：任何回滚方案不得解除「Shadow 只读 / dry_run / 无凭证」红线。

### 5.4 与 Shadow Mode 四模式的关系

| Shadow Mode | 双读期行为 | 迁移后 Fixture |
|---|---|---|
| MODE_READ | 只读，无包 | 不涉及 G-01 |
| MODE_SHADOW_DECIDE | 生成 shadow 包；G-01 写硬拒 | 本指南默认目标态 |
| MODE_SHADOW_EXEC_SIM | 本地状态机推进；仍无真实写 | `adapter_runtime_mode=SIMULATION` + `SIMULATED` 回执 |
| MODE_LIVE_WRITE | **本轮禁止** | 迁移不得生成 `execution_mode=LIVE` |

---

## 6. 待决问题

| ID | 问题 | 建议 | 阻塞联调？ |
|---|---|---|---|
| FM-Q1 | 双读期旧 `status` 是否作为写镜像，还是仅 fallback 读？ | **仅 fallback 读 + 审计镜像**；门禁只认双字段 | 否（可后置） |
| FM-Q2 | 迁移脚本是否需要提供可执行实现，还是仅文档规则？ | 本文档为规则；脚本属实现任务，需单独授权 | 否 |
| FM-Q3 | `trust_actual` 缺失时拷贝 `trust_required` 是否可接受？ | **Proposed** 可接受，须打 `trust_actual_imputed`；上线前 TE 重算 | 否 |
| FM-Q4 | `predicate_trace` 空数组的迁移包是否允许进入 Executed 路径？ | Fixture 允许（打 `MIGRATED_NO_TRACE`）；**LIVE 语境禁止** | 是（若混用） |
| FM-Q5 | 旧 `status=APPROVE` 但动作非 NO_ACTION，是否可能应映射为其他 review_result？ | 默认 `APPROVE`；若 Risk 显示 hard_block/R4 则回退 Draft + 冲突标签 | 否 |
| FM-Q6 | 迁移后 `schema_version` 统一 `"0.2.0"` 还是保留 `"0.1.0"` + 迁移元数据？ | 统一 `"0.2.0"`；`migration.from_schema="0.1"` 保留 lineage | 否 |
| FM-Q7 | 双读窗口的关闭条件（metrics 连续 N 日为 0）N 取多少？ | **Proposed** N=7；由实现期实测调整 | 否 |
| FM-Q8 | 与 GA2-T12（GIP 同步）谁先改文档表述 `DP.status==APPROVE`？ | GIP 先按本指南 + JD v0.2 §10.3 解读；正式改写在 T12 | 否 |
| FM-Q9 | FX-03…FX-10 等其余 Fixture 是否同批迁移？ | 是；规则同源；本指南以 A/B 为样板，其余按 §2.2 批处理 | 否 |
| FM-Q10 | 迁移产物是否需要独立目录（`fixtures/v02/`）以免覆盖 v0.1？ | **是**；源目录只读；见 §5.3 可逆原则 | 否 |

---

## 7. 与后续任务的接口

| 下游任务 | 本文供给 |
|---|---|
| GA2-T11 Shadow Mode 联调 | Shadow 标签补全规则、source_env、SIMULATED 回执约定 |
| GA2-T12 Gate Playbook 同步 | G-01 双条件、G-07 扩展、`DP.status==APPROVE` 解读（JD-Q12 / FM-Q8） |
| Adapter / Fixture 实现 | 字段映射表、迁移伪逻辑、校验清单、双读窗口 |
| GA-3 验证 | 迁移后样例 A/B 可直接作为门禁闭环与 NO_ACTION 成包的回归基线 |

---

## 8. 理论与架构追踪（摘要）

| 主张 | 落点 |
|---|---|
| 成长最小原子 / 决策包可审计 | §1 双字段 + §3 样例完整生命周期 |
| NO_ACTION 合法且必须成包（架构 P5 / DPK-I2） | §2.6、§3.2、§4.1#6 |
| Shadow / 只读红线（GA-DEC-004 / DPK-I5） | §2.5、§4.2、§5.4 |
| 平台数据不可直信 | 迁移不伪造 validation_confidence / BDV PASS（§2.1#3、§2.3） |
| 失败即学习事件 / 不静默丢弃（DPK-I6） | §2.3 REJECT 保留、§4.3#6 |
| 稳定性优先 / 收割 NO_ACTION | 样例 B 全链路 |
| Trust 样本防污染（JD-Q10） | §2.5 source_env / 不计入 T2/T8 |

---

## 9. 变更记录

| 日期 | 版本 | 变更 | 依据 |
|---|---|---|---|
| 2026-09-12 | v0.1 | 首次建立 Fixture/样例 v0.1→v0.2 迁移说明：字段映射、迁移规则、双样例、G-01/G-07 校验清单、双读与回滚、待决问题 | GA2-T20；JD_Adapter_Interface_v0.1/v0.2；Decision_Packet_Schema_v0.1；Gate_Integration_Playbook；Shadow_Mode_Design |

---

**Document Status:** Draft  
**Next Review:** 项目负责人 / Research Architect；与 GA2-T11 / GA2-T12 对齐  
**Explicit Non-claim:** 本文档不代表已对接京东或抖音官方 API；所有样例为本地 Fixture；全部阈值与默认值一律 **Proposed**。
