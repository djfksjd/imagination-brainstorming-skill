<div align="center">

# ◇ Imagination Brainstorming

**把已选创意变成经得住现实检验的概念。**

[![Tests](https://github.com/djfksjd/imagination-brainstorming-skill/actions/workflows/tests.yml/badge.svg)](https://github.com/djfksjd/imagination-brainstorming-skill/actions/workflows/tests.yml)
![Version](https://img.shields.io/badge/version-0.4.2-db2777)
![Preference](https://img.shields.io/badge/blind_preference-90.0%25-16a34a)
![License](https://img.shields.io/badge/license-MIT-0f766e)

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português (Brasil)](README.pt-BR.md)

</div>

---

> [!TIP]
> 大多数用户建议安装整合版
> [Imagination](https://github.com/djfksjd/imagination)，依次完成发散、用户
> 选择与概念深化。

Imagination Brainstorming 在 **方向已经选定后** 开始。它会在实现前检查
目标、约束、最强替代方案、日常运营和该机制特有的失败方式。

```text
已选方向 → 约束预检 → 压力测试 → 可决策概念
```

## 使用示例

```text
使用 $imagination-brainstorming 深化这个方向，说明首次真实使用、持续运营、
特有失败、证伪条件和下一项决策。
```

## 实测结果

| 指标 | 相对强普通提示词 |
|---|---:|
| 带入规划的偏好 | **45–5（90.0%）** |
| 可执行性 | **+1.37** |
| 决策契合度 | **+0.95** |
| 因果清晰度 | **+0.71** |
| 稳健性 | **+0.82** |

这是预注册盲测中的模型评审结果，并不保证普遍占优。

## 单独安装

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-brainstorming-skill/main/install.sh | bash
```

初始创意发散请使用
[Imagination Engine](https://github.com/djfksjd/imagination-engine-skill)。
旧流程仅保存在 `legacy/v0.3.0/`，运行时不会加载。MIT License.
