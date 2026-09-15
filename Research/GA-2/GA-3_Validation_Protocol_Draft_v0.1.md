# GA-2：GA-3 验证协议草案（不启动实验）

**文档编号：** GA-2-VALP-001  
**任务编号：** GA2-T29  
**版本：** v0.1  
**状态：** Draft（**协议草案**；不构成 GA-3 启动批准）  
**阶段：** GA-2 Engineering Design（派生材料）  
**输入基线：** `Research/GA-1/GA-1_Theory_v1.0.md`（GA-1.0 / v1.0，Confirmed）  
**主线架构：** `Architecture_Overview_v0.2.md`（Confirmed，GA-DEC-004）  
**工程基线：** `GA-2.0_Baseline_Package.md`（Confirmed，GA-DEC-005）  
**授权依据：** GA-DEC-005（Accepted；允许工程设计与无写方案；**不启动 GA-3、不授权真实只读连接、不授权真实写**）  
**权威引用（本文强制对齐，不重复实现）：**  
- `Research/GA-1/Research_Questions.md` — GA-RQ-011…018  
- `GA-1_Theory_v1.0.md` §16 — 验证入口十问  
- `Shadow_Trial_Run_Plan_v0.1.md` — 无写试运行、SM-M*、升权阶梯  
- `Precalibration_Experiment_Design_v0.1.md` — PE-M*、泄漏防护、伦理边界  
- `JD_Adapter_Interface_v0.2.md` — 只读/写契约、RO-* 清单、G-01–G-09  
- `Runtime_Envelope_Selfcheck_v0.1.md` — SC-A–E、RE-I*、防污染  
- `Gate_Integration_Playbook_v0.2.md` — 双字段门禁  
- `Theory_Engineering_Trace.md` — 理论→工程追踪  

**作者角色：** Research Engineer 子代理（工程派生；**不新增理论主张、不修改 GA-1 / PROJECT_SPEC**）  
**约束：** 本文仅为 **GA-3 验证协议草案**。**不执行任何 GA-3 实验**；**不创建真实凭证**；**不调用真实 API**；**不假设 GA2-T25 只读连接已授权**；一切样本量、阈值、门槛、窗口均为 **Proposed**，禁止当作已验证真值。

---

## 0. 安全边界与范围声明（强制阅读）

### 0.1 本轮明确不做

| 项 | 说明 |
|---|---|
| 启动 GA-3 实验 | 不跑任何实验臂、不产生实验结果、不更新 GA-3 状态机 |
| 解锁 GA-3 | `Research/GA-3/Validation_TODO.md` 仍为 Locked；进入 GA-3 须**新 GA-DEC** |
| 真实广告写操作 | 不调用任何改价/改预算/建计划接口 |
| 真实凭证与密钥 | 不创建、不示例、不落盘任何 AppKey / Token / Secret |
| 真实只读连接 | 不假设 GA2-T25 已授权；主证据路径默认 Fixture / 历史导出 |
| 修改 GA-1 / PROJECT_SPEC | 纯工程派生 |
| 把 Proposed 参数升 Confirmed | 协议通过评审也不自动升格阈值 |

### 0.2 本轮明确要做

1. 将理论 §16 十问与 GA-RQ-011…018 **映射为可证伪验证问题**（VQ）。  
2. 给出对照设计：规则基线 / 人工运营基线 / 无反思消融。  
3. 定义指标族：预测精度、ROI/无效花费、计划成功率、知识沉淀、Trust 成长、人工成本。  
4. 定义数据与伦理边界（对齐 PE-E* / SM 风险）。  
5. 定义**阶段门禁**：进入 GA-3 与进入各实验波次均须新决策。  
6. 给出产出物模板（验证计划预注册表、结果报告骨架、决策建议）。

### 0.3 一句话定位

> **本协议不是实验报告，而是「若负责人批准 GA-3，我们如何可复现地回答 §16」的预注册契约。**  
> 它锁定问题、对照、指标、熔断与伦理，防止事后挑指标、挑样本、挑结论。

---

