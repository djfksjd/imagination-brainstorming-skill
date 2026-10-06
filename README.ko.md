<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/brand/imagination-octo-brainstorming-logo-dark.png" />
  <img src="assets/brand/imagination-octo-brainstorming-logo.png" alt="IMAGINATION OCTO BRAINSTORMING — 하나를 버티게 만든다" width="380" />
</picture>

# IMAGINATION OCTO BRAINSTORMING

**MAKE ONE HOLD**

### Imagination Octo의 수렴 단계 —<br/>고른 방향 하나를 압박 검증해서 기획에 가져갈 수 있는 컨셉으로

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português (Brasil)](README.pt-BR.md)

[![Tests](https://img.shields.io/github/actions/workflow/status/djfksjd/imagination-octo-brainstorming/tests.yml?style=flat-square&label=tests)](https://github.com/djfksjd/imagination-octo-brainstorming/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-MIT-1f2937?style=flat-square)](LICENSE)
![Version](https://img.shields.io/badge/version-0.4.3-d69526?style=flat-square)
[![Family](https://img.shields.io/badge/part%20of-Imagination%20Octo-6d5ef5?style=flat-square)](https://github.com/djfksjd/imagination-octo)
![Hosts](https://img.shields.io/badge/hosts-Claude%20Code%20%C2%B7%20Codex-0ea5b7?style=flat-square)

</div>

Imagination Octo Brainstorming은 방향을 고른 뒤에 시작합니다. 그 아이디어 하나를 목표, 제약, 가장 강한 평범한 대안, 일상 운영, 그리고 자기 고유의 실패 방식에 비추어 검증하고 짧은 컨셉 메모를 돌려줍니다. 고른 방향이 브리프를 어기거나 더 단순한 대안에 진다면, 다듬는 대신 그렇다고 말합니다.

> [!TIP]
> **대부분의 사용자에게는 [Imagination Octo](https://github.com/djfksjd/imagination-octo) 설치를 권합니다.** 엔진으로 방향을 만들고, 사용자의 선택을 기다린 뒤, 그 선택을 이 워크숍으로 넘깁니다.

**현재 `v0.4.3`이며, v0.4.2로 평가한 런타임의 이름만 바꾼 릴리스입니다.** 아래 측정값은 AI가 심사한 소규모 비교 한 번에서 나왔고, 모든 컨셉이 나아진다는 주장이 아닙니다. 자동 호출은 꺼져 있으니 스킬 이름으로 직접 호출하세요.

## 하는 일

| | |
|---|---|
| **제약 사전 점검** | 배제한 메커니즘이 다른 이름, 주체, 장소, 규모로 되돌아오고 있지 않은가? |
| **핵심 가정** | 틀리면 아이디어 전체가 무너지는 믿음 하나는 무엇인가? |
| **평범한 경쟁자** | 평범한 답보다 복잡해지는 값을 왜 치를 만한가? |
| **핵심 메커니즘** | 어떤 관찰 가능한 원인이 결과를 바꾸는가? |
| **지루한 절반** | 반복 업무, 대기열, 예외, 유지보수는 누가 맡는가? |
| **고유한 실패** | 이 아이디어를 정의하는 메커니즘은 그 자체로 어떻게 실패하는가? |
| **반증 조건** | 어떤 결과가 나오면 멈추거나 방향을 바꿔야 하는가? |

## 작동 방식

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

- 사전 점검은 문제의 크기에 맞춥니다. 작은 위반에는 가장 작은 수정을 잠정적으로 붙일 뿐, 아이디어를 새로 쓰지 않습니다.
- 구현은 하지 않습니다. 결과물은 컨셉 메모이지 코드, 스캐폴딩, 구현 계획이 아닙니다.
- 실행 시 불러오는 것은 Markdown 파일 하나뿐입니다. 배분된 프레임, 금지 계약, JSON 사이드카, 품질 게이트가 없습니다.

## 사용해 보기

```text
$imagination-octo-brainstorming을 사용해서 이 선택한 방향을 발전시켜 줘.
첫 실제 사용 장면, 반복되는 운영 부담, 고유한 실패 방식, 반증 조건,
그리고 우리가 내려야 할 다음 결정을 보여 줘.
```

응답은 다음 결정으로 끝나는 컨셉 메모이고, 거기서 멈춥니다.

## 측정 결과

v0.4.2를 강한 일반 프롬프트와 비교한 사전 등록 블라인드 결과입니다. 방향이 이미 선택된 새 영어·한국어 브리프 10개, 각 5회 실행, 심사자 5명 (2026-07-30).

| 지표 | 워크숍 − 일반 프롬프트 |
|---|---:|
| 기획에 가져가고 싶은 쪽 | **45–5 (90%)** |
| 실행 가능성 | **+1.37** |
| 결정 적합성 | **+0.95** |
| 견고성 | **+0.82** |
| 인과 명료성 | **+0.71** |
| 토큰 | `1.14×` |

정직하게 읽는 법:

- **생성도 심사도 모델 하나였습니다.** `gpt-5.4`뿐이고 심사자도 같은 계열입니다. 선호도의 95% Wilson 구간은 78.6–95.7%라서, 하한만으로는 90% 비율이 입증되지 않습니다.
- **질 수 있습니다.** 브리프 9개는 만장일치로 워크숍이, 1개는 만장일치로 일반 프롬프트가 선택됐습니다.
- **Claude에서도, 사람에게도 측정하지 않았습니다.** Octo 저장소의 교차 모델 실험([A](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-a.md), [B](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-b.md))은 엔진만 시험했습니다. 워크숍이 다른 모델에서 어떻게 동작하는지는 여기서 알 수 없습니다.
- **이전 설계는 교체됐습니다.** 배분된 프레임, 금지 계약, 기계적 품질 게이트를 쓰던 덱·게이트 워크플로(v0.3.0)는 기록으로 [`legacy/v0.3.0/`](legacy/v0.3.0/)에 남겨 두었고 실행 시에는 불러오지 않습니다.

프로토콜, 판정 규칙, 고정된 결과 파일: [`evals/`](evals/README.md).

## 쓸 때와 쓰지 않을 때

**쓰세요:** 방향, 후보 중 1순위, 또는 거친 컨셉이 이미 있고, 기획에 들어가기 전에 그것이 버티는지 알아야 할 때.

**다른 것을 쓰세요:** 첫 아이디어를 낼 때나 구현할 때. 첫 아이디어에는 [Imagination Octo Engine](https://github.com/djfksjd/imagination-octo-engine)을 쓰세요. 워크숍은 의도적으로 구현 앞에서 멈춥니다.

## `imagination-brainstorming`에서 이름이 바뀌었습니다

v0.4.2까지 이 저장소는 `imagination-brainstorming-skill`, 스킬은 `$imagination-brainstorming`이었습니다. 예전 URL은 GitHub가 리다이렉트하지만 플러그인 이름, 마켓플레이스 ID, 명령은 바뀌었습니다. `imagination-octo-brainstorming@imagination-octo-brainstorming`을 설치하고 `$imagination-octo-brainstorming`으로 호출하세요. 그 밖의 런타임 지시문은 그대로입니다.

## 단독 설치

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-octo-brainstorming/main/install.sh | bash
```

업데이트할 때도 같은 명령을 다시 실행하면 됩니다. 예전에 따로 설치한 스킬 복사본이 있다고 나오면 명령 끝을 `| bash -s -- --clean-legacy`로 바꿔 실행하세요. 삭제하지 않고 옮겨 둡니다.

```bash
# Claude Code
claude plugin marketplace add djfksjd/imagination-octo-brainstorming
claude plugin install imagination-octo-brainstorming@imagination-octo-brainstorming

# Codex
codex plugin marketplace add djfksjd/imagination-octo-brainstorming
codex plugin add imagination-octo-brainstorming@imagination-octo-brainstorming
```

## 개발

```bash
python3 -m pytest tests/ -q
python3 evals/harness.py --help
bash -n install.sh
```

## 라이선스

[MIT](LICENSE).
