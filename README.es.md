<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/brand/imagination-octo-brainstorming-logo-dark.png" />
  <img src="assets/brand/imagination-octo-brainstorming-logo.png" alt="IMAGINATION OCTO BRAINSTORMING — Haz que una se sostenga" width="380" />
</picture>

# IMAGINATION OCTO BRAINSTORMING

**MAKE ONE HOLD**

### La mitad convergente de Imagination Octo —<br/>una dirección elegida, puesta a prueba hasta ser un concepto que puedes llevar a planificación

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português (Brasil)](README.pt-BR.md)

[![Tests](https://img.shields.io/github/actions/workflow/status/djfksjd/imagination-octo-brainstorming/tests.yml?style=flat-square&label=tests)](https://github.com/djfksjd/imagination-octo-brainstorming/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/license-MIT-1f2937?style=flat-square)](LICENSE)
![Version](https://img.shields.io/badge/version-0.4.3-d69526?style=flat-square)
[![Family](https://img.shields.io/badge/part%20of-Imagination%20Octo-6d5ef5?style=flat-square)](https://github.com/djfksjd/imagination-octo)
![Hosts](https://img.shields.io/badge/hosts-Claude%20Code%20%C2%B7%20Codex-0ea5b7?style=flat-square)

</div>

Imagination Octo Brainstorming empieza después de elegir una dirección. Pone a prueba esa única idea frente a su objetivo, sus restricciones, su alternativa convencional más fuerte, la operación diaria y su propio modo de fallo, y devuelve un memo de concepto breve. Si la dirección rompe el brief o pierde frente a algo más simple, lo dice en lugar de pulirla.

> [!TIP]
> **A la mayoría le conviene instalar [Imagination Octo](https://github.com/djfksjd/imagination-octo).** Genera direcciones con el motor, espera tu elección y pasa esa elección a este taller.

**Esto es `v0.4.3`, una versión que solo cambia el nombre del runtime evaluado como v0.4.2.** Las mediciones de abajo provienen de una única comparación pequeña juzgada por IA y no afirman que todo concepto mejore. La invocación implícita sigue desactivada: llama a la skill por su nombre.

## Qué hace

| | |
|---|---|
| **Revisión previa de restricciones** | ¿Vuelve un mecanismo excluido con otro nombre, responsable, lugar o escala? |
| **Supuesto de carga** | ¿Qué única creencia haría caer la idea si fuera falsa? |
| **Competidor convencional** | ¿Por qué merece su complejidad añadida frente a la respuesta corriente? |
| **Mecanismo central** | ¿Qué causa observable cambia el resultado? |
| **La mitad aburrida** | ¿Quién se ocupa del trabajo recurrente, las colas, las excepciones y el mantenimiento? |
| **Fallo propio** | ¿Cómo falla el mecanismo que define la idea, en sus propios términos? |
| **Falsador** | ¿Qué resultado debería hacer que el equipo pare o cambie de dirección? |

## Cómo funciona

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

- La revisión previa es proporcionada. Una infracción pequeña recibe la reparación más pequeña, que queda como provisional, no una reescritura de la idea.
- No se implementa nada. El resultado es un memo de concepto, no código, andamiaje ni un plan de implementación.
- En tiempo de ejecución solo se carga un archivo Markdown: sin marcos repartidos, contratos de prohibición, archivos JSON auxiliares ni compuertas de calidad.

## Pruébalo

```text
Usa $imagination-octo-brainstorming para desarrollar esta dirección elegida. Muestra
el primer uso real, la carga operativa recurrente, el modo de fallo propio,
el falsador y la próxima decisión que debemos tomar.
```

La respuesta es un memo de concepto que termina en la próxima decisión y ahí se detiene.

## Mediciones

v0.4.2 frente a un prompt normal fuerte, prerregistrado y a ciegas: 10 briefs nuevos en inglés y coreano con una dirección ya elegida, 5 ejecuciones cada uno, 5 jueces (2026-07-30).

| Métrica | Taller menos prompt normal |
|---|---:|
| Preferido para planificar | **45–5 (90%)** |
| Accionabilidad | **+1,37** |
| Ajuste a la decisión | **+0,95** |
| Robustez | **+0,82** |
| Claridad causal | **+0,71** |
| Tokens | `1,14×` |

Léelas con honestidad:

- **Un solo modelo generó y juzgó.** Solo `gpt-5.4`, con jueces de la misma familia. El intervalo de Wilson al 95% para la preferencia es 78,6–95,7%, así que el límite inferior no demuestra una tasa del 90%.
- **Puede perder.** Nueve briefs fueron para el taller por unanimidad y uno fue para el prompt normal por unanimidad.
- **No se ha medido con Claude ni con personas.** Los experimentos entre modelos del repositorio de Octo ([A](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-a.md), [B](https://github.com/djfksjd/imagination-octo/blob/main/evals/results/2026-10-06-experiment-b.md)) solo probaron el motor. Nada de esto dice cómo se comporta el taller con otros modelos.
- **Un diseño anterior fue reemplazado.** El flujo de mazos y compuertas (v0.3.0), con marcos repartidos, contratos de prohibición y compuertas de calidad mecánicas, se conserva en [`legacy/v0.3.0/`](legacy/v0.3.0/) como registro y nunca se carga.

Protocolo, regla de decisión y resultados congelados: [`evals/`](evals/README.md).

## Cuándo usarlo y cuándo no

**Úsalo** cuando ya existe una dirección, una favorita de la lista corta o un concepto en bruto y necesitas saber si se sostiene antes de planificar.

**Usa otra cosa** para las primeras ideas o para implementar. Para las primeras ideas usa [Imagination Octo Engine](https://github.com/djfksjd/imagination-octo-engine). El taller se detiene a propósito antes de la implementación.

## Antes se llamaba `imagination-brainstorming`

Hasta la v0.4.2 este repositorio era `imagination-brainstorming-skill` y la skill era `$imagination-brainstorming`. GitHub redirige la URL antigua, pero el plugin, el id del marketplace y el comando cambiaron: instala `imagination-octo-brainstorming@imagination-octo-brainstorming` e invoca `$imagination-octo-brainstorming`. Por lo demás, las instrucciones del runtime no han cambiado.

## Instalación independiente

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-octo-brainstorming/main/install.sh | bash
```

Para actualizar, ejecuta el mismo comando otra vez. Si avisa de copias antiguas de estas skills instaladas por separado, termina el comando con `| bash -s -- --clean-legacy` para apartarlas; no se borra nada.

```bash
# Claude Code
claude plugin marketplace add djfksjd/imagination-octo-brainstorming
claude plugin install imagination-octo-brainstorming@imagination-octo-brainstorming

# Codex
codex plugin marketplace add djfksjd/imagination-octo-brainstorming
codex plugin add imagination-octo-brainstorming@imagination-octo-brainstorming
```

## Desarrollo

```bash
python3 -m pytest tests/ -q
python3 evals/harness.py --help
bash -n install.sh
```

## Licencia

[MIT](LICENSE).