## 1. 验证问题映射（Theory §16 ↔ GA-RQ ↔ VQ）

> 原则：每条 GA-RQ 至少对应 1 条可证伪 VQ；VQ 必须写清**对照**、**主指标**、**反例条件**。  
> §16 原文十问中「提升 ROI」「降低无效花费」在 GA-RQ-012 合并；本文 VQ-012a/VQ-012b 保持可分项报告。

### 1.1 映射总表

| Theory §16 | GA-RQ | 验证问题 ID | 可证伪表述（草案） | 回路锚点 | 首要证据阶段（Proposed） |
|---|---|---|---|---|---|
| §16.1 预测准确率 | GA-RQ-011 | **VQ-011** | 在预注册评估窗内，FE 的 within_band / MAPE 优于「朴素基线」（上一日同窗、滚动均值、季节 naive） | 回路 A / FE | P1 影子 + P2 只读对照 |
| §16.2 ROI | GA-RQ-012 | **VQ-012a** | 在可比槽位上，Agent 建议/执行路径相对对照臂提高 trusted ROI（非平台虚高 ROI） | 回路 A / BDV | P2–P3（需更严因果） |
| §16.3 无效花费 | GA-RQ-012 | **VQ-012b** | 相对对照臂，降低「事后判定为无效/失控」花费占比 | 回路 A / Risk | P2–P3 |
| §16.4 人工运营成本 | GA-RQ-013 | **VQ-013** | 在等质量约束下，单位可判定决策所需人工分钟数 / 干预次数下降 | 回路 D / 自治路径 | P2–P4 |
| §16.5 计划成功率 | GA-RQ-014 | **VQ-014** | 预注册「计划成功」定义下，Agent 臂成功率不低于对照且关键失败更少 | 回路 A / Genome | P2–P3 |
| §16.6 反思持续改进 | GA-RQ-015 | **VQ-015** | 开启 Reflection→Learning 的完整回路 B，相对**无反思消融**，跨期关键指标单调改善或恶化率更低 | 回路 B | P3（需消融） |
| §16.7 可复用经营知识 | GA-RQ-016 | **VQ-016** | 知识对象（Rule/Strategy/Genome 候选）在跨计划/跨周期 holdout 上可迁移，且可追溯到 Decision Packet 链 | 回路 C | P3–P4 |
| §16.8 优于传统规则系统 | GA-RQ-017 | **VQ-017a** | 在预注册主指标与护栏上，Growth Agent 臂优于冻结规则基线 | 回路 A–D | P2–P3 |
| §16.9 优于普通人工运营 | GA-RQ-017 | **VQ-017b** | 在同等信息与同等风险约束下，不劣于或优于人工运营基线（非劣性优先） | 回路 A–D | P2–P4 |
| §16.10 长期商业价值 | GA-RQ-018 | **VQ-018** | 在多周期窗口上，知识复利 + 成本下降的净价值为正，且未以硬红线/合规事件为代价 | 回路 C+D | P4 终局评估 |

### 1.2 与理论的边界说明

1. 本映射**不修改** §16 原文，也不收窄理论主命题；只把入口问题工程化。  
2. GA-RQ-001…010（机制类）不在本协议主验证清单，但作为**解释性证据**出现在讨论：例如 VQ-015 失败时，回看是否因 BDV 噪声、样本不足或回路 B 未闭环。  
3. GA-RQ-010「数字员工终态」仍属终局命题，本协议只提供支撑证据，不宣称已验证。

---

## 2. 对照与实验臂设计

> 预注册原则（继承 PE §3.0）：每波实验前固定假设、主指标、臂、槽位、最小样本、熔断。  
> **一次主对比只动一类差异**；多臂组合效应标 `EXPLORE`。

### 2.1 三类强制对照

