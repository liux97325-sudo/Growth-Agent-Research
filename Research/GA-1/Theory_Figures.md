# GA-1 理论图登记表

## 1. 编号规范

所有图统一使用 `Figure-NNN` 编号。Mermaid 图源保存在 `Figures/Mermaid/`，SVG 导出物保存在 `Figures/SVG/`。编号分配后不得复用。

## 2. 图表索引

| 编号 | 名称 | 类型 | 图源 | SVG | 状态 | 理论来源 |
|---|---|---|---|---|---|---|
| Figure-001 | 项目架构图 | Repository Architecture | `Figures/Mermaid/Figure-001_Project_Architecture.mmd` | 待生成 | Confirmed | 项目初始化规范 |
| Figure-002 | 研究路线图 | Research Roadmap | `Figures/Mermaid/Figure-002_Research_Roadmap.mmd` | 待生成 | Confirmed | `ROADMAP.md` |
| Figure-003 | 目录关系图 | Directory Relationships | `Figures/Mermaid/Figure-003_Directory_Relationships.mmd` | 待生成 | Confirmed | `PROJECT_SPEC.md` |

## 3. 维护要求

- 图中理论关系必须来自已确认的 Research 内容。
- 修改图源时同步更新本索引和 `CHANGELOG.md`。
- 导出 SVG 时保留相同编号与基本文件名。
- 当前三张图仅表达项目治理与目录关系，不表达新增理论。

