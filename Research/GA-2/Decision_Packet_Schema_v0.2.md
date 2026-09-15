# GA-2：Decision Packet Schema v0.2（增量修订）

**文档编号：** GA-2-DPKT-002  
**任务编号：** GA2-T39  
**版本：** v0.2  
**状态：** Draft  
**阶段：** GA-2 Engineering Design  
**基线：** `Decision_Packet_Schema_v0.1.md`（Draft，GA2-T10）  
**主线架构：** `Architecture_Overview_v0.2.md`（Confirmed，GA-DEC-004）  
**对齐详设：**  
- `CBA_OFG_Interface_v0.1.md`（§2.4/§2.5/§5；CO-Q03 提案）  
- `Gate_Integration_Playbook_v0.2.md`（双字段可执行判定）  
- `JD_Adapter_Interface_v0.2.md`（DecisionPackage 双字段 + objective_snapshot）  
**授权依据：** GA2-T39 开放任务；**本文件为 Draft 增量提案，不是已确认 GA-DEC**  
**作者角色：** Research Engineer 子代理  
**约束：** 增量修订，不重写全文；不改 GA-1 / PROJECT_SPEC；不接真实 API；新增字段一律 **Proposed / optional**。

---

## 0. 相对 v0.1 的变更说明

> **继承原则：** 除本文显式列出的增量外，v0.1 的定位、硬不变式（DPK-I1…I8）、生命周期状态机、O-H-A-R-R 映射、门禁衔接、shadow 变体、端到端样例语义与理论追踪**全部继承 v0.1，不在此重写**。

### 0.1 本轮增量（v0.2）

| ID | 变更 | 性质 | 影响面 |
|---|---|---|---|
| **CHG-01** | `objective_snapshot` 增补可选字段 `derivation_trace`、`applied_overlays` | **Proposed**；`N` 可选；`F` 冻结 | OFG→DPK 对齐；关闭 CBA/CO-Q03 实现侧悬念 |
| **CHG-02** | `schema_version` 示例与 JSON Schema `$id` 建议升至 `0.2.0` | 版本策略 | Fixture / 校验器 |
| **CHG-03** | 明确 v0.1 包在 v0.2 校验器下仍合法（向后兼容） | 兼容策略 | 迁移 |
| **CHG-04** | 对齐注记：CBA/OFG 的 `ofg_version` / `generated_at` 作为 OFG 内部审计字段，**暂不**进入 DPK 必填 | 边界澄清 | 防止 Schema 膨胀 |

### 0.2 明确不做

- 不改变门禁双字段语义（`status` / `review.review_result`）；权威仍在 GIP v0.2 §1.1 与 JD v0.2。  
- 不把 `derivation_trace` / `applied_overlays` 升为必填。  
- 不修改 Architecture v0.2 §6 最小契约字段集合。  
- 不重发端到端样例全文（样例见 §3.2 增量补丁说明）。

---

## 1. 裁决：`derivation_trace` / `applied_overlays` 是否入 Schema

### 1.1 背景

`CBA_OFG_Interface_v0.1.md` §2.4 将 ObjectiveSnapshot 定义为包含：

- 既有（DPK v0.1 §2.3 已收录）：`template_id` / `weights` / `lifecycle_bias` / `explanation` / `valid_until`  
- 提案新增：`applied_overlays[]`、`derivation_trace`、以及 OFG 侧 `generated_at` / `ofg_version`

CBA §5.1 与 CO-Q03 明确：**建议 DPK v0.2 增补；当前可序列化入 explanation**。  
GIP v0.2 / JD v0.2 仅要求透传 `objective_snapshot`（含 weights），**未强制**这两个子字段。

### 1.2 选项对比

| 选项 | 做法 | 优点 | 缺点 |
|---|---|---|---|
| A 不入 Schema | 继续塞进 `explanation` / `tags` | 零迁移成本 | 不可结构化审计；SRA CHK_GOAL 难做机器校验；与 OFG 契约漂移 |
| **B 收录为 optional（Proposed）** | `objective_snapshot.derivation_trace` / `applied_overlays`，必填=`N`，可变性=`F` | 对齐 OFG；可解释性可结构化；v0.1 包仍合法 | Fixture 需逐步补齐；字段体积略增 |
| C 收录为 required | v0.2 起强制 | 审计完整 | 破坏 v0.1 兼容；对早期 Fixture / NO_ACTION 包过苛 |