| 对照 ID | 名称 | 定义 | 用途 | 实现约束 |
|---|---|---|---|---|
| **ARM-RULE** | 规则基线 | 冻结的专家规则/阈值包（当前 Expert_Prior + 现网常见规则），无学习回写 | VQ-017a 主对照 | 参数快照冻结；禁止边跑边改 |
| **ARM-HUMAN** | 人工运营基线 | 历史人工操作轨迹，或预注册并行窗口内的人工决策记录 | VQ-017b / VQ-013 | 必须预注册窗口语义；标注 concurrent_action |
| **ARM-GA** | Growth Agent 全回路 | Architecture v0.2 四回路：决策 + 蒸馏 + 知识候选 + Trust 代理 | 多 VQ 主臂 | Shadow 下不升 live Trust |

### 2.2 消融臂（至少一个必做）

| 消融 ID | 名称 | 关掉什么 | 回答什么 |
|---|---|---|---|
| **ARM-NO-REF** | 无反思消融 | 回路 B：Reflection→Learning→经验候选→Knowledge 反哺 | VQ-015：改进是否来自反思，而非仅数据变多 |
| **ARM-NO-KE**（可选） | 无知识反哺 | 回路 C 输出不进 Reasoning | VQ-016：知识是否真驱动决策 |
| **ARM-READ-ONLY-NO-GATE**（诊断，非主结论） | 仅预测不门禁 | Risk/Trust/SRA 对动作的约束 | 解释误拒/漏拦；**不得**作升权证据 |

### 2.3 波次阶梯（P0–P4，全部 Proposed）

```text
P0  协议评审 + 预注册冻结（本文 → Under Review → Confirmed 由负责人）
P1  无写影子验证（对齐 Shadow_Trial_Run_Plan；主证据 VQ-011 + 门禁可审计）
      数据：SRC-FIXTURE → SRC-EXPORT
P2  只读对照验证（若 GA2-T25 获授权：SRC-LIVE-RO；否则继续 SRC-EXPORT）
      主证据：VQ-011/014/017a/017b（非劣性）+ 人工成本观察
P3  消融与知识可迁移验证（ARM-NO-REF；跨计划 holdout）
      主证据：VQ-015/016/017
P4  终局商业价值评估（多周期；成本-收益-风险联合）
      主证据：VQ-012/013/018
```

**硬规则：**

1. 每一波进入前，须新的 **GA-DEC**（见 §6）。  
2. P1 不得声称已回答 VQ-012/018。  
3. 反事实不可识别时，只报告代理指标与区间，禁止点估计因果宣称（SM-R02）。  
4. LIVE 写路径（若有）永远不在本协议默认范围内；须独立决策。

### 2.4 槽位与分层（继承 TCAL / Genome）

- 主槽位：`price_band × plan_purpose × life_cycle_stage`（2×2×5）。  
- 报告单元必须披露 `n_eff`；`n_eff` 不足则继承父层或标 `sample_size_low`（禁止编造段内终值）。  
- 活动窗 / 平台异常窗单独分层，不进常态主结论（TCAL §3.3 / PE-L05）。

---

## 3. 指标体系

> 不重复实现 SM-M* / PE-M* 全文；本表定义 **GA-3 消费方式与主/护栏角色**。  
> 全部门槛为 **Proposed**，首次 E0 数据盘点后由负责人修订。

### 3.1 指标族总图

