<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/brand/imagination-octo-brainstorming-logo-dark.png" />
  <img src="assets/brand/imagination-octo-brainstorming-logo.png" alt="IMAGINATION OCTO BRAINSTORMING — ひとつを確かなものに" width="380" />
</picture>

# IMAGINATION OCTO BRAINSTORMING

**MAKE ONE HOLD**

### Imagination Octo の収束フェーズ —<br/>選んだ方向ひとつを負荷テストし、企画に持ち込めるコンセプトにする

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português (Brasil)](README.pt-BR.md)

[![Tests](https://img.shields.io/github/actions/workflow/status/djfksjd/imagination-octo-brainstorming/tests.yml?style=flat-square&label=tests)](https://github.com/djfksjd/imagination-octo-brainstorming/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-MIT-1f2937?style=flat-square)](LICENSE)
![Version](https://img.shields.io/badge/version-0.4.3-d69526?style=flat-square)
[![Family](https://img.shields.io/badge/part%20of-Imagination%20Octo-6d5ef5?style=flat-square)](https://github.com/djfksjd/imagination-octo)
![Hosts](https://img.shields.io/badge/hosts-Claude%20Code%20%C2%B7%20Codex-0ea5b7?style=flat-square)

</div>

Imagination Octo Brainstorming は、方向を選んだ後に始まります。そのひとつのアイデアを、目的、制約、最も強い平凡な代替案、日々の運用、そしてそれ固有の失敗の仕方に照らして検証し、短いコンセプトメモを返します。選んだ方向がブリーフに反する場合や、より単純な案に負ける場合は、磨き上げる代わりにそう伝えます。

> [!TIP]
> **ほとんどの方には [Imagination Octo](https://github.com/djfksjd/imagination-octo) のインストールをおすすめします。** エンジンで方向を生成し、あなたの選択を待ってから、その選択をこのワークショップに渡します。

**現在は `v0.4.3` で、v0.4.2 として評価したランタイムの名前だけを変えたリリースです。** 以下の測定値は AI が審査した小規模な比較 1 回によるもので、すべてのコンセプトが良くなるという主張ではありません。暗黙の呼び出しは無効のままなので、スキル名で呼び出してください。

## できること

| | |
|---|---|
| **制約の事前点検** | 除外したメカニズムが、別の名前・担い手・場所・規模で戻ってきていないか？ |
| **要となる仮定** | 誤りならアイデア全体が崩れる、ただひとつの前提は何か？ |
| **平凡な競合案** | 平凡な答えより複雑になる分の価値はどこにあるか？ |
| **中核メカニズム** | どの観察可能な原因が結果を変えるのか？ |
| **地味な半分** | 繰り返しの作業、待ち行列、例外、保守は誰が担うのか？ |
| **固有の失敗** | このアイデアを定義するメカニズムは、それ自体としてどう失敗するか？ |
| **反証条件** | どんな結果が出たら、止めるか方向を変えるべきか？ |

## 仕組み

```text
 your chosen direction ──► ┌─────────────── constraint preflight ───────────────┐
                           │ is an excluded mechanism back under another name?  │
                           └──────────────────────────┬─────────────────────────┘
                                                      ▼
                           ┌────────────────── pressure test ───────────────────┐
                           │ load-bearing assumption · conventional competitor  │
                           │      boring half · native failure · falsifier      │
                           └──────────────────────────┬─────────────────────────┘
                                                      ▼
                                         decision-ready concept memo
                                                      ▼
                                           ◆ YOUR NEXT DECISION ◆        nothing is implemented
```

- 事前点検は問題の大きさに合わせます。小さな違反には最小の修正を暫定的に添えるだけで、アイデアを書き直しません。
- 実装は行いません。出力はコンセプトメモであり、コード、スキャフォールディング、実装計画ではありません。
- 実行時に読み込むのは Markdown ファイル 1 つだけです。配布フレーム、禁止契約、JSON サイドカー、品質ゲートはありません。

## 使ってみる

```text
$imagination-octo-brainstorming を使って、この選んだ方向を発展させて。
最初の実際の利用場面、繰り返し発生する運用負荷、固有の失敗の仕方、反証条件、
そして次に下すべき判断を示して。
```

応答は次の判断で終わるコンセプトメモで、そこで止まります。

## 測定結果

v0.4.2 を強い通常プロンプトと比べた、事前登録のブラインド比較です。方向が選択済みの新しい英語・韓国語ブリーフ 10 件、各 5 回実行、審査 5 名（2026-07-30）。

| 指標 | ワークショップ − 通常プロンプト |
|---|---:|
| 企画に持ち込みたい側 | **45–5 (90%)** |
| 実行可能性 | **+1.37** |
| 判断への適合 | **+0.95** |
| 堅牢性 | **+0.82** |
| 因果の明確さ | **+0.71** |
| トークン | `1.14×` |

正直に読むために:

- **生成も審査もひとつのモデルでした。** `gpt-5.4` のみで、審査も同じ系列です。選好の 95% Wilson 区間は 78.6–95.7% で、下限は 90% という率を裏づけていません。
- **負けることがあります。** 9 件のブリーフは全員一致でワークショップ、1 件は全員一致で通常プロンプトが選ばれました。
- **Claude でも人間でも測定していません。** Octo リポジトリのモデル横断実験（[A](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-a.md)、[B](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-b.md)）が試したのはエンジンだけです。ワークショップがほかのモデルでどう振る舞うかは、ここからは分かりません。
- **以前の設計は置き換えました。** 配布フレーム、禁止契約、機械的な品質ゲートを使うデッキとゲートのワークフロー（v0.3.0）は、記録として [`legacy/v0.3.0/`](legacy/v0.3.0/) に残してあり、実行時には読み込みません。

プロトコル、判定規則、固定された結果: [`evals/`](evals/README.md)。

## 使うとき、使わないとき

**使う場面：** 方向、候補の第一位、または粗いコンセプトがすでにあり、企画に入る前にそれが持ちこたえるかを知りたいとき。

**別のものを使う場面：** 最初のアイデア出しや実装。最初のアイデア出しには [Imagination Octo Engine](https://github.com/djfksjd/imagination-octo-engine) を使ってください。ワークショップは意図的に実装の手前で止まります。

## `imagination-brainstorming` から改名しました

v0.4.2 まで、このリポジトリは `imagination-brainstorming-skill`、スキルは `$imagination-brainstorming` でした。旧 URL は GitHub がリダイレクトしますが、プラグイン名、マーケットプレイス ID、コマンドは変わりました。`imagination-octo-brainstorming@imagination-octo-brainstorming` をインストールし、`$imagination-octo-brainstorming` で呼び出してください。それ以外のランタイムの指示は変わっていません。

## 単独インストール

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-octo-brainstorming/main/install.sh | bash
```

更新するときも同じコマンドを再実行します。以前に個別インストールしたスキルのコピーが報告された場合は、コマンドの末尾を `| bash -s -- --clean-legacy` に変えて実行してください。削除はせず、別の場所へ移します。

```bash
# Claude Code
claude plugin marketplace add djfksjd/imagination-octo-brainstorming
claude plugin install imagination-octo-brainstorming@imagination-octo-brainstorming

# Codex
codex plugin marketplace add djfksjd/imagination-octo-brainstorming
codex plugin add imagination-octo-brainstorming@imagination-octo-brainstorming
```

## 開発

```bash
python3 -m pytest tests/ -q
python3 evals/harness.py --help
bash -n install.sh
```

## ライセンス

[MIT](LICENSE).