### 1.3 裁决结论（Draft / Proposed）

> **采纳选项 B：以 Proposed、optional 形式收录进 `objective_snapshot`，可变性 `F`（与同对象其他字段一致，DPK-I7 / OFG-I6）。**  
> **不采纳**升为必填；**不**将 `ofg_version` / `generated_at` 作为 DPK 顶层或 snapshot 必填（可放在 derivation_trace 或 OFG 自身审计日志）。

**写入来源：** OFG（经 CBA 原样拷贝进 Packet，对齐 CBA §5.2 时序）。  
**消费方：** SRA `CHK_GOAL`（可选增强）；审计/复盘；不参与 ADAPT 写门禁。  
**缺失行为：** 字段缺省或为空对象/数组 → **不阻断** Draft / 审批 / 执行；SRA 不得仅因缺这两字段 REJECT（与 GIP 双字段可执行判定兼容）。

### 1.4 增量字段表（相对 v0.1 §2.3）

| 字段 | 类型 | 必填 | 来源 | 可变性 | 版本 | 说明 |
|---|---|---|---|---|---|---|
| `objective_snapshot.derivation_trace` | object | **N** | OFG | **F** | 否* | 权重如何从模板+偏置链得出；结构对齐 CBA §2.5 |
| `objective_snapshot.derivation_trace.base_template_id` | string | N | OFG | F | 否 | 理论序关系模板 |
| `objective_snapshot.derivation_trace.order_relation` | string[] | N | OFG | F | 否 | 六指标有序列表 |
| `objective_snapshot.derivation_trace.decay_r` | number | N | OFG | F | 否 | 衰减系数（Proposed，默认见 Genome/CBA） |
| `objective_snapshot.derivation_trace.bias_chain` | object[] | N | OFG | F | 否 | 按序应用的 lifecycle/campaign/inventory 等偏置 |
| `objective_snapshot.derivation_trace.renormalized` | bool | N | OFG | F | 否 | 是否已重归一化 |
| `objective_snapshot.derivation_trace.theory_anchors` | string[] | N | OFG | F | 否 | GA-1 锚点（§7.2/§7.3/§7.4/§8.2 等） |
| `objective_snapshot.applied_overlays` | object[] | **N** | OFG | **F** | 否* | 偏置叠加记录 `{type, direction, magnitude}` |

\* 版本比较语义：与 `weights` 一并参与「目标快照是否等价」判定；单独缺失不触发 supersede。

**与 explanation 的关系：** `explanation` 仍为人类可读必填（若 OFG 产出）；`derivation_trace` 为机器可读结构化追踪。二者并存，不互相替代。

---

## 2. 继承声明（未变更部分 = v0.1）

以下章节在 v0.2 **不重写**，效力等同原文：

| v0.1 章节 | 内容 | v0.2 状态 |
|---|---|---|
| §1 定位与硬不变式 | DPK-I1…I8 | **继承**（I1 可执行公式仍指 GIP v0.2 §1.1） |
| §2.2 顶层字段 | decision_id…superseded_by | **继承** |
| §2.3（除 objective_snapshot 增补外） | state_digest / forecast_ref / knowledge_refs… | **继承** |
| §2.4–2.7 | 假设动作、门禁、回填槽 | **继承** |
| §3 状态机 | Draft…Superseded | **继承** |
| §4–5 | O-H-A-R-R 与 Risk/Trust/SRA | **继承** |
| §7 shadow_decision | 与 standard 差异 | **继承** |
| §8 端到端样例 | JSON 语义 | **继承**；样例可选补丁见 §3.2 |
| §9 JSON Schema 主体 | Draft 2020-12 | **继承**；仅 bump `$id` 与 `objective_snapshot` properties |

---

## 3. 与 CBA_OFG / GIP v0.2 / JD v0.2 对齐

### 3.1 对齐矩阵

