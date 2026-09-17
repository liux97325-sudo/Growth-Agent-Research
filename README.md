# Growth Agent Research Project（GARP）

## 1. 项目介绍

Growth Agent Research Project（GARP）是一个长期维护的企业成长型 AI 研究仓库，用于统一管理 Growth Agent 的理论研究、工程规划与实验验证资料。本仓库当前已由 GA-1 理论阶段转入 GA-2 工程设计阶段（依据 GA-DEC-003）；GA-3 实验验证与论文正文写作仍禁止启动。

本项目的最高治理规范为 [PROJECT_SPEC.md](PROJECT_SPEC.md)。`Research/` 是研究内容的唯一真相源（Single Source of Truth，SSOT）；[GA-1_Theory_v1.0.md](Research/GA-1/GA-1_Theory_v1.0.md) 是所有 GA-1 相关工作的最高理论依据。

## 2. 研究目标

项目最终目标是构建一套完整的企业成长型 AI（Growth Agent）理论、工程设计及实验验证体系，并确保理论、工程和验证之间可追踪、可复现、可持续迭代。

## 3. 项目结构

```text
Growth-Agent-Research/
├── README.md
├── PROJECT_SPEC.md
├── LICENSE
├── CHANGELOG.md
├── ROADMAP.md
├── Research/
│   ├── GA-1/                  # 理论唯一真相源
│   ├── GA-2/                  # 工程阶段占位
│   └── GA-3/                  # 验证阶段占位
├── Meeting/                  # 会议与决策记录
├── Paper/                    # 由 Research 同步生成的论文占位
├── Figures/
│   ├── Mermaid/              # Mermaid 图源文件
│   └── SVG/                  # 后续导出的 SVG
├── Appendix/                 # 缩略语与符号
└── Templates/                # 标准模板
```

## 4. 开发路线

```text
GA-1 Theory → GA-2 Engineering → GA-3 Validation → Future Versions
```

阶段转换必须满足 [ROADMAP.md](ROADMAP.md) 的完成标准，并在 `Meeting/Decision_Log.md` 中记录批准决定。

## 5. 三个阶段

### 5.1 GA-1：Theory

统一概念、研究问题、相关工作、理论结构与创新点；所有内容维护在 `Research/GA-1/`。GA-1 相关工作只能从理论基线单向派生，不得反向修改理论。

### 5.2 GA-2：Engineering

将经确认的理论转化为工程方案。当前状态 Active（GA-DEC-003）；第一轮聚焦总体架构与理论追踪。

### 5.3 GA-3：Validation

设计并执行实验验证。当前禁止启动，仅保留入口与待办占位。

## 6. 如何维护

1. 先阅读 `PROJECT_SPEC.md` 与最新 `Decision_Log.md`。
2. GA-1 工作先读取 `Research/GA-1/GA-1_Theory_v1.0.md`；只允许对其内容进行格式化、保真扩写、图表化和论文结构化。
3. 使用 `Templates/` 中的模板新增会议、创新或实验记录。
4. 同步更新 `CHANGELOG.md`、相关交叉引用和版本号。
5. Mermaid 图源保存在 `Figures/Mermaid/`，导出物保存到 `Figures/SVG/`。
6. 提交前检查术语、编号、链接、UTF-8 编码与阶段边界。

## 7. 如何新增研究内容

1. 在 `Research_Questions.md` 登记研究问题。
2. 在会议日志中记录讨论过程。
3. 重大选择写入 `Decision_Log.md`。
4. 新创新点使用 `Innovation_Template.md`，编号为 `GA-INNOV-NNN`。
5. 更新派生术语材料时，以 `GA-1_Theory_v1.0.md` 为准；冲突时修改派生材料，不修改理论基线。
6. 研究内容确认后，才允许同步至 `Paper/`。

## 8. 版本规范

阶段版本格式为 `GA-MAJOR.MINOR`，例如 `GA-1.0`、`GA-1.1`、`GA-2.0`。阶段切换提升 `MAJOR`，阶段内兼容性迭代提升 `MINOR`。理论文档文件版本采用 `vMAJOR.MINOR`。每次版本变化必须更新 `CHANGELOG.md`。

## 9. 未来规划

- 保持 GA-1 理论基线稳定，禁止反向修改。
- 在 GA-2 Conditional 下完成契约收敛、Fixture 与可重放证据。
- 负责人确认后推进 GA-2 Release Candidate 与 GA-3 解锁评审。
- 建立可复现实验、证据和版本化成果发布流程。

## 10. 许可证 / License

本仓库采用 **Creative Commons BY-NC-SA 4.0**（署名—非商业性使用—相同方式共享）。

- 允许署名后的分享与演绎；
- **禁止商业用途**（商用须另行书面授权）；
- 衍生作品须以相同协议共享。

完整文本见 [LICENSE](LICENSE) 与 <https://creativecommons.org/licenses/by-nc-sa/4.0/>。

当前阶段表述：**GA-2 Conditional — Design Baseline Not Yet Releasable**（详见 `Research/GA-2/GA-2_Release_Manifest_v0.1.md`）。