| 族 | 名称 | 定义（验证语义） | 对齐 | 关联 VQ | 角色 |
|---|---|---|---|---|---|
| **M-PRED** | 预测命中率 | 事后落入预注册分位带比例（分 horizon） | SM-M03 / PE-M03 / FE within_band | 011 | 主 |
| **M-PRED** | 预测 MAPE / 分位误差 | 分 horizon 误差；低置信 vs 高置信分层 | SM-M04 / PE-M04 | 011 | 主+护栏 |
| **M-ROI** | trusted ROI 差 | Agent 臂 − 对照臂（经 BDV 的可信口径） | JD BDV；禁用平台虚高 | 012a | 主 |
| **M-WASTE** | 无效花费占比 | 事后无效/失控花费 / 总花费 | Risk 后验代理 | 012b | 主 |
| **M-PLAN** | 计划成功率 | 预注册成功判据达成比例 | Genome / 场景目标 | 014 | 主 |
| **M-PLAN** | 关键失败率 | 硬红线、超损、异常归因事件率 | Risk R4 / 合规 | 014 | 护栏（否决级） |
| **M-REFLECT** | 跨期改进斜率 | 回路 B 开 vs 关的指标斜率差 | LE / RFE | 015 | 主 |
| **M-REFLECT** | 失败复盘闭合率 | Failure Pattern → 可追溯结论的闭合比例 | ME/LE | 015 | 辅 |
| **M-KNOW** | 知识对象可迁移增益 | 候选 Rule/Strategy/Genome 在 holdout 的增益 vs 冻结 Prior | KE 状态机 | 016 | 主 |
| **M-KNOW** | 可追溯完整率 | 知识对象 → 经验 → Decision Packet 链完整比例 | DPK / KE | 016 | 护栏 |
| **M-TRUST** | 代理 Trust 轨迹合理性 | shadow_trust_proxy 与人工否决/硬红线事件的一致性（仅影子域） | SM §8.3 | 013/017/018 | 观察；**禁止映射 live T2/T8** |
| **M-TRUST** | live Trust 误计分 | 任一非 LIVE 样本计入 live Trust 的次数 | SM-M10 / P-02 | 全体 | 硬门槛 = 0 |
| **M-HUMAN** | 单位决策人工分钟 | 人工处理分钟 / 可判定决策数 | 运营日志 | 013 | 主 |
| **M-HUMAN** | 干预次数比 | 人工改写/否决次数 / 建议数 | override 率 | 013/017b | 主 |
| **M-GATE** | 门禁通过/误拒/误放 | APPROVE 率、应拦未拦、应放未放代理 | SM-M06/07 / PE-M11/13 | 017 | 主+护栏 |
| **M-ISO** | 隔离完整率 | 零 live 污染事件 | SM-M10 / PE-M10 | 全体 | **硬门槛 = 1.0** |

### 3.2 Proposed 门槛草案（可修订）

| 指标 | Proposed 门槛 | 说明 |
|---|---|---|
| M-PRED within_band（24h） | ≥ 0.60 | 对齐 SM 升权材料 |
| M-PLAN 成功率 | 相对 ARM-RULE 非劣：差值 ≥ −5pp（95% CI 下界） | 首期优先非劣性 |
| M-PLAN 关键失败率 | 不高于对照；R4 语义违反 = 0 | 否决级 |
| M-REFLECT | ARM-GA 跨期斜率 > ARM-NO-REF；且恶化周占比更低 | 方向稳定 |
| M-KNOW 可迁移增益 | holdout 上正增益且 CI 不跨 0；否则 Inconclusive | 禁止只报点估计 |
| M-HUMAN 人工分钟 | 相对 ARM-HUMAN 下降 ≥ 15% **且** 质量护栏不劣 | 同时看质量 |
| M-GATE 硬红线仍 APPROVE | = 0 | 否决级 |
| M-ISO / live Trust 误计分 | 1.0 / 0 | 否决级 |
| 可判定样本（比率类） | n ≥ 50；覆盖 ≥3 最小任务 | 对齐 SM/PE 占位 |
| 分位/幅度类 | 槽位 n_eff ≥ 30 | 否则继承 Prior |
| 预测回看 | 每 horizon n ≥ 30 条 ForecastEvalRecord | 不足只报方向 |

### 3.3 解读纪律

1. **NO_ACTION 率**升高不自动 = 更好或失能；必须与正确率（SM-M02/PE-M02）联合解读。  
2. 主指标漂亮但护栏失败 → 整包 **Not-Usable**。  
3. CI 跨无效应或跨 Prior 边界 → **Inconclusive**；输出「维持 Prior / 扩样本」，不输出新终值。  
4. 多重比较：预注册主指标；探索网格标 `EXPLORE`。  
5. 影子/仿真证据 **不得**写成 live 已验证。

---

## 4. 数据与伦理边界

### 4.1 数据源阶梯（对齐 Shadow 三档 + PE 数据源）

