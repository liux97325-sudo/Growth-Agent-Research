# GARP Fixture Shadow Skeleton（GA2-T31）

> 状态：Draft / Skeleton only。对应 `Research/GA-2/Module_Skeleton_Design_v0.1.md`。  
> **不接真实广告 API、不写凭证、不开启 LIVE 写。** 全部阈值与默认值 **Proposed**。

## 1. 定位

落地可运行的影子（Shadow / Fixture）代码骨架：

- 契约类型与枚举（`lifecycle_status` + `review_result` 双字段）
- `DecisionPacket` dataclass + `is_writable` 门禁伪实现
- `RuntimeEnvelope` + Boot 自检（SC-A/B/C 子集）
- `FixtureTransport` stub + `LiveTransport` Fail-Closed
- 最小单测：NO_ACTION 成包 / Shadow 写拒绝 / source_env 过滤

## 2. 目录树（摘要）

```text
garp/
├── README.md
├── configs/
│   ├── default.json              # 默认 FIXTURE + MODE_SHADOW_DECIDE（Proposed）
│   └── envelopes/
│       └── fixture_shadow.json
├── packages/
│   ├── garp_contracts/           # 纯类型/枚举；零 I/O
│   │   ├── enums.py              # LifecycleStatus / ReviewResult / SourceEnv(+HUMAN) / ...
│   │   ├── packet.py             # DecisionPacket + is_writable
│   │   ├── envelope.py           # RuntimeEnvelope / SelfcheckRecord
│   │   └── adapter.py            # AbstractActionRequest / ActionReceipt / ReceiptAudit
│   ├── garp_edge/
│   │   └── adapter/
│   │       ├── write_gate.py     # G-01 子集 + SHADOW_WRITE_FORBIDDEN
│   │       ├── fixture_transport.py
│   │       └── live_stub.py      # Fail-Closed
│   ├── garp_gate/
│   │   ├── self_review/agent.py  # SRA 伪实现（唯一写 review_result）
│   │   └── trust/filter.py       # source_env / trust_credit_allowed 过滤
│   └── garp_runtime/
│       ├── bootstrap/bootstrapper.py
│       └── selfcheck/boot_selfcheck.py
├── apps/cli/selfcheck.py         # 可运行 boot 自检
└── tests/unit/test_skeleton_gates.py
```

## 3. 如何运行

依赖：**Python 3.10+ 标准库 only**（无 pytest / 无第三方包）。

在 `garp/` 目录下：

```bash
# 1) 最小单测
python -m unittest discover -s tests/unit -v

# 2) Boot 自检（JSON 报告）
python apps/cli/selfcheck.py
# 或指定配置
python apps/cli/selfcheck.py --config configs/default.json
```

期望：

- 单测全部 `ok`
- 自检 `status=PASS`，`live_transport_state=FAIL_CLOSED_STUB`

## 4. 硬约束（代码层）

| 约束 | 实现锚点 |
|---|---|
| 默认 env=FIXTURE / SHADOW_DECIDE | `configs/default.json`；`bootstrap_envelope` 强制非 LIVE 不可信任计分、强制 dry_run |
| LiveTransport Fail-Closed | `LiveTransportStub` 任意 read/write 抛错；Boot SC-B1 |
| 双字段语义 | `DecisionPacket.status`（lifecycle）+ `review.review_result`（审批） |
| packet_kind | `standard` / `shadow_decision`；shadow ⇔ SHADOW_READ_ONLY（RE-I8） |
| source_env | `{LIVE, SHADOW, SIMULATION, FIXTURE, HUMAN}`（GA-DEC-006）；`REAL→LIVE` 归一 |
| 阈值 Proposed | `configs/default.json` → `thresholds.*` 注释 |
| 无真实凭证 | CredentialProvider=EmptyProvider（SC-A5） |

## 5. 明确不做

- 业务算法（FE/RE/OFG/Trust 公式）
- 真实京东/抖音 SDK、OAuth、可执行投放
- 数据库 / MQ / Web 框架绑定
- 修改 GA-1 / PROJECT_SPEC / Architecture 语义

## 6. 文档锚点

- `Research/GA-2/Module_Skeleton_Design_v0.1.md`
- `Research/GA-2/Decision_Packet_Schema_v0.1.md`
- `Research/GA-2/Runtime_Envelope_Selfcheck_v0.1.md`
- `Research/Gate_Integration_Playbook_v0.2.md`（见 `Research/GA-2/Gate_Integration_Playbook_v0.2.md`）
- `Meeting/Decision_Log.md` GA-DEC-004 / 005 / 006
