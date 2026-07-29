<div align="center">

# ◇ Imagination Brainstorming

**選んだアイデアを、現実に耐えるコンセプトへ。**

[![Tests](https://github.com/djfksjd/imagination-brainstorming-skill/actions/workflows/tests.yml/badge.svg)](https://github.com/djfksjd/imagination-brainstorming-skill/actions/workflows/tests.yml)
![Version](https://img.shields.io/badge/version-0.4.2-db2777)
![Preference](https://img.shields.io/badge/blind_preference-90.0%25-16a34a)
![License](https://img.shields.io/badge/license-MIT-0f766e)

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português (Brasil)](README.pt-BR.md)

</div>

---

> [!TIP]
> 通常は統合版 [Imagination](https://github.com/djfksjd/imagination) を
> 推奨します。案の生成、ユーザー選択、本ワークショップを一つにつなぎます。

Imagination Brainstorming は **方向性を選んだ後** に始まります。実装前に
目標、制約、最強の代替案、通常運用、固有の失敗に照らして案を検証します。

```text
選択済みの案 → 制約チェック → 圧力テスト → 意思決定可能なコンセプト
```

## 使用例

```text
$imagination-brainstorming を使ってこの案を発展させ、最初の利用場面、
継続運用、固有の失敗、反証条件、次の判断を示して。
```

## 実測結果

| 指標 | 強い通常プロンプトとの差 |
|---|---:|
| 計画に持ち込みたい結果 | **45–5 (90.0%)** |
| 実行可能性 | **+1.37** |
| 意思決定への適合性 | **+0.95** |
| 因果的明瞭さ | **+0.71** |
| 頑健性 | **+0.82** |

事前登録したブラインド比較のモデル審査結果であり、普遍的な優位を保証する
ものではありません。

## 単独インストール

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-brainstorming-skill/main/install.sh | bash
```

初期のアイデア生成には
[Imagination Engine](https://github.com/djfksjd/imagination-engine-skill)
を使用してください。旧ワークフローは `legacy/v0.3.0/` にのみ保存され、
実行時には読み込まれません。MIT License.