| 档 | 代码 | GA-3 可用性 | 硬约束 |
|---|---|---|---|
| Fixture | SRC-FIXTURE | P1 可用 | 不得证明 live 最优；env=FIXTURE |
| 历史导出 | SRC-EXPORT | P1–P2 默认主证据 | 脱敏；BDV 对齐；不含写接口 |
| Shadow 池 | SRC-SHADOW | 消融/辅证 | 不进 live Trust、不与 live 主集合并分位 |
| 授权后只读 | SRC-LIVE-RO | **仅当 GA2-T25 授权后** | dry_run 恒 true；写路径硬失败 |
| Live 写 | SRC-LIVE-W | **本协议范围外** | 须独立 GA-DEC + Trust + 人工否决 |

### 4.2 纳入 / 排除（继承 TCAL §3.3 + Trial §4.4）

- `origin_env != LIVE` 默认不进 live 主集。  
- BDV `blocking_for_decision=true`：排除出主集；关键决策 0 次使用 FAIL 数据。  
- 活动爆发窗 / 平台异常窗：单独分层。  
- 任何排除必须写入 `excluded_summary`；禁止静默丢样本。

### 4.3 泄漏防护（强制 E0）

继承 PE-L01…L08：未来标签、全局统计、同实体跨集、环境池、活动窗、多重比较、只报成功、事后标签。  
**PE-L01 / PE-L04 任一失败 → 实验熔断。**

### 4.4 伦理 / 合规边界（继承 PE-E* 并扩展到验证）

| ID | 边界 | GA-3 要求 |
|---|---|---|
| VA-E01 | 不触碰真实投放 | 默认无写；若有写波次须独立决策 |
| VA-E02 | 不伪造企业真值 | SIM/Fixture 必标 `origin_env` |
| VA-E03 | 不把影子当 live 证据 | Shadow/SIM 不进 live Trust、不晋升 Rule/Genome |
| VA-E04 | 数据最小化与脱敏 | 企业明细不进研究仓库默认树 |
| VA-E05 | 可审计可复现 | 预注册 + 参数快照 + 切分 + 排除计数 |
| VA-E06 | 人工否决保留 | 产物不得表述为「已授权自动执行」 |
| VA-E07 | 理论优先 | 与 GA-1 冲突 → 改工程或否决，不改理论 |
| VA-E08 | 租户隔离 | 默认租户内；不合并跨租户数值 |
| VA-E09 | 对照公平 | 人工基线须披露信息不对称与激励差异 |
| VA-E10 | 停止权 | 负责人可随时 Abort；熔断触发不得以「样本还差一点」续跑 |

---

## 5. 统计原则（全部 Proposed）

| 原则 | 内容 |
|---|---|
| S1 | 主估计稳健分位/加权中位数；避免活动与大额订单绑架 |
| S2 | 必须报 CI / 分位带；跨无效效应 → Inconclusive |
| S3 | 同 plan/product 重复样本用聚类稳健 SE 或降权 |
| S4 | 时间序列：T-Holdout / T-Blocked 主协议；禁止 i.i.d. 随机切分做主结论 |
| S5 | 因果宣称门槛：无随机化或可信自然实验时，只作关联/代理；报告必须降级措辞 |
| S6 | 功效分析后置，但任何「优于」提案必须披露 n_eff、CI、切分、偏离预注册项 |

**Proposed 时间切分：** train/valid/test = 60/20/20 或「常态 + ≥1 完整大促」事件边界；具体以 E0 盘点为准。

---

## 6. 阶段门禁（进入 GA-3 与进入各波次）

### 6.1 总门禁：GA-3 解锁

```text
当前：GA-3 = Locked（Validation_TODO.md）
进入 GA-3 的必要条件（须同时满足）：
  1) 工程基线与跨文档一致性可接受（建议完成 GA2-T27）
  2) Shadow 试运行（T26）达到可评审门槛或明确豁免理由并记录
  3) 参数 Proposed 状态与预标定策略明确（不要求已标定）
  4) 数据路径明确：至少 SRC-EXPORT 脱敏方案获批；SRC-LIVE-RO 另议
  5) 本协议经负责人评审（Under Review → Confirmed）
  6) 新增 GA-DEC-NNN：明确批准「启动 GA-3 验证」及范围/资源/负责人
```