| 来源 | 主张 | DPK v0.2 处理 |
|---|---|---|
| **CBA_OFG §2.4/§5.1** | `derivation_trace` / `applied_overlays` 为 ObjectiveSnapshot 字段 | **收录**（optional，§1.3/§1.4） |
| **CBA_OFG CO-Q03** | 「建议 DPK v0.2 增补；当前可序列化入 explanation」 | **v0.2 正式回应：增补；解释与结构并存**；CO-Q03 实现侧可标 Closed-by-proposal（仍待负责人确认 Schema 文稿） |
| **CBA_OFG §5.2** | CBA 原样拷贝 ObjectiveSnapshot；此后 F 冻结 | **继承**；新增字段同 F |
| **CBA OFG-I6** | weights 冻结；Executed 不可原地覆盖 | **扩展适用**至 derivation_trace / applied_overlays |
| **GIP v0.2 §1.1 / §7.2** | 可执行 = lifecycle_status ∧ review_result ∧ 非 Shadow 写 ∧ hard_block 空 | **不依赖**新增字段；新增字段不改变可执行公式 |
| **GIP §7.2** | `objective_snapshot` 必填（整体对象） | 对象仍必填；**子字段** derivation_trace/applied_overlays 可选 |
| **JD v0.2 §4.8** | DecisionPackage 透传 `objective_snapshot`；Adapter 不解释权重 | **继承**；Adapter 对新增子字段**只透传不解释** |
| **JD v0.2 §10.1** | v0.1→v0.2 字段迁移表 | 见本文 §4；与 JD 迁移表兼容 |
| **Architecture v0.2 §6** | 最小契约字段 | **不扩最小契约**；仅扩 `objective_snapshot` 内部 optional 子字段 |

### 3.2 样例补丁（不重写全文）

v0.1 §8 样例 A/B 的 `objective_snapshot` 可在 Fixture 迁移时追加（示意，**Proposed**）：

```json
"objective_snapshot": {
  "template_id": "T-MHB-SEED",
  "weights": { "...": "同 v0.1" },
  "lifecycle_bias": "lifecycle_grow",
  "explanation": "中高客单×种草×成长放量：触达与点击优先，ROI 权重低",
  "valid_until": "2026-09-12T00:00:00+08:00",
  "applied_overlays": [
    { "type": "lifecycle", "direction": "grow", "magnitude": 0.20 }
  ],
  "derivation_trace": {
    "base_template_id": "T-MHB-SEED",
    "order_relation": ["ctr", "clicks", "add_cart", "impressions", "cpc", "gmv_roi"],
    "decay_r": 0.75,
    "bias_chain": [
      { "layer": "lifecycle", "name": "grow", "multipliers": { "ctr": 1.15, "clicks": 1.10 } }
    ],
    "renormalized": true,
    "theory_anchors": ["GA-1§7.2", "GA-1§7.4", "GA-1§8.2"]
  }
}
```

未补丁的旧样例在 v0.2 下**仍合法**。

---

## 4. 迁移：v0.1 → v0.2 字段说明

### 4.1 兼容策略

| 策略项 | 规则 |
|---|---|
| 向后兼容 | 缺少 `derivation_trace` / `applied_overlays` 的 v0.1 包 **直接通过** v0.2 校验 |
| 向前兼容 | v0.1 校验器遇到未知子字段：建议 `additionalProperties` 对 `objective_snapshot` 宽松为 true，或忽略未知键（存储层） |
| 版本号 | 新产包建议 `schema_version: "0.2.0"`；历史包保留 `0.1.0`，**不强制改写** |
| 已 Executed 包 | **禁止**为“补齐字段”原地写入（DPK-I7）；审计侧可外挂 OFG 原始快照 |
| Supersede | 不因新增 optional 字段触发 supersede |

### 4.2 字段迁移表

| 路径 | v0.1 | v0.2 | 动作 |
|---|---|---|---|
| `schema_version` | `0.1.0` | `0.2.0`（新包） | 建议 bump |
| `objective_snapshot.template_id` … `valid_until` | 已有 | 不变 | 无 |
| `objective_snapshot.derivation_trace` | （无；或挤在 explanation） | **新增 optional** | OFG 产出则拷贝 |
| `objective_snapshot.applied_overlays` | （无） | **新增 optional** | 同上 |
| `status` / `review.review_result` | 双字段 | 不变 | 无 |
| JSON Schema `$id` | `.../decision_packet/0.1.0` | `.../decision_packet/0.2.0` | 更新 `$id` 与 objective_snapshot properties |
| 门禁可执行公式 | GIP v0.2 | 不变 | 无 |