**在第 6 项决策落地前，任何实验执行均视为越权。**

### 6.2 波次门禁（P1–P4）

| 从 → 到 | 必要条件（Proposed） | 须记录 |
|---|---|---|
| P0 → P1 | 协议 Confirmed；Fixture/导出就绪；SC-A–E 可绿 | GA-DEC 启动 P1 |
| P1 → P2 | SM-M10=1.0；M-PRED 达标或可解释；n 达标；**若需 SRC-LIVE-RO 则 GA2-T25 已授权** | GA-DEC 启动 P2 |
| P2 → P3 | 主对照结论可解释；泄漏审计通过；消融环境隔离就绪 | GA-DEC 启动 P3 |
| P3 → P4 | VQ-015/016 至少 Inconclusive 以上且无护栏否决；多周期数据就绪 | GA-DEC 启动 P4 |
| 任一波次熔断 | M-ISO<1.0、live Trust 误计分>0、硬红线仍 APPROVE、负责人 Abort | 停止；修复；重审 |

### 6.3 与 Trust / 权限的关系

- GA-3 证据 **默认不**提升 live Trust Level。  
- 若未来要以验证结果支持升权，必须单独写「升权证据包」，并满足：LIVE 样本规则、人工否决保留、独立 GA-DEC。  
- `shadow_trust_proxy` 仅影子域，禁止映射生产权限（SM §8.3）。

---

## 7. 产出物模板

### 7.1 验证计划预注册表（每波次一份）

```markdown
# GA-3 验证计划预注册（模板）

- prereg_id: GA3-PR-{wave}-{yyyymmdd}-{seq}
- wave: P1 | P2 | P3 | P4
- linked_protocol: GA-2-VALP-001 v0.1
- authorizing_decision: GA-DEC-____ （启动本波次）
- runtime_envelope_root: { env, mode, dry_run: true }
- status: PREREGISTERED | ACTIVE | FROZEN | CLOSED
- explicit_non_claim: 未授权真实写；未修改 GA-1；阈值均为 Proposed

## 1. 假设与 VQ
- VQs covered: [VQ-…]
- 可证伪表述：
- 反例条件（何种结果算证伪）：

## 2. 臂与槽位
- arms[]: ARM-RULE / ARM-HUMAN / ARM-GA / ARM-NO-REF / …
- segments[]: price_band × plan_purpose × life_cycle_stage 子集
- 只动一类差异的说明：

## 3. 指标
- primary_metrics[]
- guardrail_metrics[]
- Proposed 门槛与 n_min
- NO_ACTION 联合解读说明

## 4. 数据
- source_type, origin_env 比例
- train/valid/test 或事件窗定义
- excluded_summary 规则
- LeakageAudit 绑定

## 5. 熔断
- 对应 SM-M10 / PE-S* / Trial TR-S* / 本文 §6.2

## 6. 偏离记录区（运行中填写）
- 时间、偏离项、原因、是否仍纳入主结论
```

### 7.2 结果报告模板

```markdown
# GA-3 验证结果报告（模板）

- report_id: GA3-RPT-{wave}-{yyyymmdd}-{seq}
- prereg_refs: [GA3-PR-…]
- authorizing_decision: GA-DEC-____
- status: DRAFT_RESULT | UNDER_REVIEW | CLOSED
- explicit_non_claim: 一切数值为研究估计；非 Confirmed live 真值

## 1. 范围与预注册对照
- 实际执行 vs 预注册差异表（必须披露）

## 2. 数据与审计
- 槽位覆盖矩阵（n_eff）
- excluded_summary
- LeakageAuditReport 摘要
- M-ISO / live Trust 误计分

## 3. 主结果
### 3.x VQ-…
- 臂对比表（点估计 + CI）
- 主指标 / 护栏
- 判定：Supported | Not-Supported | Inconclusive

## 4. 消融与机制解释
- ARM-NO-REF 等
- 与回路 B/C 的对应

## 5. 人工成本与对照公平性
- M-HUMAN
- 信息不对称披露

## 6. 风险、局限、伦理核查
- 反事实不可识别、选择偏差、Fixture≠真实 等

## 7. 建议决策
- Accept / Narrow / Reject / Defer
- 是否触发升权证据包（须另文 + 新 GA-DEC）
- 是否修订 Proposed 阈值（仍 PROPOSED）

## 8. 附件
- 参数快照、切分索引、审计日志摘要
```

### 7.3 报告验收检查

| 检查 | 通过条件 |
|---|---|
| V-01 | 有 authorizing_decision；无未授权波次 |
| V-02 | 无 live 写痕迹；dry_run/env 声明完整 |
| V-03 | 偏离预注册已披露 |
| V-04 | 所有「优于/非劣」结论带 n_eff 与 CI |
| V-05 | 护栏结果完整；否决级失败未被淡化 |
| V-06 | 未把 shadow 证据写成 live 终值 |
| V-07 | GA-1 / PROJECT_SPEC 未被修改 |
| V-08 | 未决槽位未被编造段内估计 |

---

## 8. 待决问题

| ID | 问题 | 建议 | 阻塞 |
|---|---|---|---|
| VA-Q1 | ARM-HUMAN 用历史轨迹还是并行窗口？ | 首期历史轨迹 + 明确局限；并行窗口后置 | P2 对照质量 |
| VA-Q2 | 「计划成功」统一判据是什么？ | 分 plan_mode 预注册（种草/收割不同） | VQ-014 |
| VA-Q3 | 人工成本如何计量才可审计？ | 运营日志时间戳 + 抽样校准；禁止自我报告单源 | VQ-013 |
| VA-Q4 | 是否允许 P2 无 SRC-LIVE-RO？ | 允许，但结论措辞必须降级为「历史分布上的证据」 | VQ-012/018 强度 |
| VA-Q5 | 多租户是否进入 GA-3？ | 默认单租户；跨租户只共享方法不合并数值 | 治理 |
| VA-Q6 | VQ-018 的时间跨度？ | 至少覆盖多个投放周期 + 预算周期；具体 E0 后定 | P4 |
| VA-Q7 | 是否需要独立安全/合规评审签字？ | 若引入 SRC-LIVE-RO 或任何写：必须 | P2+ |

---

## 9. 与既有文档的接口

| 文档 | 本文关系 |
|---|---|
| Theory §16 / Research_Questions | 映射来源；不改写理论问题 |
| Shadow_Trial_Run_Plan | P1 执行契约；SM-M*、升权阶梯、三档数据 |
| Precalibration_Experiment_Design | 泄漏防护、统计原则、伦理边界、报告纪律 |
| JD_Adapter_Interface v0.2 | 只读能力面与写门禁；VQ 数据对象 |
| Runtime_Envelope_Selfcheck | 启动自检与防污染硬门槛 |
| Gate_Integration_Playbook v0.2 | 门禁行为指标语义 |
| GA2-T25 ReadOnly Assessment | P2 的 SRC-LIVE-RO 前提；本文不代替其授权 |
| Validation_TODO（GA-3） | 保持 Locked；解锁须新 GA-DEC |

---

## 10. 变更记录

| 日期 | 版本 | 变更 | 依据 |
|---|---|---|---|
| 2026-09-14 | v0.1 | 首次建立 GA-3 验证协议草案：§16/RQ 映射、对照与消融、指标族、数据伦理、阶段门禁、产出物模板 | GA2-T29；GA-1 §16；Research_Questions；Shadow Trial；Precalibration；GA-DEC-005 |

---

**Document Status:** Draft  
**Next Review:** Project Owner / Research Architect  
**Explicit Non-claim:** 本文**不启动** GA-3；**不授权**真实只读连接或真实写；**未修改** GA-1 与 PROJECT_SPEC；所有样本量、阈值、门槛均为 **Proposed**。进入 GA-3 须新 `GA-DEC-NNN`。