### 4.3 Fixture / 校验器清单

1. JSON Schema：`$id` → `0.2.0`；`objective_snapshot.properties` 增加两字段（均不在 required）。  
2. 契约测试：保留「无新字段仍 valid」用例 + 「有新字段仍 valid」用例。  
3. OFG 单测：产出含 derivation_trace 的 snapshot → CBA 拷贝 → Packet 冻结后改 snapshot 应失败。  
4. SRA：CHK_GOAL 不因缺新字段 fail；有新字段时可用于增强解释（非阻断）。  
5. JD Adapter：透传；G-01… 不检查这两字段。

### 4.4 JSON Schema 增量（仅 objective_snapshot 段）

```json
"objective_snapshot": {
  "type": "object",
  "required": ["template_id", "weights"],
  "properties": {
    "template_id": {"type": "string"},
    "weights": {
      "type": "object",
      "additionalProperties": {"type": "number", "minimum": 0, "maximum": 1}
    },
    "lifecycle_bias": {"type": "string"},
    "explanation": {"type": "string"},
    "valid_until": {"type": ["string", "null"], "format": "date-time"},
    "applied_overlays": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "type": {"type": "string"},
          "direction": {"type": "string"},
          "magnitude": {"type": "number"}
        }
      }
    },
    "derivation_trace": {
      "type": "object",
      "properties": {
        "base_template_id": {"type": "string"},
        "order_relation": {"type": "array", "items": {"type": "string"}},
        "decay_r": {"type": "number"},
        "bias_chain": {"type": "array", "items": {"type": "object"}},
        "renormalized": {"type": "boolean"},
        "theory_anchors": {"type": "array", "items": {"type": "string"}}
      }
    }
  }
}
```

---

## 5. 待决问题更新

| ID | 问题 | v0.2 处理 | 阻塞 |
|---|---|---|---|
| ~~CO-Q03~~ | derivation_trace 是否进入 DPK 正式字段？ | **本文件提案关闭（Proposed optional）**；待负责人确认 Schema 文稿状态 | 否（确认前 OFG 可双写 explanation） |
| DPK-Q08 | 与 JD status 双向映射 | **已由 JD v0.2 关闭**（双字段） | 否 |
| DPK-V02-Q01 | `applied_overlays.magnitude` 语义（绝对/相对）是否冻结？ | 建议与 CBA/Genome 偏置表一致；实现前对齐 | 否 |
| DPK-V02-Q02 | derivation_trace 是否进入 CausalRecord / 审计外链？ | 默认仅 Packet 内；ME 外链后置 | 否 |
| DPK-V02-Q03 | 多租户下 OFG 模板覆盖是否写入 derivation_trace？ | 否；对齐 CO-Q10 治理 | 否 |

---

## 6. 明确非声称

1. 本文不授权真实广告 API / 只读连接 / LIVE 写路径。  
2. 新增字段与默认值（如 `decay_r`）均为 **Proposed**，非 GA-1 理论结论，待标定与 GA-3。  
3. 本文**不构成**已确认 GA-DEC；`Decision_Packet_Schema` 正式升格仍须负责人确认。  
4. 未变更语义以 v0.1 正文为准。

---

## 7. 变更记录

| 日期 | 版本 | 变更 | 依据 |
|---|---|---|---|
| 2026-09-15 | v0.2 | 增量：裁决 derivation_trace / applied_overlays 为 optional Proposed；变更说明；CBA/GIP/JD 对齐；v0.1→v0.2 迁移；JSON Schema 增量 | GA2-T39；CBA_OFG §2.4/§5/CO-Q03；GIP v0.2；JD v0.2；DPK v0.1 |

---

**Document Status:** Draft  
**Next Review:** 项目负责人 / Research Architect  
**Explicit Non-claim:** 增量 Schema 草案；非 Confirmed 契约；不改门禁可执行公式；不改 GA-1 / PROJECT_SPEC。
